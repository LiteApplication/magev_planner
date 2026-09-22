<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { serverDegraded } from '@/serverStatus';

const { t } = useI18n();
</script>

<template>
    <div v-if="serverDegraded" class="server-status-bar">
        <span class="pi pi-exclamation-triangle"></span>
        <span>{{ t('message.server_status.degraded') }}</span>
    </div>
</template>

<style scoped>
.server-status-bar {
    position: sticky;
    top: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: #f59e0b;
    color: #1f2937;
    font-size: 0.875rem;
    font-weight: 600;
    text-align: center;
}
</style>
