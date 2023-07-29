import { createApp } from "vue";

import "@/index.css";
import PrimeVue from "primevue/config";
import ToastService from "primevue/toastservice";

import router from "@/router";
import App from "@/App.vue";
import { createPinia } from "pinia";

const pinia = createPinia();

const app = createApp(App);

app.use(PrimeVue, { unstyled: true });
app.use(ToastService);
app.use(pinia).use(router).mount("#app");
