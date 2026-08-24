<template>
    <Dialog v-model:visible="visible" modal :header="editingSlot?.id ? $t('message.edit') : $t('message.add')"
        :style="{ width: '28rem' }" :closable="true">
        <div class="flex flex-col gap-4 pt-2">
            <IftaLabel v-if="editingSlot?.id">
                <Select id="slot-mode" v-model="saveMode" :options="saveModeOptions"
                    optionLabel="label" optionValue="value" fluid />
                <label for="slot-mode">{{ $t('admin.shop.slot_edit_scope') }}</label>
            </IftaLabel>
            <div class="flex gap-4">
                <IftaLabel class="flex-1">
                    <Select id="slot-day" v-model="form.day"
                        :options="Array.from({ length: 7 }, (_, i) => ({ label: $t('day.' + i), value: i }))"
                        optionLabel="label" optionValue="value" fluid />
                    <label for="slot-day">{{ $t('admin.shop.or_day') }}</label>
                </IftaLabel>
            </div>
            <div class="flex gap-4">
                <IftaLabel class="flex-1">
                    <InputMask id="slot-start" v-model="form.start_time" mask="99:99" placeholder="HH:MM" fluid />
                    <label for="slot-start">{{ $t('admin.shop.or_start') }}</label>
                </IftaLabel>
                <IftaLabel class="flex-1">
                    <InputMask id="slot-end" v-model="form.end_time" mask="99:99" placeholder="HH:MM" fluid />
                    <label for="slot-end">{{ $t('admin.shop.or_end') }}</label>
                </IftaLabel>
            </div>
            <IftaLabel>
                <InputNumber id="slot-max" v-model="form.max_volunteers" :min="1" fluid />
                <label for="slot-max">{{ $t('admin.shop.slot_max_volunteers') }}</label>
            </IftaLabel>
            <div v-if="saveMode !== 'single'" class="flex gap-4">
                <IftaLabel v-if="saveMode === 'all'" class="flex-1">
                    <DatePicker id="slot-from" v-model="form.valid_from_date" date-format="yy-mm-dd" fluid />
                    <label for="slot-from">{{ $t('admin.shop.slot_valid_from') }}</label>
                </IftaLabel>
                <IftaLabel class="flex-1">
                    <DatePicker id="slot-until" v-model="form.valid_until_date" date-format="yy-mm-dd" fluid />
                    <label for="slot-until">{{ $t('admin.shop.slot_valid_until') }}</label>
                </IftaLabel>
            </div>
            <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
        </div>
        <template #footer>
            <div class="flex justify-between w-full">
                <Button v-if="editingSlot?.id" :label="$t('message.delete')" severity="danger" text @click="onDelete" />
                <div class="flex gap-2 ml-auto">
                    <Button :label="$t('message.cancel')" text @click="visible = false" />
                    <Button :label="$t('message.save')" @click="onSave(saveMode)" />
                </div>
            </div>
        </template>
    </Dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import type { TimeSlot, SaveMode } from '@/api/types';
import { useI18n } from 'vue-i18n';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import InputNumber from 'primevue/inputnumber';
import InputMask from 'primevue/inputmask';
import Select from 'primevue/select';
import IftaLabel from 'primevue/iftalabel';
import DatePicker from '@/components/primevue/DatePicker';

const props = defineProps<{
    editingSlot: Partial<TimeSlot> | null,
    shopId: number
}>();

const emit = defineEmits<{
    save: [slot: Partial<TimeSlot>, mode: SaveMode],
    delete: [slotId: number]
}>();

const visible = defineModel<boolean>('visible', { default: false });

const { t } = useI18n();
const error = ref<string | null>(null);

const saveMode = ref<SaveMode>('all');
const saveModeOptions = computed(() => [
    { label: t('admin.shop.slot_save_all'), value: 'all' },
    { label: t('admin.shop.slot_save_upcoming'), value: 'upcoming' },
    { label: t('admin.shop.slot_save_single'), value: 'single' },
]);

const form = ref({
    day: 0,
    start_time: '09:00',
    end_time: '11:00',
    max_volunteers: 1,
    valid_from_date: new Date(),
    valid_until_date: new Date(new Date().getFullYear(), 11, 31),
});

watch(() => props.editingSlot, (slot) => {
    if (!slot) return;
    form.value.day = slot.day ?? 0;
    form.value.start_time = slot.start_time ? slot.start_time.slice(0, 5) : '09:00';
    form.value.end_time = slot.end_time ? slot.end_time.slice(0, 5) : '11:00';
    form.value.max_volunteers = slot.max_volunteers ?? 1;
    form.value.valid_from_date = slot.valid_from ? new Date(slot.valid_from) : new Date();
    form.value.valid_until_date = slot.valid_until
        ? new Date(slot.valid_until)
        : new Date(new Date().getFullYear(), 11, 31);
    saveMode.value = 'all';
    error.value = null;
}, { immediate: true });

function toDateStr(d: Date): string {
    const offset = d.getTimezoneOffset();
    const local = new Date(d.getTime() - offset * 60000);
    return local.toISOString().slice(0, 10);
}

function onSave(mode: SaveMode) {
    if (!form.value.start_time.match(/^\d{2}:\d{2}$/) || !form.value.end_time.match(/^\d{2}:\d{2}$/)) {
        error.value = 'Invalid time format';
        return;
    }
    error.value = null;
    emit('save', {
        id: props.editingSlot?.id,
        shop_id: props.shopId,
        day: form.value.day,
        start_time: form.value.start_time + ':00',
        end_time: form.value.end_time + ':00',
        max_volunteers: form.value.max_volunteers,
        valid_from: toDateStr(form.value.valid_from_date),
        valid_until: toDateStr(form.value.valid_until_date),
    }, mode);
    visible.value = false;
}

function onDelete() {
    if (props.editingSlot?.id) {
        emit('delete', props.editingSlot.id);
        visible.value = false;
    }
}
</script>
