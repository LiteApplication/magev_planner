<template>
    <DataTable :value="settings" dataKey="key" tableStyle="min-width: 60rem" size="large" stripedRows sort-field="group" :sort-order="1" removableSort
        :globalFilterFields="['key', 'value']" filterDisplay="row" v-model:filters="filters" editMode="row" @row-edit-save="saveRow"
        v-model:editingRows="editingRows" @row-edit-init="editingRows = [$event.data]" @row-edit-cancel="editingRows = []"
        v-model:expandedRows="expandedRows">
        <template #header>
            <Toolbar>
                <template #start>
                    <Button label="Optimize Database" icon="pi pi-cog" class="p-button-success" @click="optimizeDatabase" />
                </template>
                <template #end>
                    <IconField>
                        <InputIcon>
                            <i class=" pi pi-search" />
                        </InputIcon>
                        <InputText v-model="filters['global'].value" :placeholder="$t('message.search')" />
                    </IconField>
                </template>
            </Toolbar>
        </template>
        <template #empty>
            <div class="p-4">
                <p>{{ $t("message.empty_list") }}</p>
            </div>
        </template>
        <Column field="key" :header="$t('admin.settings.key')" sortable>
            <template #body="{ data }">
                <p>
                    {{ $t(`admin.settings.title.${data.key}`) }}
                </p>
            </template>
        </Column>
        <Column field="value" :header="$t('admin.settings.value')" sortable>
            <template #editor>
                <ToggleSwitch v-if="['True', 'False'].includes(editingRows[0].value)" v-model="editingRows[0].value" true-value="True"
                    false-value="False" />
                <InputText v-model="editingRows[0].value" v-else />
            </template>
        </Column>
        <Column expander style="width: 3rem" />
        <Column rowEditor style="width: 8rem" bodyStyle="text-align:center"></Column>
        <template #expansion="slotProps">
            <div class="p-4">
                <p v-html="$t('admin.settings.description.' + slotProps.data.key)"></p>
            </div>
        </template>
    </DataTable>
</template>

<script setup lang="ts">
import { type Setting } from '@/api/types';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import { FilterMatchMode } from '@primevue/core/api';
import { defineComponent, onMounted, ref } from 'vue'
import { settingsApi } from '@/main';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';
import Toolbar from 'primevue/toolbar';
import ToggleSwitch from 'primevue/toggleswitch';
import handleError from '@/error_handler';

const toast = useToast();
const $t = useI18n().t;

const settings = ref<Setting[]>([
]);

const filters = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
});

const editingRows = ref<Setting[]>([]);
const expandedRows = ref<Setting[]>([]);



function loadList() {
    settingsApi.list().then(
        (r) => {
            settings.value = r;
        }
    ).catch(handleError(toast, $t));
}

const saveRow = (e: any) => {
    settingsApi.update(e.data.key, e.data.value).then(
        (new_setting) => {
            toast.add({ severity: 'success', summary: $t("admin.settings.saved_title"), detail: $t("admin.settings.saved_description", { key: new_setting.key }), life: 3000 });
        }
    ).catch(handleError(toast, $t));
};

function optimizeDatabase() {
    settingsApi.cleanupDb().then(
        (result) => {
            toast.add({ severity: 'success', summary: $t("admin.settings.optimized_title"), detail: $t("admin.settings.optimized_description", result), life: 3000 });
        }
    ).catch(handleError(toast, $t));
}



onMounted(loadList);

</script>

<script lang="ts">
export default defineComponent({
    name: 'AdminSettingsView',
    components: {
        DataTable,
        Column,
        // eslint-disable-next-line vue/no-reserved-component-names
        Button,
        IconField,
        InputIcon,
        InputText,
        Toolbar,
        ToggleSwitch
    },
})
</script>