<template>
    <div class="mt-layout">
        <!-- Template list -->
        <aside class="mt-list">
            <button v-for="tpl in templates" :key="tpl.name" class="mt-item" :class="{ active: tpl.name === selectedName }"
                @click="select(tpl.name)">
                <span class="mt-item-name">{{ subjectOrName(tpl) }}</span>
                <Tag v-if="tpl.customized" :value="$t('admin.mail_templates.customized')" severity="warn" />
            </button>
        </aside>

        <!-- Editor -->
        <section class="mt-editor" v-if="current">
            <div class="flex items-center justify-between mb-2 gap-2 flex-wrap">
                <div>
                    <h2 class="text-lg font-semibold">{{ current.subject || current.name }}</h2>
                    <code class="text-xs text-slate-500">{{ current.name }}</code>
                </div>
                <div class="flex gap-2">
                    <Button :label="$t('admin.mail_templates.reset')" icon="pi pi-undo" severity="secondary" outlined
                        @click="confirmReset" :disabled="!current.customized" />
                    <Button :label="$t('admin.mail_templates.test')" icon="pi pi-send" severity="info" outlined
                        @click="testMail" :loading="testing" :disabled="dirty" />
                    <Button :label="$t('message.save')" icon="pi pi-save" @click="save" :loading="saving" :disabled="!dirty" />
                </div>
            </div>

            <div class="flex flex-col gap-1 mb-3">
                <label for="mt-subject" class="text-sm text-slate-500">{{ $t('admin.mail_templates.subject') }}</label>
                <InputText id="mt-subject" v-model="subject" class="w-full" />
            </div>

            <div class="flex items-center gap-2 mb-2 flex-wrap">
                <Select v-model="docToInsert" :options="documents" optionLabel="filename" :placeholder="$t('admin.mail_templates.pick_document')"
                    class="w-72" filter :showClear="true" />
                <Button :label="$t('admin.mail_templates.insert_button')" icon="pi pi-link" size="small" text :disabled="!docToInsert"
                    @click="insertDoc('button')" />
                <Button :label="$t('admin.mail_templates.insert_image')" icon="pi pi-image" size="small" text :disabled="!docToInsert"
                    @click="insertDoc('image')" />
            </div>

            <Textarea ref="editorRef" v-model="content" class="mt-textarea" :autoResize="false" spellcheck="false" />

            <p class="text-xs text-slate-500 mt-2" v-html="$t('admin.mail_templates.syntax_help')"></p>
        </section>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineComponent } from 'vue';
import type { MailTemplate, Document } from '@/api/types';
import Button from 'primevue/button';
import Textarea from 'primevue/textarea';
import InputText from 'primevue/inputtext';
import Select from 'primevue/select';
import Tag from 'primevue/tag';
import { mailTemplateApi, documentApi } from '@/main';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useI18n } from 'vue-i18n';
import handleError from '@/error_handler';

const $t = useI18n().t;
const toast = useToast();
const confirm = useConfirm();

const templates = ref<MailTemplate[]>([]);
const documents = ref<Document[]>([]);
const selectedName = ref<string | null>(null);
const content = ref('');
const subject = ref('');
const saving = ref(false);
const testing = ref(false);
const docToInsert = ref<Document | null>(null);
const editorRef = ref<{ $el: HTMLTextAreaElement } | null>(null);

const current = computed(() => templates.value.find(t => t.name === selectedName.value) ?? null);
const dirty = computed(() => !!current.value && (content.value !== current.value.content || subject.value !== current.value.subject));

function subjectOrName(tpl: MailTemplate): string {
    return tpl.subject || tpl.name;
}

function loadList(keepSelection = false) {
    return mailTemplateApi.list().then(r => {
        templates.value = r;
        if (!keepSelection && r.length && !selectedName.value) select(r[0].name);
    }).catch(handleError(toast, $t));
}

onMounted(() => {
    loadList();
    documentApi.list().then(r => { documents.value = r; }).catch(() => { /* documents optional */ });
});

function select(name: string) {
    selectedName.value = name;
    content.value = current.value?.content ?? '';
    subject.value = current.value?.subject ?? '';
}

function insertDoc(kind: 'button' | 'image') {
    const doc = docToInsert.value;
    if (!doc) return;
    const snippet = kind === 'image'
        ? `![${doc.filename}](${doc.url})`
        : `[[ ${doc.url} | ${doc.filename} ]]`;
    const el = editorRef.value?.$el;
    if (el && typeof el.selectionStart === 'number') {
        const start = el.selectionStart;
        const end = el.selectionEnd;
        content.value = content.value.slice(0, start) + snippet + content.value.slice(end);
    } else {
        content.value += (content.value.endsWith('\n') ? '' : '\n') + snippet;
    }
}

function save() {
    if (!current.value) return;
    saving.value = true;
    mailTemplateApi.update(current.value.name, content.value, subject.value).then((updated) => {
        saving.value = false;
        templates.value = templates.value.map(t => t.name === updated.name ? updated : t);
        subject.value = updated.subject;
        toast.add({ severity: 'success', summary: $t('message.success'), detail: $t('admin.mail_templates.saved'), life: 2000 });
    }).catch((e) => {
        saving.value = false;
        handleError(toast, $t)(e);
    });
}

function confirmReset() {
    if (!current.value) return;
    confirm.require({
        header: $t('admin.mail_templates.reset'),
        message: $t('admin.mail_templates.reset_confirm'),
        icon: 'pi pi-exclamation-triangle',
        acceptProps: { label: $t('admin.mail_templates.reset'), icon: 'pi pi-undo', class: 'p-button-warning p-button' },
        rejectProps: { label: $t('admin.cancel'), icon: 'pi pi-times', class: 'p-button-secondary p-button' },
        accept: () => {
            mailTemplateApi.reset(current.value!.name).then((updated) => {
                templates.value = templates.value.map(t => t.name === updated.name ? updated : t);
                content.value = updated.content;
                subject.value = updated.subject;
                toast.add({ severity: 'success', summary: $t('message.success'), detail: $t('admin.mail_templates.reset_done'), life: 2000 });
            }).catch(handleError(toast, $t));
        },
    });
}

function testMail() {
    if (!current.value) return;
    testing.value = true;
    mailTemplateApi.test(current.value.name).then(() => {
        testing.value = false;
        toast.add({ severity: 'success', summary: $t('message.success'), detail: $t('admin.mail_templates.test_sent'), life: 3000 });
    }).catch((e) => {
        testing.value = false;
        handleError(toast, $t)(e);
    });
}
</script>

<script lang="ts">
export default defineComponent({ name: 'AdminMailTemplatesView' });
</script>

<style scoped>
.mt-layout {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}

.mt-list {
    width: 260px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
    border: 1px solid var(--p-content-border-color);
    border-radius: var(--p-border-radius-md, 6px);
    padding: 0.5rem;
    max-height: 80vh;
    overflow: auto;
}

.mt-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    text-align: left;
    padding: 0.5rem 0.75rem;
    border-radius: var(--p-border-radius-sm, 4px);
    font-size: 0.8rem;
    color: var(--p-text-muted-color);
    background: none;
    border: none;
    cursor: pointer;
}

.mt-item:hover {
    background: var(--p-navigation-item-focus-background);
    color: var(--p-text-color);
}

.mt-item.active {
    background: var(--p-highlight-background);
    color: var(--p-highlight-color);
    font-weight: 600;
}

.mt-item-name {
    flex: 1;
}

.mt-editor {
    flex: 1;
    min-width: 0;
}

.mt-textarea {
    width: 100%;
    min-height: 420px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 0.85rem;
}
</style>
