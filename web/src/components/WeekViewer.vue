<script setup lang="ts">
import { computed, defineComponent, onMounted, ref, watch } from 'vue';
import { reservationApi, shopApi, authApi } from '@/main';
import type { SlotStatus, Shop } from '@/api/types';
import DayTimeline from './DayTimeline.vue';
import { useI18n } from 'vue-i18n';
import { timeToMinutes } from '../utils';
import { type Task } from '../types';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import handleError from '@/error_handler';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';

const toast = useToast();
const confirm = useConfirm();
const { t, d } = useI18n();

const props = defineProps({
    shopId: { type: Number, required: true },
    week: { type: String, required: true },
});

const planning = ref<SlotStatus[][]>([[], [], [], [], [], [], []]);
const shopData = ref<Shop | null>(null);
const isAdmin = ref(false);

// A slot is "past" once its start time has elapsed. Non-admins cannot book it.
function isPastSlot(date: string, startTime: string): boolean {
    return new Date(`${date}T${startTime}`) < new Date();
}
const isLoading = defineModel('loading', { type: Boolean, default: false });

// Multi-slot selection: key = `${slot_id}:${date}`
const selectedSlots = ref<Set<string>>(new Set());
const confirmDialogVisible = ref(false);

const titles = computed<string[]>(
    () => Array.from({ length: 7 }, (_, i) =>
        d(new Date(props.week).setDate(new Date(props.week).getDate() + i), 'week')
    )
);

watch(() => props.week, () => {
    selectedSlots.value = new Set();
    fetchPlanning();
});

const dayBounds = computed(() => {
    let start = timeToMinutes('09:00');
    let end = timeToMinutes('18:00');
    for (const day of planning.value) {
        for (const ss of day) {
            const s = timeToMinutes(ss.slot.start_time);
            const e = timeToMinutes(ss.slot.end_time);
            if (s < start) start = Math.max(0, s - 30);
            if (e > end) end = e + 30;
        }
    }
    start = start - (start % 30);
    end = end + (30 - (end % 30 || 30));
    return { start_time: start, end_time: end };
});

function slotKey(slotId: number, date: string): string {
    return `${slotId}:${date}`;
}

const selectedSlotDetails = computed(() => {
    const result: SlotStatus[] = [];
    for (const key of selectedSlots.value) {
        const [slotIdStr, date] = key.split(':');
        const slotId = Number(slotIdStr);
        for (const day of planning.value) {
            const ss = day.find(s => s.slot.id === slotId && s.date === date);
            if (ss) { result.push(ss); break; }
        }
    }
    return result.sort((a, b) => a.date.localeCompare(b.date) || a.slot.start_time.localeCompare(b.slot.start_time));
});

const displayedTasks = computed<Task[][]>(() =>
    planning.value.map((daySlots) => {
        const tasks: Task[] = [];
        for (const ss of daySlots) {
            const startMin = timeToMinutes(ss.slot.start_time);
            const endMin = timeToMinutes(ss.slot.end_time);
            const key = slotKey(ss.slot.id, ss.date);
            const isSelected = selectedSlots.value.has(key);
            const bookedByOthers = ss.booked_count - (ss.booked_by_me ? 1 : 0);
            const remaining = ss.slot.max_volunteers - ss.booked_count;
            const past = !isAdmin.value && isPastSlot(ss.date, ss.slot.start_time);
            const description = `${ss.slot.start_time.slice(0, 5)}–${ss.slot.end_time.slice(0, 5)} · ${t('message.reservation.spots_taken', { booked: ss.booked_count, max: ss.slot.max_volunteers })}`;

            const common = {
                start_time: startMin,
                end_time: endMin,
                _row: undefined as undefined | number,
                description,
                id: ss.slot.id,
                slot_id: ss.slot.id,
                reservation_id: ss.reservation_id,
                remaining,
                slot_date: ss.date,
                selected: false,
            };

            // Own booking lane
            if (ss.booked_by_me) {
                tasks.push({
                    ...common,
                    color: '#3b82f6',
                    cursor: 'pointer',
                    title: t('message.reservation.booked_by_you'),
                    status: -2,
                });
            }

            // Booked-by-others lanes
            for (let i = 0; i < bookedByOthers; i++) {
                tasks.push({
                    ...common,
                    color: '#ef4444',
                    cursor: 'not-allowed',
                    title: t('message.reservation.booked'),
                    status: 1,
                });
            }

            // Available lanes
            for (let i = 0; i < remaining; i++) {
                const isThisOneSelected = isSelected && i === 0 && !past;
                tasks.push({
                    ...common,
                    color: past ? '#94a3b8' : (isThisOneSelected ? '#16a34a' : '#22c55e'),
                    cursor: (past || ss.booked_by_me) ? 'not-allowed' : 'pointer',
                    title: past
                        ? t('message.reservation.past')
                        : t('message.reservation.spots_remaining', { n: remaining }),
                    status: 0,
                    selected: isThisOneSelected,
                });
            }
        }
        return tasks;
    })
);

async function fetchPlanning() {
    isLoading.value = true;
    try {
        const [shop, plan, me] = await Promise.all([
            shopApi.get(props.shopId),
            reservationApi.getPlanning(props.shopId, props.week),
            authApi.me(),
        ]);
        shopData.value = shop;
        planning.value = plan;
        isAdmin.value = me.admin;
    } catch (e) {
        handleError(toast, t, 'error.shop.not_loaded')(e);
    } finally {
        isLoading.value = false;
    }
}

onMounted(fetchPlanning);

function selectionBounds(): { date: string; minStart: number; maxEnd: number } | null {
    const details = selectedSlotDetails.value;
    if (details.length === 0) return null;
    return {
        date: details[0].date,
        minStart: Math.min(...details.map(ss => timeToMinutes(ss.slot.start_time))),
        maxEnd: Math.max(...details.map(ss => timeToMinutes(ss.slot.end_time))),
    };
}

function canAddSlot(task: Task): boolean {
    const bounds = selectionBounds();
    if (!bounds) return true;
    if (task.slot_date !== bounds.date) return false;
    return task.start_time === bounds.maxEnd || task.end_time === bounds.minStart;
}

function onTaskClick(_day: number, task: Task) {
    if (!task.slot_id || !task.slot_date) return;

    // Own booking → confirm cancel with slot details
    if (task.status === -2 && task.reservation_id != null) {
        // Find slot details for the warning message
        let slotInfo = '';
        for (const day of planning.value) {
            const ss = day.find(s => s.slot.id === task.slot_id && s.date === task.slot_date);
            if (ss) {
                slotInfo = `${task.slot_date} · ${ss.slot.start_time.slice(0, 5)}–${ss.slot.end_time.slice(0, 5)}`;
                break;
            }
        }
        confirm.require({
            message: `${t('error.reservation.confirm_cancel')}\n${slotInfo}`,
            header: t('message.reservation.booked_by_you'),
            icon: 'pi pi-exclamation-triangle',
            rejectLabel: t('message.cancel'),
            acceptLabel: t('message.reservation.cancel_booking'),
            acceptClass: 'p-button-danger',
            accept: () => {
                reservationApi.cancel(task.reservation_id!).then(() => {
                    fetchPlanning();
                }).catch(handleError(toast, t, 'error.reservation.unknown'));
            },
        });
        return;
    }

    if (task.cursor === 'not-allowed') return;

    const key = slotKey(task.slot_id, task.slot_date);
    const next = new Set(selectedSlots.value);

    if (next.has(key)) {
        // Deselect only if it's at the edge of the contiguous block
        const bounds = selectionBounds();
        if (bounds && next.size > 1) {
            const taskStart = task.start_time;
            const taskEnd = task.end_time;
            if (taskStart !== bounds.minStart && taskEnd !== bounds.maxEnd) {
                toast.add({ severity: 'warn', summary: t('error.title'), detail: t('message.reservation.deselect_edge'), life: 2500 });
                return;
            }
        }
        next.delete(key);
    } else {
        if (!canAddSlot(task)) {
            toast.add({ severity: 'warn', summary: t('error.title'), detail: t('message.reservation.consecutive_only'), life: 2500 });
            return;
        }
        next.add(key);
    }
    selectedSlots.value = next;
}

async function bookSelected() {
    try {
        const details = selectedSlotDetails.value;
        if (details.length === 0) return;

        await reservationApi.bookSlots(props.shopId, {
            time_slot_ids: details.map(ss => ss.slot.id),
            date: details[0].date,
        });

        selectedSlots.value = new Set();
        confirmDialogVisible.value = false;
        await fetchPlanning();
        toast.add({ severity: 'success', summary: t('message.success'), detail: t('message.shops.booked'), life: 2000 });
    } catch (e) {
        handleError(toast, t, 'error.reservation.unknown')(e);
    }
}
function dayName(date: string): string {
    return d(new Date(date), 'week');
}
</script>

<template>
    <div v-if="shopData">
        <div id="legend" class="rounded p-4 m-4 mb-0 bg-slate-100 dark:bg-slate-800">
            <div class="flex gap-4 flex-wrap">
                <div class="flex items-center gap-1">
                    <div class="rounded square-legend" style="background: #22c55e"></div>
                    <p class="text-sm">{{ t('message.shops.open') }}</p>
                </div>
                <div class="flex items-center gap-1">
                    <div class="rounded square-legend" style="background: #ef4444"></div>
                    <p class="text-sm">{{ t('message.reservation.booked') }}</p>
                </div>
                <div class="flex items-center gap-1">
                    <div class="rounded square-legend" style="background: #3b82f6"></div>
                    <p class="text-sm">{{ t('message.reservation.booked_by_you') }}</p>
                </div>
                <div class="flex items-center gap-1">
                    <div class="rounded square-legend" style="background: #16a34a"></div>
                    <p class="text-sm">{{ t('message.reservation.selected') }}</p>
                </div>
            </div>
        </div>

        <div class="weekview">
            <div class="weekview-container">
                <DayTimeline v-for="[index, tasks] in displayedTasks.entries()" :key="index"
                    :title="titles[index]" :tasks="tasks"
                    :startOfDay="dayBounds.start_time" :endOfDay="dayBounds.end_time"
                    @click-task="(task: Task) => onTaskClick(index, task)" />
            </div>
        </div>

        <!-- Booking basket -->
        <Transition name="slide-up">
            <div v-if="selectedSlots.size > 0" class="booking-basket">
                <span class="text-sm font-semibold">{{ t('message.reservation.n_selected', { n: selectedSlots.size }) }}</span>
                <Button :label="t('message.reservation.confirm_booking')" icon="pi pi-check" size="small"
                    @click="confirmDialogVisible = true" />
                <Button icon="pi pi-times" severity="secondary" text size="small"
                    @click="selectedSlots = new Set()" v-tooltip="t('message.cancel')" />
            </div>
        </Transition>
    </div>
    <div v-else class="flex justify-center p-8 text-slate-400">
        <span class="pi pi-spin pi-spinner text-2xl"></span>
    </div>

    <!-- Confirmation dialog -->
    <Dialog v-model:visible="confirmDialogVisible" :header="t('message.reservation.confirm_booking')" modal style="min-width: 20rem">
        <ul class="flex flex-col gap-2 mb-4">
            <li v-for="ss in selectedSlotDetails" :key="`${ss.slot.id}:${ss.date}`"
                class="flex items-center gap-2 p-2 rounded" style="background: var(--p-content-hover-background)">
                <span class="pi pi-calendar-clock opacity-60"></span>
                <span class="text-sm">
                    <strong>{{ dayName(ss.date) }}</strong> {{ ss.date }}
                    · {{ ss.slot.start_time.slice(0, 5) }}–{{ ss.slot.end_time.slice(0, 5) }}
                </span>
            </li>
        </ul>
        <div class="flex justify-end gap-2">
            <Button :label="t('message.cancel')" severity="secondary" outlined @click="confirmDialogVisible = false" />
            <Button :label="t('message.save')" icon="pi pi-check" @click="bookSelected" />
        </div>
    </Dialog>
</template>

<script lang="ts">
export default defineComponent({ name: 'WeekViewer' });
</script>

<style scoped>
.weekview {
    max-width: 100%;
    overflow-x: scroll;
}
.weekview-container {
    display: flex;
    gap: 0;
    flex-wrap: nowrap;
    justify-content: space-evenly;
    min-width: fit-content;
    width: 100%;
}
.square-legend {
    width: 16px;
    height: 16px;
    border: 1px solid rgba(0,0,0,0.1);
    display: inline-block;
    flex-shrink: 0;
}

.booking-basket {
    position: sticky;
    bottom: 1rem;
    margin: 1rem;
    padding: 0.75rem 1rem;
    background: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    align-items: center;
    gap: 0.75rem;
    z-index: 10;
}

.slide-up-enter-active,
.slide-up-leave-active {
    transition: transform 0.2s ease, opacity 0.2s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
    transform: translateY(1rem);
    opacity: 0;
}
</style>
