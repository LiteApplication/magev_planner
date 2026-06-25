<script setup lang="ts">
import Menubar from 'primevue/menubar';
import { computed, defineComponent, onMounted, ref } from 'vue';
import { PrimeIcons } from '@primevue/core/api';
import { useI18n } from 'vue-i18n';
import { authApi, notificationsApi } from '@/main';
import { useRouter } from 'vue-router';
import Button from 'primevue/button';
import LocaleChanger from './LocaleChanger.vue';
import handleError from '@/error_handler';
import { useToast } from 'primevue/usetoast';

const $t = useI18n().t;
const router = useRouter();
const toast = useToast();

const logout = () => {
    authApi.logout();
    router.push({ name: "login" });
};


const notificationModel = defineModel('notificationCount');

defineProps({
    isAdmin: Boolean
})


onMounted(() => {
    // Fetch notification count
    notificationsApi.count().then(
        (r) => {
            notificationModel.value = r;
        }
    );
});

const items = ref<any>([
    {
        label: $t("menu.my_reservations"),
        icon: PrimeIcons.CALENDAR,
        route: "/"
    },
    {
        label: $t("menu.create_reservation"),
        icon: PrimeIcons.PLUS,
        route: "/shops"
    }, {
        label: $t("menu.daily"),
        icon: PrimeIcons.LIST_CHECK,
        adminRequired: true,
        route: "/daily"
    }, {
        label: $t("menu.admin.title"),
        icon: PrimeIcons.COG,
        adminRequired: true,
        items: [
            {
                label: $t("menu.admin.users"),
                icon: PrimeIcons.USERS,
                route: "/admin/users"
            },
            {
                label: $t("menu.admin.shops"),
                icon: PrimeIcons.BUILDING,
                route: "/admin/shops"
            },
            {
                label: $t("menu.admin.reservations"),
                icon: PrimeIcons.CALENDAR,
                route: "/admin/reservations"
            },
            {
                label: $t("menu.admin.settings"),
                icon: PrimeIcons.FILE_EDIT,
                route: "/admin/settings"
            }
        ]
    }]);

// Get browser preference
const prefersDarkScheme = computed(() => window.matchMedia("(prefers-color-scheme: dark)").matches);

</script>

<template>
    <Menubar :model="items" class="m-4">
        <template #start>
            <img src="../assets/logo-dark.png" alt="Logo" class="p-mr-2 h-12" id="logo" v-if="prefersDarkScheme" />
            <img src="../assets/logo-light.png" alt="Logo" class="p-mr-2 h-12" id="logo" v-else />
        </template>
        <template #item="{ item, props, hasSubmenu }">
            <div v-if="!item.adminRequired || isAdmin">
                <router-link v-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
                    <a v-ripple :href="href" v-bind="props.action" @click="navigate">
                        <span :class="item.icon" />
                        <span class="ml-1">{{ item.label }}</span>
                    </a>
                </router-link>
                <a v-else v-ripple :href="item.url" :target="item.target" v-bind="props.action">
                    <span :class="item.icon" />
                    <span class="ml-1">{{ item.label }}</span>
                    <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down" />
                </a>
            </div>
        </template>
        <!-- Logout button at the end -->
        <template #end>
            <div class="flex items-center gap-2">
                <Button :icon="PrimeIcons.BELL" :severity="notificationModel == 0 ? 'secondary' : 'info'" :text="notificationModel == 0"
                    :badge="notificationModel ? notificationModel.toString() : undefined" @click="router.push({ name: 'notifications' })" />
                <LocaleChanger />
                <Button :label="$t('message.logout')" rounded icon="pi pi-sign-out" @click="logout" severity="danger" outlined />
            </div>
        </template>

    </Menubar>
</template>

<script lang="ts">
export default defineComponent({
    name: 'MainMenu',
    components: {
        Menubar,
        // eslint-disable-next-line vue/no-reserved-component-names
        Button,
        LocaleChanger,
    }
})
</script>

<style scoped>
#logo {
    object-fit: contain;
}
</style>