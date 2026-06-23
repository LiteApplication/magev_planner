<template>
    <EnsureLoggedIn require-admin />
    <div class="admin-layout">
        <aside class="admin-sidebar">
            <div class="sidebar-header">
                <span class="pi pi-shield text-xl"></span>
                <span class="font-bold text-lg">{{ $t('menu.admin.title') }}</span>
            </div>
            <nav class="sidebar-nav">
                <RouterLink v-for="item in navItems" :key="item.to" :to="item.to"
                    class="nav-item" :class="{ active: $route.path.startsWith(item.to) }">
                    <span :class="item.icon" class="text-base"></span>
                    <span>{{ item.label }}</span>
                </RouterLink>
            </nav>
        </aside>
        <main class="admin-content">
            <RouterView />
        </main>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import EnsureLoggedIn from '@/components/EnsureLoggedIn.vue';

const { t } = useI18n();

const navItems = computed(() => [
    { to: '/admin/shops', label: t('menu.admin.shops'), icon: 'pi pi-shop' },
    { to: '/admin/reservations', label: t('menu.admin.reservations'), icon: 'pi pi-calendar' },
    { to: '/admin/users', label: t('menu.admin.users'), icon: 'pi pi-users' },
    { to: '/admin/enterprises', label: t('menu.admin.enterprises'), icon: 'pi pi-building' },
    { to: '/admin/documents', label: t('menu.admin.documents'), icon: 'pi pi-file' },
    { to: '/admin/mail-templates', label: t('menu.admin.mail_templates'), icon: 'pi pi-envelope' },
    { to: '/admin/settings', label: t('menu.admin.settings'), icon: 'pi pi-cog' },
]);
</script>

<style scoped>
.admin-layout {
    display: flex;
    min-height: calc(100vh - 4rem);
}

.admin-sidebar {
    width: 220px;
    flex-shrink: 0;
    background: var(--p-content-background);
    border-right: 1px solid var(--p-content-border-color);
    display: flex;
    flex-direction: column;
}

.sidebar-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--p-content-border-color);
    color: var(--p-primary-color);
}

.sidebar-nav {
    display: flex;
    flex-direction: column;
    padding: 0.5rem;
    gap: 2px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.625rem 1rem;
    border-radius: var(--p-border-radius-md, 6px);
    font-size: 0.875rem;
    color: var(--p-text-muted-color);
    text-decoration: none;
    transition: background 0.15s, color 0.15s;
}

.nav-item:hover {
    background: var(--p-navigation-item-focus-background);
    color: var(--p-text-color);
}

.nav-item.active {
    background: var(--p-highlight-background);
    color: var(--p-highlight-color);
    font-weight: 600;
}

.admin-content {
    flex: 1;
    overflow: auto;
    padding: 1.5rem;
}
</style>
