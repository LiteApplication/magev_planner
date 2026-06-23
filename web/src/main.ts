import './assets/main.css'

import App from './App.vue'
import router from './router'
import { createApp } from 'vue';
import PrimeVue, { defaultOptions } from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import Aura from '@primeuix/themes/aura';
import { createI18n } from 'vue-i18n';
import messages from './language';
import { datetimeFormats } from './language';
import Tooltip from 'primevue/tooltip';
import ToastService from 'primevue/toastservice';
import Ripple from 'primevue/ripple';

import AuthApi from './api/auth';
import ShopApi from './api/shop';
import ReservationApi from './api/reservation';
import SlotsApi from './api/slots';
import UsersApi from './api/users';
import SettingsApi from './api/settings';
import NotificationsApi from './api/notifications';
import EnterpriseApi from './api/enterprise';
import DocumentApi from './api/document';
import MailTemplateApi from './api/mailTemplate';



const app = createApp(App);
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: 'system',
        },
        ripple: true,
    },
    locale: {
        ...defaultOptions.locale,
        firstDayOfWeek: 1,        // change to Monday

    },
});
app.use(router)
app.use(ConfirmationService);
app.directive('tooltip', Tooltip);
app.use(ToastService);
app.directive('ripple', Ripple);

const i18n = createI18n({
    legacy: false,
    warnHtmlMessage: false,
    locale: 'fr-FR',
    messages,
    datetimeFormats
});

app.use(i18n);

app.mount('#app')

const authApi: AuthApi = new AuthApi();
const shopApi: ShopApi = new ShopApi();
const reservationApi: ReservationApi = new ReservationApi();
const slotsApi: SlotsApi = new SlotsApi();
const usersApi: UsersApi = new UsersApi();
const settingsApi: SettingsApi = new SettingsApi();
const notificationsApi = new NotificationsApi();
const enterpriseApi = new EnterpriseApi();
const documentApi = new DocumentApi();
const mailTemplateApi = new MailTemplateApi();

export { authApi, shopApi, reservationApi, slotsApi, usersApi, settingsApi, notificationsApi, enterpriseApi, documentApi, mailTemplateApi };
