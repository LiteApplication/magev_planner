<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { ref } from 'vue';
import { defineComponent } from 'vue'

import { useRouter } from 'vue-router';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Checkbox from 'primevue/checkbox';


import { usersApi } from '@/main';

const { t: $t } = useI18n();


const password = ref('');
const confirm_password = ref('');
const accepted_reminder = ref(false);
const error_msg = ref('');
const router = useRouter();
const api_error = ref('');

const token = router.currentRoute.value.params.token as string;
const first_login = (router.currentRoute.value.params.first_setup as string) === 'first_login';

function invalidPassword() {
    if (password.value === '') {
        api_error.value = '';
        error_msg.value = "";
        return false;
    }

    if (password.value.length < 8) {
        api_error.value = '';
        error_msg.value = $t('error.auth.password_too_short');
        return true;
    }

    if (confirm_password.value === '') {
        api_error.value = '';
        error_msg.value = "";
        return false;
    }

    if (confirm_password.value !== password.value) {
        api_error.value = '';
        error_msg.value = $t('error.auth.password_match');
        return true;
    }

    error_msg.value = api_error.value;
    return api_error.value !== '';

}


const onSubmit = async () => {
    if (password.value === '' || confirm_password.value === '') {
        error_msg.value = $t('error.fields');
        return;
    }

    if (password.value !== confirm_password.value) {
        error_msg.value = $t('error.auth.password_match');
        return;
    }

    if (password.value.length < 8) {
        error_msg.value = $t('error.auth.password_too_short');
        return;
    }

    if (first_login && !accepted_reminder.value) {
        error_msg.value = $t('error.auth.reminder_not_accepted');
        return;
    }

    usersApi.resetPassword(token, password.value).then(
        () => {
            console.log('Password reset');
            router.replace({ name: 'login' });
        }
    ).catch(
        error => {
            if (error.response) {
                api_error.value = $t(error.response.data.detail);
                console.log(error.response.data)
            } else {
                api_error.value = $t('error.unknown');
                console.error(error);
            }

        }
    );



};



</script>

<template>
    <div class="register-container">

        <Card class="register-card">
            <template #title>{{ $t("message.password_title_set") }}</template>
            <template #content>
                <div class="fields">


                    <div class="flex flex-col gap-2">
                        <label for="password">{{ $t("message.password") }}</label>
                        <Password v-model="password" :feedback="false" id="new-password" :invalid="invalidPassword()" toggle-mask fluid autofocus
                            pt:pcinput:root:autoComplete="new-password" />
                    </div>

                    <div class="flex flex-col gap-2">
                        <label for="password">{{ $t("message.confirm_password") }}</label>
                        <Password v-model="confirm_password" :feedback="false" id="confirm-password" :invalid="invalidPassword()" fluid toggle-mask
                            @keyup.enter="onSubmit" pt:pcinput:root:autoComplete="new-password" />
                    </div>

                    <div class="flex items-start gap-2 mt-1" v-if="first_login">
                        <Checkbox v-model="accepted_reminder" :binary="true" inputId="accept-reminder" />
                        <label for="accept-reminder" class="text-xs text-justify">{{ $t('message.reminder_confirmation') }}</label>
                    </div>

                </div>

            </template>
            <template #footer>
                <p class=" error" v-if="error_msg != ''"> {{ error_msg }}</p>
                <Button :label="first_login ? $t('message.set_password') : $t('message.reset_password')" @click="onSubmit" />
            </template>
        </Card>
    </div>
</template>

<script lang="ts">



export default defineComponent({
    name: 'ResetPasswordView',
    components: {
        Password,
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

.error {
    color: rgb(255, 81, 81);
    margin-bottom: 1rem;
}
</style>
