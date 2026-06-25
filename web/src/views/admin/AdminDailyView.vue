<script setup lang="ts">
import type { DaySlot, Shop, User } from '@/api/types';
import DatePicker from '@/components/primevue/DatePicker';
import { reservationApi, shopApi, usersApi } from '@/main';
import { networkDate, reformatTime } from '@/utils';
import EnsureLoggedIn from '@/components/EnsureLoggedIn.vue';
import Button from 'primevue/button';
import Select from 'primevue/select';
import Dialog from 'primevue/dialog';
import Tag from 'primevue/tag';
import { computed, defineComponent, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import handleError from '@/error_handler';

const $t = useI18n().t;
const toast = useToast();
const confirm = useConfirm();

const shops = ref<Shop[]>([]);
const users = ref<User[]>([]);
const selectedShop = ref<number | null>(null);
const datePicked = ref<Date>(new Date());

const daySlots = ref<DaySlot[]>([]);
const loading = ref(false);

// Add-person dialog state
const addDialogVisible = ref(false);
const addSlotId = ref<number | null>(null);
const addUserId = ref<number | null>(null);

onMounted(() => {
    shopApi.list().then((response) => {
        shops.value = response;
        if (response.length === 1) selectedShop.value = response[0].id;
    }).catch(handleError(toast, $t, "error.shop.unknown"));

    usersApi.list().then((response) => {
        users.value = response;
    }).catch(handleError(toast, $t, "error.user.unknown"));
});

function load() {
    if (!selectedShop.value || !datePicked.value) {
        daySlots.value = [];
        return;
    }
    loading.value = true;
    reservationApi.getDayBookings(selectedShop.value, networkDate(new Date(datePicked.value)))
        .then((response) => {
            daySlots.value = response;
        })
        .catch(handleError(toast, $t, "error.reservation.unknown"))
        .finally(() => { loading.value = false; });
}

watch([selectedShop, datePicked], load);

const dateLabel = computed(() =>
    datePicked.value
        ? new Date(datePicked.value).toLocaleDateString($t("date_locale"), {
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
        })
        : ""
);

const totalPeople = computed(() =>
    daySlots.value.reduce((sum, s) => sum + s.bookings.length, 0)
);

function openAdd(slotId: number) {
    addSlotId.value = slotId;
    addUserId.value = null;
    addDialogVisible.value = true;
}

function confirmAdd() {
    if (!selectedShop.value || !addSlotId.value || !addUserId.value) return;
    reservationApi.assign(selectedShop.value, {
        time_slot_id: addSlotId.value,
        date: networkDate(new Date(datePicked.value)),
        user_id: addUserId.value,
    }).then(() => {
        toast.add({ severity: 'success', summary: $t("admin.daily.added"), life: 3000 });
        addDialogVisible.value = false;
        load();
    }).catch(handleError(toast, $t, "error.reservation.unknown"));
}

function removeBooking(reservationId: number, name: string) {
    confirm.require({
        message: $t("admin.daily.remove_confirm", { name }),
        header: $t("admin.daily.remove"),
        icon: 'pi pi-exclamation-triangle',
        rejectProps: { label: $t("message.cancel"), severity: 'secondary', outlined: true },
        acceptProps: { label: $t("admin.daily.remove"), severity: 'danger' },
        accept: () => {
            reservationApi.cancel(reservationId).then(() => {
                toast.add({ severity: 'success', summary: $t("admin.daily.removed"), life: 3000 });
                load();
            }).catch(handleError(toast, $t, "error.reservation.unknown"));
        },
    });
}
</script>

<template>
    <EnsureLoggedIn require-admin />
    <div class="max-w-3xl mx-auto p-3 sm:p-4">
        <h1 class="text-2xl font-bold mb-4">{{ $t("admin.daily.title") }}</h1>

        <div class="flex flex-col sm:flex-row gap-3 mb-4">
            <Select v-model="selectedShop" :options="shops" filter optionLabel="name" optionValue="id"
                :placeholder="$t('admin.daily.select_shop')" class="w-full sm:w-64"
                :filter-fields="['name', 'location']"
                :empty-filter-message="$t('admin.reservations.filter_no_shop_found')" />
            <DatePicker v-model="datePicked" showIcon fluid :showOnFocus="true"
                date-format="dd/mm/yy" class="w-full sm:w-56" />
        </div>

        <template v-if="!selectedShop">
            <div class="text-center text-surface-500 mt-10">{{ $t("admin.daily.pick_shop_prompt") }}</div>
        </template>
        <template v-else>
            <div class="flex items-baseline justify-between mb-3">
                <h2 class="text-lg font-semibold capitalize">{{ dateLabel }}</h2>
                <span class="text-sm text-surface-500">{{ $t("admin.daily.total_people", { count: totalPeople }) }}</span>
            </div>

            <div v-if="loading" class="text-center text-surface-500 mt-10">
                <i class="pi pi-spin pi-spinner text-2xl" />
            </div>
            <div v-else-if="daySlots.length === 0" class="text-center text-surface-500 mt-10">
                {{ $t("admin.daily.no_slots") }}
            </div>

            <div v-for="ds in daySlots" :key="ds.slot.id"
                class="mb-4 rounded-lg border border-surface-200 dark:border-surface-700 overflow-hidden">
                <div class="flex items-center justify-between gap-2 px-3 py-2 bg-surface-100 dark:bg-surface-800">
                    <div class="flex items-center gap-2 font-semibold">
                        <i class="pi pi-clock" />
                        <span>{{ reformatTime(ds.slot.start_time) }} – {{ reformatTime(ds.slot.end_time) }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <Tag :value="`${ds.bookings.length} / ${ds.slot.max_volunteers}`"
                            :severity="ds.bookings.length >= ds.slot.max_volunteers ? 'success' : 'warn'" />
                        <Button icon="pi pi-user-plus" rounded text size="small"
                            :aria-label="$t('admin.daily.add')" @click="openAdd(ds.slot.id)" />
                    </div>
                </div>

                <div v-if="ds.bookings.length === 0" class="px-3 py-3 text-sm text-surface-500">
                    {{ $t("admin.daily.nobody") }}
                </div>
                <ul v-else class="divide-y divide-surface-200 dark:divide-surface-700">
                    <li v-for="b in ds.bookings" :key="b.reservation_id"
                        class="flex flex-wrap items-center gap-x-3 gap-y-2 px-3 py-2">
                        <div class="flex-1 min-w-0">
                            <div class="font-medium truncate">
                                {{ b.full_name }}
                                <i v-if="b.validated" class="pi pi-check-circle text-green-500 ml-1"
                                    v-tooltip="$t('admin.daily.validated')" />
                            </div>
                            <div v-if="b.group" class="text-xs text-surface-500 truncate">{{ b.group }}</div>
                        </div>
                        <div class="flex items-center gap-1">
                            <a v-if="b.phone" :href="`tel:${b.phone}`">
                                <Button icon="pi pi-phone" rounded text size="small" severity="success"
                                    :aria-label="$t('admin.daily.call')" v-tooltip="b.phone" />
                            </a>
                            <a :href="`mailto:${b.email}`">
                                <Button icon="pi pi-envelope" rounded text size="small"
                                    :aria-label="$t('admin.daily.email')" v-tooltip="b.email" />
                            </a>
                            <Button icon="pi pi-trash" rounded text size="small" severity="danger"
                                :aria-label="$t('admin.daily.remove')"
                                @click="removeBooking(b.reservation_id, b.full_name)" />
                        </div>
                    </li>
                </ul>
            </div>
        </template>
    </div>

    <Dialog v-model:visible="addDialogVisible" modal :header="$t('admin.daily.add')" class="w-[90vw] sm:w-96">
        <Select v-model="addUserId" :options="users" filter optionLabel="full_name" optionValue="id"
            :placeholder="$t('admin.reservations.select_user')" class="w-full"
            :filter-fields="['full_name', 'group', 'email']"
            :empty-filter-message="$t('admin.reservations.filter_no_user_found')" />
        <template #footer>
            <Button :label="$t('message.cancel')" severity="secondary" outlined @click="addDialogVisible = false" />
            <Button :label="$t('admin.daily.add')" :disabled="!addUserId" @click="confirmAdd" />
        </template>
    </Dialog>
</template>

<script lang="ts">
export default defineComponent({
    name: 'AdminDailyView',
    components: {
        EnsureLoggedIn,
        // eslint-disable-next-line vue/no-reserved-component-names
        Select,
        DatePicker,
        // eslint-disable-next-line vue/no-reserved-component-names
        Button,
        // eslint-disable-next-line vue/no-reserved-component-names
        Dialog,
        Tag,
    }
});
</script>
