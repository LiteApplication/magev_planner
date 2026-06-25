<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { computed, onMounted, ref, watch } from 'vue';
import { defineComponent } from 'vue'
import { useRoute } from 'vue-router';

import InputText from 'primevue/inputtext';
import Select from 'primevue/select';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Checkbox from 'primevue/checkbox';

import type { EnterprisePublic } from '@/api/types';
import { authApi, enterpriseApi } from '@/main';

const { t: $t } = useI18n();
const route = useRoute();

const email = ref('');
const full_name = ref('');
const phone = ref('');
const error_msg = ref('');
const accepted_terms = ref(false);
const accepted_privacy = ref(false);

const enterprises = ref<EnterprisePublic[]>([]);
const selected = ref<EnterprisePublic | null>(null);

const loading = ref(false);
const mail_sent = ref(false);

// When the route carries a slug, the enterprise is locked and the dropdown is hidden.
const lockedSlug = computed(() => (route.params.slug as string | undefined) || null);
const isLocked = computed(() => lockedSlug.value !== null && selected.value !== null);

function parseDomains(raw: string): string[] {
    return raw.replace(/,/g, ' ').split(/\s+/).map(d => d.trim().replace(/^@/, '').toLowerCase()).filter(Boolean);
}

function matchesEmail(ent: EnterprisePublic, mail: string): boolean {
    const domains = parseDomains(ent.email_domains);
    if (domains.length === 0) return true;
    const emailDomain = mail.trim().toLowerCase().split('@').pop() || '';
    return domains.some(d => emailDomain === d || emailDomain.endsWith('.' + d));
}

onMounted(async () => {
    try {
        enterprises.value = await enterpriseApi.listPublic();
    } catch {
        error_msg.value = $t('error.unknown');
        return;
    }
    if (lockedSlug.value) {
        selected.value = enterprises.value.find(e => e.slug === lockedSlug.value) ?? null;
        if (!selected.value) error_msg.value = $t('error.auth.enterprise_invalid');
    }
});

// Auto-detect the enterprise from the typed email (unless locked by slug).
watch(email, (mail) => {
    if (lockedSlug.value) return;
    if (selected.value && matchesEmail(selected.value, mail)) return;
    const match = enterprises.value.find(e => parseDomains(e.email_domains).length > 0 && matchesEmail(e, mail));
    if (match) selected.value = match;
});

// Reset the consent checkbox whenever the enterprise changes.
watch(selected, () => { accepted_terms.value = false; });

const emailMismatch = computed(() =>
    !!selected.value && !!email.value && !matchesEmail(selected.value, email.value)
);

const onSubmit = async () => {
    if (email.value === '' || full_name.value === '' || phone.value === '' || !selected.value) {
        error_msg.value = $t('error.fields');
        return;
    }
    if (emailMismatch.value) {
        error_msg.value = $t('error.auth.email_domain_mismatch');
        return;
    }
    if (selected.value.checkbox_text && !accepted_terms.value) {
        error_msg.value = $t('error.auth.terms_not_accepted');
        return;
    }
    if (!accepted_privacy.value) {
        error_msg.value = $t('error.auth.privacy_not_accepted');
        return;
    }
    loading.value = true;
    authApi.register(email.value, full_name.value, phone.value, selected.value.slug, accepted_terms.value).then(
        () => {
            error_msg.value = '';
            loading.value = false;
            mail_sent.value = true;
        }
    ).catch(
        error => {
            if (error.response) {
                error_msg.value = $t(error.response.data.detail);
            } else {
                error_msg.value = $t('error.unknown');
                console.error(error);
            }
            loading.value = false;
        }
    );
};
</script>

<template>
    <div class="register-container">
        <Card class="register-card">
            <template #title>{{ $t("message.register") }}</template>
            <template #content>
                <div v-if="mail_sent">
                    <p>{{ $t("message.mail_sent") }}</p>
                </div>
                <div class="fields" v-else>
                    <div class="flex flex-col gap-2">
                        <label for="email">{{ $t("message.email") }}</label>
                        <InputText id="email" v-model="email" autocomplete="email" />
                    </div>
                    <div class="flex flex-col gap-2">
                        <label for="full_name">{{ $t("message.full_name") }}</label>
                        <InputText id="full_name" v-model="full_name" autocomplete="name" />
                    </div>
                    <div class="flex flex-col gap-2">
                        <label for="phone">{{ $t("message.phone") }}</label>
                        <InputText id="phone" v-model="phone" type="tel" autocomplete="tel" />
                    </div>

                    <div class="flex flex-col gap-2" v-if="isLocked">
                        <label>{{ $t("message.group") }}</label>
                        <div class="locked-enterprise">{{ selected?.name }}</div>
                    </div>
                    <div class="flex flex-col gap-2" v-else>
                        <label for="group">{{ $t("message.group") }}</label>
                        <Select v-model="selected" inputId="group" :options="enterprises" optionLabel="name"
                            class="w-full" :placeholder="$t('message.group')" />
                    </div>

                    <p v-if="emailMismatch" class="warn">{{ $t('error.auth.email_domain_mismatch') }}</p>

                    <div class="flex items-start gap-2 mt-1" v-if="selected?.checkbox_text">
                        <Checkbox v-model="accepted_terms" :binary="true" inputId="accept-terms" />
                        <label for="accept-terms" class="text-sm">{{ selected.checkbox_text }}</label>
                    </div>

                    <div class="flex items-start gap-2 mt-1">
                        <Checkbox v-model="accepted_privacy" :binary="true" inputId="accept-privacy" />
                        <label for="accept-privacy" class="text-xs text-justify">{{ $t('message.privacy_consent') }}</label>
                    </div>
                </div>
            </template>
            <template #footer>
                <p class="error" v-if="error_msg != ''"> {{ error_msg }}</p>
                <div class="flex gap-4 mt-1" v-if="!mail_sent">
                    <Button v-bind:label="$t('message.to_login')" severity="secondary" outlined class="w-2/3"
                        v-on:click="$router.replace({ name: 'login' })" />
                    <Button v-bind:label="$t('message.register')" class="w-1/3" v-on:click="onSubmit" :loading="loading" :disabled="loading" />
                </div>
            </template>
        </Card>
    </div>
</template>

<script lang="ts">
export default defineComponent({
    name: 'RegisterView',
    components: {
        InputText,
        // eslint-disable-next-line vue/no-reserved-component-names
        Button,
        Card,
    },
});
</script>

<style scoped>
.register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

.register-card {
    padding: 1.5rem;
    width: 30rem;
}

@media (max-width: 768px) {
    .register-card {
        width: 100%;
    }
}

.p-field {
    margin-top: 1.6 rem;
}

.locked-enterprise {
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--p-content-border-color);
    border-radius: var(--p-border-radius-md, 6px);
    background: var(--p-content-background);
    font-weight: 600;
}

.warn {
    color: #d97706;
    font-size: 0.85rem;
}

.error {
    color: rgb(255, 81, 81);
}
</style>
