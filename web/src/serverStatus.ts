import { ref } from 'vue';
import { api } from './api';

const POLL_INTERVAL_MS = 20000;

const serverDegraded = ref(false);
let intervalId: ReturnType<typeof setInterval> | null = null;

async function checkHealth() {
    try {
        await api.get('/health');
        serverDegraded.value = false;
    } catch {
        serverDegraded.value = true;
    }
}

function startHealthMonitor() {
    if (intervalId !== null) return;
    checkHealth();
    intervalId = setInterval(checkHealth, POLL_INTERVAL_MS);
}

export { serverDegraded, checkHealth, startHealthMonitor };
