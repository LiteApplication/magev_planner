<script setup lang="ts">
import { computed, defineComponent, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import EnsureLoggedIn from '@/components/EnsureLoggedIn.vue';
import Timeline from 'primevue/timeline';
import type { Notification } from '@/api/types';
import { PrimeIcons } from '@primevue/core/api';
import { notificationsApi } from '@/main';
import { parseServerDate } from '@/utils';
import Button from 'primevue/button';
import { useConfirm } from "primevue/useconfirm";
import handleError from '@/error_handler';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const { t, d } = useI18n();
const confirm = useConfirm();

const notifications = ref<Notification[]>([]);

const notifCount = ref(0);
const sorted = (r: Notification[]) => r.sort((a, b) => -((a.date > b.date) ? 1 : ((b.date > a.date) ? -1 : 0)))

onMounted(() => {
    notificationsApi.list().then(
        (r) => {
            notifications.value = sorted(r);
        }
    ).catch(handleError(toast, t, "error.notification.unknown"));
});

const notifications_computed = computed(() => {
    return notifications.value.map(n => {
        const data = JSON.parse(n.data);
        // Date/time fields hold UTC instants from the backend; render them in local time.
        for (const key in data) {
            if (key.startsWith("date-")) {
                data[key] = d(parseServerDate(data[key]));
            }
            if (key.startsWith("time-")) {
                data[key] = d(parseServerDate(data[key]), 'time');
            }
            if (key.startsWith("datetime-")) {
                data[key] = d(parseServerDate(data[key]), 'datetime');
            }
            if (key.startsWith("datetime_long-")) {
                data[key] = d(parseServerDate(data[key]), 'long');
            }
            if (key.startsWith("datetime_short-")) {
                data[key] = d(parseServerDate(data[key]), 'short');
            }
            if (key.endsWith("duration")) {
                // Transform 90 (minutes) into 1h30, 120 to 2h, etc.
                const hours = Math.floor(data[key] / 60);
                const minutes = data[key] % 60;
                data[key] = (hours > 0 ? hours + "h" : "") + (minutes > 0 ? minutes + "min" : "");
            }
        }
        return { ...n, data: data };
    });
});


const getIcon = (notification: Notification) => {
    if (notification.icon != null) {
        return notification.icon;
    }
    if (notification.is_reminder) {
        return PrimeIcons.BELL;
    } else {
        return PrimeIcons.ENVELOPE;
    }
};

const getColor = (notification: Notification) => {
    if (notification.is_reminder) {
        return 'bg-teal-500 dark:bg-teal-400';
    } else {
        return 'bg-blue-500 dark:bg-blue-400';
    }
};


function deleteNotification(notif: Notification) {
    notificationsApi.delete(notif.id).catch(handleError(toast, t));
    if (!notif.read) {
        notifCount.value -= 1;
    }
    notifications.value = sorted(notifications.value.filter(n => n.id !== notif.id));
}

function markAsRead(notif: Notification) {
    notificationsApi.mark_as_read(notif.id).then((r) => {
        notifications.value = sorted(notifications.value.map(n => n.id === notif.id ? r : n));
    }).catch(handleError(toast, t));
    if (!notif.read) {
        notifCount.value -= 1;
    }
    notif.read = true;
}

function markAsUnread(notif: Notification) {
    notificationsApi.mark_as_unread(notif.id).then((r) => {
        notifications.value = sorted(notifications.value.map(n => n.id === notif.id ? r : n));
    }).catch(handleError(toast, t));
    if (notif.read) {
        notifCount.value += 1;
    }
    notif.read = false;
}

function markAsReadAll() {
    notificationsApi.mark_all_as_read().then((r) => {
        notifications.value = sorted(r);
    }).catch(handleError(toast, t));
    notifCount.value = 0;
    notifications.value.forEach(n => n.read = true);
}

function deleteAllNotifications() {
    confirm.require({
        header: t('notification.delete_all'),
        message: t('notification.delete_all_confirm'),
        icon: 'pi pi-exclamation-triangle',
        acceptProps: { label: t('notification.delete_all'), icon: 'pi pi-trash', className: 'p-button-danger p-button' },
        rejectProps: { label: t('notification.cancel'), icon: 'pi pi-times', className: 'p-button-secondary p-button' },
        accept: () => {
            notificationsApi.delete_all().then((n) => {
                notifications.value = n;
                notifCount.value = n.filter(n => !n.read).length;
                toast.add({ severity: 'success', summary: t('notification.success'), detail: t('notification.all_deleted'), life: 3000 });
            }).catch(handleError(toast, t));
        }
    });
}

</script>
<script lang="ts">
export default defineComponent({
    name: 'AdminSettingsView',
    components: {
        EnsureLoggedIn,
        Timeline,
        // eslint-disable-next-line vue/no-reserved-component-names
        Button,
    }
})
</script>
<template>
    <EnsureLoggedIn v-model:notification-count="notifCount" />

    <Button :label="t('notification.mark_all_as_read')" @click="markAsReadAll" :disabled="notifCount == 0"
        :severity="notifCount == 0 ? 'secondary' : 'info'" class="ml-4 mb-4" :icon="PrimeIcons.CHECK_SQUARE" />
    <Button :label="t('notification.delete_all')" @click="deleteAllNotifications" :severity="'danger'" class="ml-4 mb-4" :icon="PrimeIcons.TRASH"
        :disabled="notifications.length == 0" />
    <Timeline :value="notifications_computed" id="timeline" pt:eventOpposite:style="max-width: 20vw;">
        <template #opposite="{ item }">
            <div class="text-surface-500 dark:text-surface-400 date-container">{{ d(parseServerDate(item.date), 'datetime') }}</div>
        </template>
        <template #content="{ item }">
            <div class="flex flex-col flex-shrink">
                <h3 v-html="t(item.message + '.title', item.data)"></h3>
                <p v-html="t(item.message + '.body', item.data)"></p>

                <div class="flex flex-row flex-wrap">
                    <Button :icon="PrimeIcons.TRASH" text severity="danger" :label="t('notification.delete')" @click="deleteNotification(item)" />
                    <Button :icon="PrimeIcons.FILE_EXPORT" text severity="primary" :label="t(item.message + '.access')"
                        @click="$router.push(item.route)" v-if="item.route != null" />
                    <Button :icon="PrimeIcons.CHECK_SQUARE" text severity="info" :label="t('notification.mark_as_unread')" @click="markAsUnread(item)"
                        v-if="item.read" />
                    <Button :icon="PrimeIcons.STOP" text severity="info" :label="t('notification.mark_as_read')" @click="markAsRead(item)" v-else />
                </div>
            </div>
        </template>

        <template #marker="slotProps">
            <span class="flex w-8 h-8 items-center justify-center text-white rounded-full z-2 shadow-sm" :class="getColor(slotProps.item)">
                <i :class="getIcon(slotProps.item)" />
            </span>
        </template>
    </Timeline>
</template>

<style scoped>
#timeline {
    max-width: 100vw;
    margin: 0;

}

.date-container {
    margin: 0;
    padding: 0;
    font-size: 0.8rem;
    color: #6b7280;
    text-wrap: balance;
    max-width: 20vw;
}
</style>