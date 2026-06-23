<template>
    <div class="bg-slate-200 dark:bg-slate-700 rounded-lg m-4 p-3">
        <div class="flex justify-between items-center">
            <div class="flex flex-col">
                <div class="flex flex-row gap-2 items-center">
                    <Button icon="pi pi-map-marker" severity="info" rounded outlined aria-label="Bookmark" as="a" :href="reservation.shop?.maps_link"
                        target="_blank" v-if="reservation.id != -1" />
                    <Skeleton shape="circle" size="2rem" class="mr-2" v-else></Skeleton>
                    <slot name="shopName" :shop="shop">
                        <h2 class="text-xl font-semibold align-middle" v-if="reservation.id != -1">{{ reservation.shop?.name }}</h2>
                        <Skeleton width="15rem" height="1.5rem" v-else></Skeleton>
                    </slot>
                </div>
                <p v-if="reservation.id != -1">
                    {{ $t('message.date') }} : <strong>
                        {{ date }}</strong>, {{ $t('message.time') }}: <strong>
                        {{ start }}</strong> - <strong>
                        {{ end }}</strong></p>
                <Skeleton class="mt-2" width="15rem" height="1rem" v-else></Skeleton>
            </div>
            <div class="flex flex-row gap-2">
                <Button :icon="PrimeIcons.EYE" aria-label="View" outlined severity="info" v-if="reservation.id != -1" @click="gotoReservation" />
                <Skeleton shape="circle" size="2rem" v-else></Skeleton>
                <Button icon="pi pi-pencil" aria-label="Edit" severity="warn" :disabled="reservation.validated" @click="editVisible = true"
                    v-if="reservation.id != -1" />
                <Skeleton shape="circle" size="2rem" v-else></Skeleton>
            </div>
        </div>
    </div>
    <ReservationDialog v-model:start-time="dialogTimeStart" v-model:end-time="dialogTimeEnd" v-model:visible="editVisible" :date="dialogDate"
        :shop-data="shop" :title="$t('message.reservation.edit_title')" :description="$t('message.reservation.edit_description')"
        @save="updateReservation" @delete="deleteReservation" :show-users="showUsers" show-delete :users="users" :show-validated="showValidated"
        v-model:validated="validatedModel" v-model:selected-user="userModel" />
</template>

<script setup lang="ts">
import { type ShopWithOpenRange, type ReservedTimeRange, type Shop, type User } from '@/api/types';
import { date_start_end, getMonday, parseServerDate } from '@/utils';
import Button from 'primevue/button';
import Skeleton from 'primevue/skeleton';
import { computed, defineComponent, onMounted, ref, type PropType } from 'vue';
import { reservationApi, shopApi, usersApi } from '@/main';
import { useI18n } from 'vue-i18n';
import { PrimeIcons } from '@primevue/core/api';
import { useRouter } from 'vue-router';
import handleError from '@/error_handler';
import { useToast } from 'primevue/usetoast';
import ReservationDialog from '../dialog/ReservationDialog.vue';

const $t = useI18n().t;
const router = useRouter();
const toast = useToast();
const props = defineProps({
    reservation: {
        type: Object as PropType<ReservedTimeRange>,
        required: true
    },
    showUsers: {
        type: Boolean,
        default: false
    },
    showValidated: {
        type: Boolean,
        default: false
    }
});


const computed_date_start_end = computed(() => date_start_end(props.reservation.start_time, props.reservation.duration_minutes, $t("date_locale")));
const date = computed(() => computed_date_start_end.value.date);
const start = computed(() => computed_date_start_end.value.start);
const end = computed(() => computed_date_start_end.value.end);

const users = ref<User[]>([]);
const userModel = ref<User | null>(null);
const validatedModel = ref(props.reservation.validated);

const editVisible = ref(false);

const shop = ref<Shop | ShopWithOpenRange | null>(props.reservation.shop);
onMounted(() => {
    shopApi.get(props.reservation.shop!.id).then(result => {
        shop.value = result
    }).catch(handleError(toast, $t));

    if (props.showUsers) {
        usersApi.list().then(result => {
            users.value = result;
        }).catch(handleError(toast, $t));
    }
});

const dialogDate = ref(parseServerDate(props.reservation.start_time));
const dialogTimeStart = ref(parseServerDate(props.reservation.start_time));
const dialogTimeEnd = ref(new Date(dialogTimeStart.value.getTime() + props.reservation.duration_minutes * 60 * 1000));

const emit = defineEmits(['update:reservation']);

function gotoReservation() {
    if (props.reservation.id === -1) return;
    router.push({
        name: 'shop', params: {
            id: props.reservation.shop!.id,
            week: getMonday(parseServerDate(props.reservation.start_time))
        }
    });
}

function updateReservation(_startDate: Date, _endDate: Date, user: User | null, validated: boolean) {
    const tasks: Promise<unknown>[] = [];

    if (user !== null && user.id !== undefined) {
        tasks.push(reservationApi.reassign(props.reservation.id!, user.id));
    }

    if (validated && !props.reservation.validated) {
        tasks.push(reservationApi.validate(props.reservation.id!));
    }

    if (tasks.length === 0) {
        editVisible.value = false;
        return;
    }

    Promise.all(tasks).then(() => {
        emit('update:reservation', { ...props.reservation, validated });
        editVisible.value = false;
    }).catch(handleError(toast, $t, 'error.reservation.not_updated'));
}

function deleteReservation() {
    reservationApi.cancel(props.reservation.id!,).then(
        () => {
            emit('update:reservation', null); // remove the reservation from the list
            editVisible.value = false;
        }
    ).catch(
        handleError(toast, $t, "error.reservation.not_deleted")
    );
}


</script>

<script lang="ts">
export default defineComponent({
    name: 'ReservationItem',
    components: {
        // eslint-disable-next-line vue/no-reserved-component-names
        Button,
        Skeleton,
        ReservationDialog
    }
})

</script>
