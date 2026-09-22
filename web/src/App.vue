<script setup lang="ts">
import { RouterView } from 'vue-router'

import { defineComponent, onMounted } from 'vue'
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import ServerStatusBar from './components/ServerStatusBar.vue';
import { startHealthMonitor } from './serverStatus';

onMounted(startHealthMonitor);

</script>

<script lang="ts">
export default defineComponent({
  name: 'App',
  components: {
    RouterView,
    Toast,
    ConfirmDialog,
    ServerStatusBar
  }
})
</script>

<template>
  <ServerStatusBar />
  <Toast />

  <RouterView />
  <ConfirmDialog style="white-space: pre-line"></ConfirmDialog>
</template>

<style></style>
