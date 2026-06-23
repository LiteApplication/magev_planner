<template>
    <DataTable :value="documents" dataKey="id" tableStyle="min-width: 50rem" size="large" stripedRows
        :globalFilterFields="['filename', 'content_type']" v-model:filters="filters">
        <template #header>
            <Toolbar>
                <template #start>
                    <FileUpload mode="basic" :auto="true" :customUpload="true" @uploader="onUpload" :chooseLabel="$t('admin.documents.upload')"
                        chooseIcon="pi pi-upload" :disabled="uploading" />
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
                <p>{{ $t('admin.documents.none') }}</p>
            </div>
        </template>

        <Column :header="$t('admin.documents.preview')" style="width: 5rem">
            <template #body="{ data }">
                <img v-if="isImage(data)" :src="data.url" :alt="data.filename" class="preview-thumb" />
                <i v-else class="pi pi-file text-2xl text-slate-400"></i>
            </template>
        </Column>
        <Column field="filename" :header="$t('admin.documents.filename')" sortable />
        <Column field="content_type" :header="$t('admin.documents.type')" sortable />
        <Column field="size" :header="$t('admin.documents.size')" sortable>
            <template #body="{ data }">{{ humanSize(data.size) }}</template>
        </Column>
        <Column :header="$t('admin.actions')" style="width: 11rem">
            <template #body="{ data }">
                <div class="flex gap-2">
                    <Button icon="pi pi-copy" severity="info" text @click="copyLink(data)" v-tooltip.top="$t('admin.documents.copy_link')" />
                    <Button icon="pi pi-external-link" severity="secondary" text as="a" :href="data.url" target="_blank"
                        v-tooltip.top="$t('admin.documents.open')" />
                    <Button icon="pi pi-trash" severity="danger" text @click="confirmDelete(data)" v-tooltip.top="$t('message.delete')" />
                </div>
            </template>
        </Column>
    </DataTable>
</template>

<script setup lang="ts">
import { ref, onMounted, defineComponent } from 'vue';
import type { Document } from '@/api/types';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import Toolbar from 'primevue/toolbar';
import FileUpload from 'primevue/fileupload';
import { FilterMatchMode } from '@primevue/core/api';
import { documentApi } from '@/main';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useI18n } from 'vue-i18n';
import handleError from '@/error_handler';

const $t = useI18n().t;
const toast = useToast();
const confirm = useConfirm();

const documents = ref<Document[]>([]);
const filters = ref({ global: { value: null, matchMode: FilterMatchMode.CONTAINS } });
const uploading = ref(false);

function loadList() {
    documentApi.list().then(r => { documents.value = r; }).catch(handleError(toast, $t));
}
onMounted(loadList);

function isImage(doc: Document): boolean {
    return doc.content_type.startsWith('image/');
}

function humanSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function onUpload(event: { files: File | File[] }) {
    const file = Array.isArray(event.files) ? event.files[0] : event.files;
    if (!file) return;
    uploading.value = true;
    documentApi.upload(file).then(() => {
        uploading.value = false;
        toast.add({ severity: 'success', summary: $t('message.success'), detail: $t('admin.documents.uploaded'), life: 2000 });
        loadList();
    }).catch((e) => {
        uploading.value = false;
        handleError(toast, $t, 'admin.documents.upload_failed')(e);
    });
}

function copyLink(doc: Document) {
    navigator.clipboard.writeText(doc.url).then(() => {
        toast.add({ severity: 'success', summary: $t('message.success'), detail: $t('admin.documents.link_copied'), life: 2000 });
    }).catch(() => {
        toast.add({ severity: 'warn', summary: $t('error.title'), detail: doc.url, life: 4000 });
    });
}

function confirmDelete(doc: Document) {
    confirm.require({
        header: $t('admin.documents.delete'),
        message: $t('admin.documents.delete_confirm', { name: doc.filename }),
        icon: 'pi pi-exclamation-triangle',
        acceptProps: { label: $t('admin.delete'), icon: 'pi pi-trash', class: 'p-button-danger p-button' },
        rejectProps: { label: $t('admin.cancel'), icon: 'pi pi-times', class: 'p-button-secondary p-button' },
        accept: () => {
            documentApi.delete(doc.id).then(() => {
                toast.add({ severity: 'success', summary: $t('message.success'), detail: $t('admin.documents.deleted'), life: 2000 });
                loadList();
            }).catch(handleError(toast, $t));
        },
    });
}
</script>

<script lang="ts">
export default defineComponent({ name: 'AdminDocumentsView' });
</script>

<style scoped>
.preview-thumb {
    width: 2.5rem;
    height: 2.5rem;
    object-fit: cover;
    border-radius: 4px;
}
</style>
