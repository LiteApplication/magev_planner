<script setup lang="ts">
import type { ReservedTimeRange, Shop, User } from '@/api/types';
import ReservationItem from '@/components/list/ReservationItem.vue';
import DatePicker from '@/components/primevue/DatePicker';
import { reservationApi, shopApi, usersApi } from '@/main';
import { getMonday, parseServerDate } from '@/utils';
import Button from 'primevue/button';
import Select from 'primevue/select';
import Toolbar from 'primevue/toolbar';
import { computed, defineComponent, onMounted } from 'vue';
import handleError from '@/error_handler';

import { ref } from "vue";
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';

const $t = useI18n().t;
const toast = useToast();

const selectedUser = ref();
const loadedUsers = ref(false);
const users = ref<User[]>([]);

const datePicked = ref<null | Date>();

const selectedShop = ref();
const loadedShops = ref(false);
const shops = ref<Shop[]>([]);

const reservations = ref<ReservedTimeRange[]>([]);


onMounted(() => {
    usersApi.list().then((response) => {
        users.value = response;
        loadedUsers.value = true;
    }).catch(handleError(toast, $t, "error.user.unknown"));

    shopApi.list().then((response) => {
        shops.value = response;
        loadedShops.value = true;
    }).catch(handleError(toast, $t, "error.user.unknown"));
});

function search() {
    const shop_id = selectedShop.value ? selectedShop.value : undefined;
    const user_id = selectedUser.value ? selectedUser.value : undefined;
    const week = datePicked.value ? getMonday(datePicked.value) : undefined;

    reservationApi.search({ shop_id, user_id, monday: week }).then((response) => {
        reservations.value = response;
    }).catch(handleError(toast, $t, "error.reservation.unknown"));
}

// Sort reservations by start time, then group them by date and by place (shop).
const groupedReservations = computed(() => {
    const sorted = [...reservations.value].sort(
        (a, b) => parseServerDate(a.start_time).getTime() - parseServerDate(b.start_time).getTime()
    );

    type Place = { shopId: number, shopName: string, reservations: ReservedTimeRange[] };
    type DateGroup = { dateKey: string, dateLabel: string, places: Place[] };
    const dateGroups: DateGroup[] = [];

    for (const reservation of sorted) {
        const date = parseServerDate(reservation.start_time);
        const dateKey = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
        const dateLabel = date.toLocaleDateString($t("date_locale"), {
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
        });

        let dateGroup = dateGroups.find((group) => group.dateKey === dateKey);
        if (!dateGroup) {
            dateGroup = { dateKey, dateLabel, places: [] };
            dateGroups.push(dateGroup);
        }

        const shopId = reservation.shop?.id ?? -1;
        const shopName = reservation.shop?.name ?? '';
        let place = dateGroup.places.find((p) => p.shopId === shopId);
        if (!place) {
            place = { shopId, shopName, reservations: [] };
            dateGroup.places.push(place);
        }
        place.reservations.push(reservation);
    }

    return dateGroups;
});

</script>
<template>
    <Toolbar class="m-4">

        <template #start>
            <div class="card flex justify-center flex-wrap gap-4">
                <h1 class="m-2 text-center text-xl">{{ $t("admin.reservations.title") }}</h1>
                <Select v-model="selectedShop" :options="shops" filter optionLabel="name" optionValue="id" label
                    :placeholder="$t('admin.reservations.select_shop')" class="w-full md:w-56" :loading="!loadedUsers"
                    :empty-filter-message="$t('admin.reservations.filter_no_shop_found')" :filter-fields="['name', 'location']" show-clear />
                <Select v-model="selectedUser" :options="users" filter optionLabel="full_name" optionValue="id" label
                    :placeholder="$t('admin.reservations.select_user')" class="w-full md:w-56" :loading="!loadedUsers"
                    :empty-filter-message="$t('admin.reservations.filter_no_user_found')" :filter-fields="['full_name', 'group', 'email']"
                    show-clear />
                <DatePicker v-model="datePicked" showIcon fluid :date-format="$t('message.shops.week_format')" :showOnFocus="true"
                    inputId="buttondisplay" :placeholder="$t('message.select_date')" show-week showButtonBar class="w-full md:w-56" />
            </div>
        </template>
        <template #end>
            <Button label="Search" icon="pi pi-search" class="p-button-raised p-button-rounded p-button-success " @click="search" />
        </template>
    </Toolbar>


    <template v-if="reservations.length === 0">
        <div class="flex justify-center">
            <h1 class="m-4 text-center text-xl">{{ $t("admin.reservations.no_reservations") }}</h1>
        </div>
    </template>
    <template v-else>
        <section v-for="group in groupedReservations" :key="group.dateKey" class="m-4">
            <h1 class="text-2xl font-bold capitalize border-b border-slate-300 dark:border-slate-600 pb-1 mb-2">
                {{ group.dateLabel }}
            </h1>
            <div v-for="place in group.places" :key="place.shopId" class="mb-4">
                <h2 class="flex items-center gap-2 text-lg font-semibold ml-2">
                    <i class="pi pi-map-marker" />{{ place.shopName }}
                </h2>
                <ReservationItem v-for="reservation in place.reservations" :key="reservation.id" :reservation="reservation"
                    @update:reservation="search()" show-users>
                    <template #shopName>
                        <h3 v-if="reservation.title" class="text-lg font-semibold align-middle">
                            {{ reservation.status > 0 ? reservation.title : $t(reservation.title) }}
                        </h3>
                    </template>
                </ReservationItem>
            </div>
        </section>
    </template>

</template>


<script lang="ts">
export default defineComponent({
    name: 'AdminReservationsView',
    components: {
        Toolbar,
        // eslint-disable-next-line vue/no-reserved-component-names
        Select,
        DatePicker,
        // eslint-disable-next-line vue/no-reserved-component-names
        Button,
        ReservationItem
    }
});
</script>