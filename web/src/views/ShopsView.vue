<script setup lang="ts">

import { defineComponent, onMounted, ref, type Ref } from 'vue'

import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';
import EnsureLoggedIn from '@/components/EnsureLoggedIn.vue';
import ShopItem from '@/components/list/ShopItem.vue';
import { exampleShop, type Shop } from '@/api/types';
import { shopApi } from '@/main';
import handleError from '@/error_handler';

const toast = useToast();
const $t = useI18n().t;

const shops: Ref<Shop[]> = ref([
    exampleShop,
    exampleShop,
]);

onMounted(() => {
    shopApi.list().then(
        (r) => { shops.value = r }
    ).catch(handleError(toast, $t, "error.shop.unknown"));
}
)



</script>
<template>
    <EnsureLoggedIn />
    <h2 class="m-4 text-center text-xl">{{ $t("message.shops.select") }}</h2>
    <div class="flex flex-wrap gap-4 justify-center w-full content-stretch">
        <ShopItem v-for="(shop, index) in shops" :key="shop.id === -1 ? index : shop.id" :shop="shop" />
    </div>
</template>

<script lang="ts">
export default defineComponent({
    name: 'ShopsView',
    components: {
        EnsureLoggedIn,
        ShopItem
    }
})
</script>
<style></style>