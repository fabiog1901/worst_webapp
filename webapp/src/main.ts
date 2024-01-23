import { createApp } from "vue";

import "@/index.css";
import "instantsearch.css/themes/algolia-min.css";

import PrimeVue from "primevue/config";
import ToastService from "primevue/toastservice";
import { GlobalCmComponent } from "codemirror-editor-vue3";
import InstantSearch from "vue-instantsearch/vue3/es";

import router from "@/router";
import App from "@/App.vue";

import { createPinia } from "pinia";

const pinia = createPinia();

const app = createApp(App);

app.use(PrimeVue, { unstyled: true });
app.use(ToastService);
app.use(InstantSearch);
app.use(GlobalCmComponent);
app.use(pinia).use(router).mount("#app");
