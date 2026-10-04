<script setup lang="ts">

import { computed, defineComponent, onMounted, ref, watch, type Ref } from 'vue'
import { useRouter } from 'vue-router';
import { useRouteParams } from '@vueuse/router';

import { useI18n } from 'vue-i18n';
import EnsureLoggedIn from '@/components/EnsureLoggedIn.vue';
import { exampleShopWithOpenRange, type ShopWithOpenRange } from '@/api/types';
import { shopApi } from '@/main';
import WeekViewer from '@/components/WeekViewer.vue';
import { getMonday, parseLocalDate } from '@/utils';
import DatePicker from '@/components/primevue/DatePicker';
import handleError from '@/error_handler';
import { useToast } from 'primevue/usetoast';
import ShopHeader from '@/components/list/ShopHeader.vue';
import Button from 'primevue/button';

const $router = useRouter();
const $t = useI18n().t;
const toast = useToast();

const shopId = useRouteParams("id", "0", { transform: Number });
const weekNumberURL = useRouteParams("week", getMonday(new Date()), { transform: String });

const isLoading = ref(true);

function addDays(date: Date, days: number): Date {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}

const datePicked = ref(parseLocalDate(weekNumberURL.value));
const shop: Ref<ShopWithOpenRange> = ref(exampleShopWithOpenRange);
const week = computed(() => getMonday(datePicked.value));

onMounted(() => {
    shopApi.get(shopId.value).then(
        (r) => {
            shop.value = r;
            if (datePicked.value < parseLocalDate(shop.value.available_from)) {
                datePicked.value = parseLocalDate(getMonday(shop.value.available_from));
            }
        }
    ).catch(handleError(toast, $t, "error.shop.unknown")).finally(() => isLoading.value = false);
})

watch([shopId, week], () => {
    $router.push({ params: { id: shopId.value, week: week.value } });
})

</script>
<template>
    <EnsureLoggedIn :additional-loading="shop.id == -1 || isLoading" />
    <ShopHeader :shop="shop">
        <template #action>
            <div>
                <DatePicker v-model="datePicked" showIcon fluid :date-format="$t('message.shops.week_format')" :showOnFocus="false"
                    inputId="buttondisplay" :min-date="parseLocalDate(shop.available_from)" :max-date="parseLocalDate(shop.available_until)"
                    :placeholder="$t('message.select_date')" show-week />
                <div class="flex flex-row justify-between">
                    <Button icon="pi pi-chevron-left" @click="datePicked = addDays(datePicked, -7)"
                        severity="secondary" />
                    <Button icon="pi pi-chevron-right" @click="datePicked = addDays(datePicked, 7)"
                        severity="secondary" />
                </div>
            </div>
        </template>
    </ShopHeader>
    <WeekViewer :shop-id="shop.id" :week="week" v-if="shop.id != -1" v-model:loading="isLoading" />
</template>

<script lang="ts">
export default defineComponent({
    name: 'ShopsView',
    components: {
        EnsureLoggedIn,
        DatePicker,
        WeekViewer,
        ShopHeader,
        // eslint-disable-next-line vue/no-reserved-component-names
        Button
    }
})
</script>
<style></style>
