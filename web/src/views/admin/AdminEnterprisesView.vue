<template>
    <DataTable :value="enterprises" dataKey="id" tableStyle="min-width: 50rem" size="large" stripedRows sort-field="name" :sort-order="1"
        removableSort :globalFilterFields="['name', 'slug', 'email_domains']" v-model:filters="filters">
        <template #header>
            <Toolbar>
                <template #start>
                    <Button :label="$t('message.add')" icon="pi pi-plus" @click="openCreate" />
                </template>
                <template #end>
                    <IconField>
                        <InputIcon><i class="pi pi-search" /></InputIcon>
                        <InputText v-model="filters['global'].value" :placeholder="$t('message.search')" />
                    </IconField>
                </template>
            </Toolbar>
        </template>
        <template #empty>
            <div class="p-4">
                <p>{{ $t('admin.enterprises.none') }}</p>
            </div>
        </template>

        <Column field="name" :header="$t('admin.enterprises.name')" sortable />
        <Column field="slug" :header="$t('admin.enterprises.slug')" sortable>
            <template #body="{ data }"><code>{{ data.slug }}</code></template>
        </Column>
        <Column field="email_domains" :header="$t('admin.enterprises.email_domains')" sortable>
            <template #body="{ data }">
                <span v-if="data.email_domains">{{ data.email_domains }}</span>
                <span v-else class="text-slate-400">{{ $t('admin.enterprises.any_email') }}</span>
            </template>
        </Column>
        <Column :header="$t('admin.enterprises.checkbox')" data-type="boolean">
            <template #body="{ data }">
                <i class="pi" :class="data.checkbox_text ? 'pi-check-circle text-green-500' : 'pi-minus-circle text-slate-400'"></i>
            </template>
        </Column>
        <Column :header="$t('admin.actions')" style="width: 8rem">
            <template #body="{ data }">
                <div class="flex gap-2">
                    <Button icon="pi pi-pencil" severity="warn" text @click="openEdit(data)" />
                    <Button icon="pi pi-trash" severity="danger" text @click="confirmDelete(data)" />
                </div>
            </template>
        </Column>
    </DataTable>

    <Dialog v-model:visible="dialogVisible" modal :header="editingId ? $t('admin.enterprises.edit') : $t('admin.enterprises.add')"
        :style="{ width: '34rem' }">
        <div class="flex flex-col gap-4 pt-2">
            <IftaLabel>
                <InputText id="ent-name" v-model="form.name" fluid @blur="autoSlug" />
                <label for="ent-name">{{ $t('admin.enterprises.name') }}</label>
            </IftaLabel>
            <IftaLabel>
                <InputText id="ent-slug" v-model="form.slug" fluid />
                <label for="ent-slug">{{ $t('admin.enterprises.slug') }}</label>
            </IftaLabel>
            <p class="text-xs text-slate-500 -mt-2">{{ $t('admin.enterprises.slug_hint') }}</p>
            <IftaLabel>
                <InputText id="ent-domains" v-model="form.email_domains" fluid />
                <label for="ent-domains">{{ $t('admin.enterprises.email_domains') }}</label>
            </IftaLabel>
            <p class="text-xs text-slate-500 -mt-2">{{ $t('admin.enterprises.email_domains_hint') }}</p>
            <IftaLabel>
                <Textarea id="ent-checkbox" v-model="form.checkbox_text" rows="2" fluid autoResize />
                <label for="ent-checkbox">{{ $t('admin.enterprises.checkbox_text') }}</label>
            </IftaLabel>
            <IftaLabel>
                <Textarea id="ent-welcome" v-model="form.welcome_message" rows="3" fluid autoResize />
                <label for="ent-welcome">{{ $t('admin.enterprises.welcome_message') }}</label>
            </IftaLabel>
            <IftaLabel>
                <Textarea id="ent-reminder" v-model="form.reminder_message" rows="3" fluid autoResize />
                <label for="ent-reminder">{{ $t('admin.enterprises.reminder_message') }}</label>
            </IftaLabel>
            <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
        </div>
        <template #footer>
            <Button :label="$t('message.cancel')" text @click="dialogVisible = false" />
            <Button :label="$t('message.save')" icon="pi pi-save" @click="save" :loading="saving" />
        </template>
    </Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, defineComponent } from 'vue';
import type { Enterprise } from '@/api/types';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import IftaLabel from 'primevue/iftalabel';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import Dialog from 'primevue/dialog';
import Toolbar from 'primevue/toolbar';
import { FilterMatchMode } from '@primevue/core/api';
import { enterpriseApi } from '@/main';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useI18n } from 'vue-i18n';
import handleError from '@/error_handler';

const $t = useI18n().t;
const toast = useToast();
const confirm = useConfirm();

const enterprises = ref<Enterprise[]>([]);
const filters = ref({ global: { value: null, matchMode: FilterMatchMode.CONTAINS } });

const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const saving = ref(false);
const error = ref<string | null>(null);

const emptyForm = () => ({
    slug: '', name: '', email_domains: '', checkbox_text: '', welcome_message: '', reminder_message: '',
});
const form = ref(emptyForm());

function loadList() {
    enterpriseApi.list().then(r => { enterprises.value = r; }).catch(handleError(toast, $t));
}
onMounted(loadList);

function slugify(value: string): string {
    return value.trim().toLowerCase().replace(/[^\w]+/g, '-').replace(/^-+|-+$/g, '');
}

function autoSlug() {
    if (!form.value.slug && form.value.name) form.value.slug = slugify(form.value.name);
}

function openCreate() {
    editingId.value = null;
    form.value = emptyForm();
    error.value = null;
    dialogVisible.value = true;
}

function openEdit(e: Enterprise) {
    editingId.value = e.id;
    form.value = {
        slug: e.slug, name: e.name, email_domains: e.email_domains,
        checkbox_text: e.checkbox_text, welcome_message: e.welcome_message, reminder_message: e.reminder_message,
    };
    error.value = null;
    dialogVisible.value = true;
}

function save() {
    if (!form.value.name.trim()) { error.value = $t('admin.enterprises.name_required'); return; }
    if (!form.value.slug.trim()) form.value.slug = slugify(form.value.name);
    saving.value = true;
    error.value = null;
    const payload = { ...form.value };
    const req = editingId.value
        ? enterpriseApi.update(editingId.value, payload)
        : enterpriseApi.create(payload);
    req.then(() => {
        saving.value = false;
        dialogVisible.value = false;
        toast.add({ severity: 'success', summary: $t('message.success'), detail: $t('admin.enterprises.saved'), life: 2000 });
        loadList();
    }).catch((e) => {
        saving.value = false;
        error.value = e?.response?.data?.detail ? $t(e.response.data.detail) : $t('error.unknown');
    });
}

function confirmDelete(e: Enterprise) {
    confirm.require({
        header: $t('admin.enterprises.delete'),
        message: $t('admin.enterprises.delete_confirm', { name: e.name }),
        icon: 'pi pi-exclamation-triangle',
        acceptProps: { label: $t('admin.delete'), icon: 'pi pi-trash', class: 'p-button-danger p-button' },
        rejectProps: { label: $t('admin.cancel'), icon: 'pi pi-times', class: 'p-button-secondary p-button' },
        accept: () => {
            enterpriseApi.delete(e.id).then(() => {
                toast.add({ severity: 'success', summary: $t('message.success'), detail: $t('admin.enterprises.deleted'), life: 2000 });
                loadList();
            }).catch(handleError(toast, $t));
        },
    });
}
</script>

<script lang="ts">
export default defineComponent({ name: 'AdminEnterprisesView' });
</script>
