<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { ref } from 'vue';
import { defineComponent } from 'vue'

import { useRouter } from 'vue-router';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Dialog from 'primevue/dialog';


import { authApi } from '@/main';

const { t: $t } = useI18n();


const email = ref('');
const password = ref('');
const error_msg = ref('');
const router = useRouter();

const forgotPasswordVisible = ref(false);
const forgotPasswordEmail = ref('');
const forgotPasswordSent = ref(false);
const forgotPasswordLoading = ref(false);

const onSubmit = async () => {
    if (email.value === '' || password.value === '') {
        error_msg.value = $t('error.fields');
        return;
    }
    authApi.login(email.value, password.value).then(
        () => {
            if (router.currentRoute.value.query.redirect) {
                router.replace(router.currentRoute.value.query.redirect as string);
            } else {
                router.replace({ name: 'reservations' });
            }
        }
    ).catch(
        error => {
            if (error.response) {

                error_msg.value = $t(error.response.data.detail);
                password.value = '';
                console.log(error.response.data)
            } else {
                error_msg.value = $t('error.unknown');
                console.error(error);
            }

        }
    );
};

const openForgotPassword = () => {
    forgotPasswordEmail.value = email.value;
    forgotPasswordSent.value = false;
    forgotPasswordVisible.value = true;
};

const onForgotPasswordSubmit = async () => {
    if (forgotPasswordEmail.value === '') {
        return;
    }
    forgotPasswordLoading.value = true;
    try {
        await authApi.forgotPassword(forgotPasswordEmail.value);
    } catch (error) {
        console.error(error);
    } finally {
        // Always report success, regardless of outcome, to avoid leaking
        // whether an account exists for this email or is rate limited.
        forgotPasswordLoading.value = false;
        forgotPasswordSent.value = true;
    }
};



</script>

<template>
    <div class="login-container">

        <Card class="login-card">
            <template #title>{{ $t("message.login") }}</template>
            <template #content>
                <div class="fields">

                    <div class="flex flex-col gap-2">
                        <label for="email">{{ $t("message.email") }}</label>
                        <InputText id="email" v-model="email" autocomplete="email" />
                    </div>

                    <div class="flex flex-col gap-2">
                        <label for="password">{{ $t("message.password") }}</label>
                        <Password v-model="password" :feedback="false" id="password" autocomplete="current-password" />
                    </div>

                    <Button v-bind:label="$t('message.forgot_password')" severity="secondary" text
                        class="self-start p-0" v-on:click="openForgotPassword" />
                </div>

            </template>
            <template #footer>
                <p class="error" v-if="error_msg != '' && password == ''"> {{ error_msg }}</p>
                <div class="flex gap-4 mt-1">
                    <Button v-bind:label="$t('message.to_register')" severity="secondary" outlined class="w-2/3"
                        v-on:click="$router.replace({ name: 'register' })" />
                    <Button v-bind:label="$t('message.login')" class="w-1/3" v-on:click="onSubmit" />
                </div>
            </template>
        </Card>

        <Dialog v-model:visible="forgotPasswordVisible" modal :header="$t('message.forgot_password')"
            class="w-[25rem] max-w-full">
            <p v-if="forgotPasswordSent">{{ $t('message.forgot_password_sent') }}</p>
            <div v-else class="flex flex-col gap-2">
                <label for="forgot-email">{{ $t("message.email") }}</label>
                <InputText id="forgot-email" v-model="forgotPasswordEmail" autocomplete="email"
                    v-on:keyup.enter="onForgotPasswordSubmit" />
                <Button v-bind:label="$t('message.reset_password')" class="mt-2" :loading="forgotPasswordLoading"
                    v-on:click="onForgotPasswordSubmit" />
            </div>
        </Dialog>
    </div>
</template>

<script lang="ts">



export default defineComponent({
    name: 'LoginView',
    components: {
        InputText,
        Password,
        // eslint-disable-next-line vue/no-reserved-component-names
        Button,
        Card,
        Dialog,
    },
});
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

.login-card {
    padding: 1.5rem;
    width: 30rem;
}

@media (max-width: 768px) {
    .login-card {
        width: 100%;
    }
}

.p-field {
    margin-top: 1.6 rem;
}

.error {
    color: rgb(255, 81, 81);
}
</style>
