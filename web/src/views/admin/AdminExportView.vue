<template>
    <div class="export-view">
        <header class="mb-6">
            <h1 class="flex items-center gap-3 text-2xl font-bold">
                <i class="pi pi-file-export text-primary" />{{ $t('admin.export.title') }}
            </h1>
            <p class="mt-2 max-w-3xl text-slate-500 dark:text-slate-400">{{ $t('admin.export.subtitle') }}</p>
        </header>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
            <Card v-for="opt in options" :key="opt.range" class="export-card">
                <template #header>
                    <div class="card-banner" :style="{ background: opt.color }">
                        <i :class="opt.icon" />
                    </div>
                </template>
                <template #title>{{ $t(opt.titleKey) }}</template>
                <template #content>
                    <p class="min-h-12 text-sm text-slate-500 dark:text-slate-400">{{ $t(opt.descKey) }}</p>
                </template>
                <template #footer>
                    <Button class="w-full" :label="$t('admin.export.download')" icon="pi pi-download"
                        :loading="loading === opt.range" :disabled="loading !== null" @click="download(opt.range)" />
                </template>
            </Card>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, defineComponent } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';
import { exportApi } from '@/main';
import type { PlanningRange } from '@/api/export';
import handleError from '@/error_handler';

const $t = useI18n().t;
const toast = useToast();

const loading = ref<PlanningRange | null>(null);

const options: { range: PlanningRange; titleKey: string; descKey: string; icon: string; color: string }[] = [
    { range: 'week', titleKey: 'admin.export.week', descKey: 'admin.export.week_desc', icon: 'pi pi-calendar', color: '#2e7d6b' },
    { range: 'fortnight', titleKey: 'admin.export.fortnight', descKey: 'admin.export.fortnight_desc', icon: 'pi pi-calendar-plus', color: '#1f6f9c' },
    { range: 'all', titleKey: 'admin.export.all', descKey: 'admin.export.all_desc', icon: 'pi pi-calendar-times', color: '#7a4fb0' },
];

function download(range: PlanningRange) {
    loading.value = range;
    exportApi.downloadPlanning(range).then(() => {
        toast.add({ severity: 'success', summary: $t('message.success'), detail: $t('admin.export.downloaded'), life: 2500 });
    }).catch(handleError(toast, $t, 'admin.export.failed')).finally(() => {
        loading.value = null;
    });
}
</script>

<script lang="ts">
export default defineComponent({ name: 'AdminExportView' });
</script>

<style scoped>
.card-banner {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 5rem;
    border-top-left-radius: var(--p-border-radius-lg, 8px);
    border-top-right-radius: var(--p-border-radius-lg, 8px);
    color: #ffffff;
    font-size: 2rem;
}

.export-card {
    overflow: hidden;
}
</style>
