<template>
    <div class="admin-shops">
        <!-- Shop list sidebar -->
        <div class="shops-list-panel">
            <div class="panel-header">
                <h2 class="font-semibold text-base">{{ $t('menu.admin.shops') }}</h2>
                <Button icon="pi pi-plus" size="small" @click="createNewShop" v-tooltip="$t('admin.shop.create')" />
            </div>
            <div class="shops-list">
                <div v-for="shop in shops" :key="shop.id" class="shop-list-item"
                    :class="{ selected: selectedShop?.id === shop.id }"
                    @click="selectShop(shop)">
                    <span class="pi pi-shop text-sm opacity-60"></span>
                    <span class="flex-1 truncate text-sm">{{ shop.name }}</span>
                </div>
                <div v-if="shops.length === 0 && !loading" class="text-slate-400 text-sm text-center py-4">
                    {{ $t('message.empty_list') }}
                </div>
                <template v-if="loading">
                    <div v-for="i in 3" :key="i" class="p-2">
                        <Skeleton height="2rem" />
                    </div>
                </template>
            </div>
        </div>

        <!-- Shop detail panel -->
        <div class="shop-detail-panel" v-if="selectedShop">
            <div class="panel-header">
                <h2 class="font-semibold text-base truncate">{{ selectedShop.id === -1 ? $t('admin.shop.create') : selectedShop.name }}</h2>
                <Button v-if="selectedShop.id !== -1" icon="pi pi-trash" severity="danger" text size="small"
                    @click="onDeleteShop" v-tooltip="$t('admin.shop.delete')" />
            </div>

            <Tabs v-model:value="activeTab">
                <TabList>
                    <Tab value="details">{{ $t('admin.shop.slot_details') }}</Tab>
                    <Tab value="slots" :disabled="selectedShop.id === -1">{{ $t('admin.shop.slot_planner') }}</Tab>
                </TabList>

                <TabPanels>
                    <!-- Details tab -->
                    <TabPanel value="details">
                        <form @submit.prevent="saveShop" class="flex flex-col gap-4 pt-2">
                            <IftaLabel>
                                <label for="name">{{ $t('admin.shop.name') }}</label>
                                <InputText id="name" v-model="selectedShop.name" fluid />
                            </IftaLabel>
                            <IftaLabel>
                                <label for="description">{{ $t('admin.shop.description') }}</label>
                                <Textarea id="description" v-model="selectedShop.description" fluid rows="3" />
                            </IftaLabel>
                            <div class="flex gap-4 flex-wrap">
                                <IftaLabel class="flex-1">
                                    <label for="location">{{ $t('admin.shop.location') }}</label>
                                    <InputText id="location" v-model="selectedShop.location" fluid />
                                </IftaLabel>
                                <IftaLabel class="flex-1">
                                    <label for="maps">{{ $t('admin.shop.maps') }}</label>
                                    <InputText id="maps" v-model="selectedShop.maps_link" fluid />
                                </IftaLabel>
                            </div>
                            <div class="flex gap-4 flex-wrap">
                                <div class="flex-1">
                                    <p class="text-sm text-slate-500 mb-1">{{ $t('admin.shop.start_date') }}</p>
                                    <DatePicker v-model="startDate" inline date-format="yy-mm-dd" />
                                </div>
                                <div class="flex-1">
                                    <p class="text-sm text-slate-500 mb-1">{{ $t('admin.shop.end_date') }}</p>
                                    <DatePicker v-model="endDate" inline date-format="yy-mm-dd" />
                                </div>
                            </div>
                            <div class="flex justify-end">
                                <Button :label="$t('message.save')" icon="pi pi-save" type="submit" />
                            </div>
                        </form>
                    </TabPanel>

                    <!-- Slot planner tab -->
                    <TabPanel value="slots">
                        <SlotPlanner :slots="slots" :shopId="selectedShop.id"
                            @create="onSlotCreate" @update="onSlotUpdate" @delete="onSlotDelete"
                            @batch="onSlotBatch" />
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </div>

        <div class="shop-detail-panel flex items-center justify-center text-slate-400" v-else>
            <div class="text-center">
                <span class="pi pi-shop text-4xl block mb-2 opacity-30"></span>
                <p>{{ $t('message.shops.select') }}</p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Shop, ShopWithOpenRange, TimeSlot, SlotOp } from '@/api/types';
import { shopApi, slotsApi } from '@/main';
import { exampleShop } from '@/api/types';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import IftaLabel from 'primevue/iftalabel';
import Skeleton from 'primevue/skeleton';
import Tabs from 'primevue/tabs';
import Tab from 'primevue/tab';
import TabList from 'primevue/tablist';
import TabPanels from 'primevue/tabpanels';
import TabPanel from 'primevue/tabpanel';
import DatePicker from '@/components/primevue/DatePicker';
import SlotPlanner from '@/components/SlotPlanner.vue';
import { networkDate } from '@/utils';
import { invalidateCache } from '@/api';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';
import handleError from '@/error_handler';

const toast = useToast();
const { t } = useI18n();

const shops = ref<Shop[]>([]);
const selectedShop = ref<ShopWithOpenRange | null>(null);
const slots = ref<TimeSlot[]>([]);
const loading = ref(false);
const activeTab = ref('details');
const startDate = ref<Date | null>(null);
const endDate = ref<Date | null>(null);

async function loadShops() {
    loading.value = true;
    try {
        shops.value = await shopApi.list();
    } catch (e) {
        handleError(toast, t, 'error.shop.unknown')(e);
    } finally {
        loading.value = false;
    }
}

async function selectShop(shop: Shop) {
    loading.value = true;
    try {
        const detail = await shopApi.get(shop.id);
        detail.open_ranges = detail.open_ranges.map(o => ({
            ...o,
            start_time: o.start_time.substring(0, 5),
            end_time: o.end_time.substring(0, 5),
        }));
        selectedShop.value = detail;
        startDate.value = new Date(detail.available_from);
        endDate.value = new Date(detail.available_until);
        activeTab.value = 'details';
        await loadSlots(shop.id);
    } catch (e) {
        handleError(toast, t, 'error.shop.unknown')(e);
    } finally {
        loading.value = false;
    }
}

async function loadSlots(shopId: number) {
    try {
        slots.value = await slotsApi.list(shopId);
    } catch (e) {
        handleError(toast, t, 'error.shop.unknown')(e);
    }
}

function createNewShop() {
    selectedShop.value = { ...exampleShop, open_ranges: [] };
    startDate.value = new Date();
    endDate.value = new Date();
    slots.value = [];
    activeTab.value = 'details';
}

async function saveShop() {
    if (!selectedShop.value) return;
    selectedShop.value.available_from = networkDate(startDate.value!);
    selectedShop.value.available_until = networkDate(endDate.value!);

    try {
        if (selectedShop.value.id === -1) {
            const created = await shopApi.create(selectedShop.value);
            await loadShops();
            await selectShop(created);
            toast.add({ severity: 'success', summary: t('message.success'), detail: t('admin.shop.created'), life: 3000 });
        } else {
            invalidateCache();
            await shopApi.update(selectedShop.value);
            await selectShop(selectedShop.value);
            toast.add({ severity: 'success', summary: t('message.success'), detail: t('admin.shop.updated'), life: 3000 });
        }
    } catch (e) {
        handleError(toast, t)(e);
    }
}

async function onDeleteShop() {
    if (!selectedShop.value || !confirm(t('admin.shop.delete_confirm'))) return;
    try {
        await shopApi.delete(selectedShop.value.id);
        shops.value = shops.value.filter(s => s.id !== selectedShop.value!.id);
        selectedShop.value = null;
        slots.value = [];
        invalidateCache();
        toast.add({ severity: 'success', summary: t('message.success'), detail: t('admin.shop.deleted'), life: 3000 });
    } catch (e) {
        handleError(toast, t)(e);
    }
}

async function onSlotCreate(slot: Partial<TimeSlot>) {
    if (!selectedShop.value) return;
    try {
        await slotsApi.create(selectedShop.value.id, {
            day: slot.day!,
            start_time: slot.start_time!,
            end_time: slot.end_time!,
            max_volunteers: slot.max_volunteers!,
            valid_from: slot.valid_from!,
            valid_until: slot.valid_until!,
        });
        invalidateCache();
        await loadSlots(selectedShop.value.id);
        toast.add({ severity: 'success', summary: t('message.success'), detail: t('admin.shop.slot_created'), life: 3000 });
    } catch (e) {
        handleError(toast, t)(e);
    }
}

async function onSlotUpdate(slot: Partial<TimeSlot>) {
    if (!slot.id) return;
    try {
        await slotsApi.update(slot.id, {
            day: slot.day!,
            start_time: slot.start_time!,
            end_time: slot.end_time!,
            max_volunteers: slot.max_volunteers!,
            valid_from: slot.valid_from!,
            valid_until: slot.valid_until!,
        });
        invalidateCache();
        await loadSlots(selectedShop.value!.id);
        toast.add({ severity: 'success', summary: t('message.success'), detail: t('admin.shop.slot_updated'), life: 3000 });
    } catch (e) {
        handleError(toast, t)(e);
    }
}

async function onSlotBatch(ops: SlotOp[]) {
    if (!selectedShop.value) return;
    try {
        for (const op of ops) {
            if (op.action === 'create') {
                await slotsApi.create(selectedShop.value.id, {
                    day: op.slot.day!,
                    start_time: op.slot.start_time!,
                    end_time: op.slot.end_time!,
                    max_volunteers: op.slot.max_volunteers!,
                    valid_from: op.slot.valid_from!,
                    valid_until: op.slot.valid_until!,
                });
            } else if (op.action === 'update') {
                await slotsApi.update(op.slot.id!, {
                    day: op.slot.day!,
                    start_time: op.slot.start_time!,
                    end_time: op.slot.end_time!,
                    max_volunteers: op.slot.max_volunteers!,
                    valid_from: op.slot.valid_from!,
                    valid_until: op.slot.valid_until!,
                });
            } else if (op.action === 'delete') {
                await slotsApi.delete(op.slot.id!);
            }
        }
        invalidateCache();
        await loadSlots(selectedShop.value.id);
        toast.add({ severity: 'success', summary: t('message.success'), detail: t('admin.shop.slot_updated'), life: 3000 });
    } catch (e) {
        handleError(toast, t)(e);
    }
}

async function onSlotDelete(slotId: number) {
    if (!confirm(t('admin.shop.slot_delete_confirm'))) return;
    try {
        await slotsApi.delete(slotId);
        invalidateCache();
        await loadSlots(selectedShop.value!.id);
        toast.add({ severity: 'success', summary: t('message.success'), detail: t('admin.shop.slot_deleted'), life: 3000 });
    } catch (e) {
        handleError(toast, t)(e);
    }
}

onMounted(loadShops);
</script>

<script lang="ts">
export default { name: 'AdminShopsView' }
</script>

<style scoped>
.admin-shops {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}

.shops-list-panel {
    width: 220px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    border: 1px solid var(--p-content-border-color);
    border-radius: var(--p-border-radius-lg, 8px);
    overflow: hidden;
    max-height: 80vh;
}

.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    background: var(--p-content-background);
    border-bottom: 1px solid var(--p-content-border-color);
}

.shops-list {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.shop-list-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    border-radius: var(--p-border-radius-md, 6px);
    cursor: pointer;
    transition: background 0.1s;
    color: var(--p-text-muted-color);
}

.shop-list-item:hover {
    background: var(--p-navigation-item-focus-background);
    color: var(--p-text-color);
}

.shop-list-item.selected {
    background: var(--p-highlight-background);
    color: var(--p-highlight-color);
    font-weight: 600;
}

.shop-detail-panel {
    flex: 1;
    border: 1px solid var(--p-content-border-color);
    border-radius: var(--p-border-radius-lg, 8px);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.shop-detail-panel :deep(.p-tabs) {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.shop-detail-panel :deep(.p-tabpanels) {
    flex: 1;
    overflow-y: auto;
}
</style>
