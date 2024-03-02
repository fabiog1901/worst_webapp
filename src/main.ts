import { createApp } from "vue";

import "@/index.css";

import { GlobalCmComponent } from "codemirror-editor-vue3";
import InstantSearch from "vue-instantsearch/vue3/es";

import router from "@/router";
import App from "@/App.vue";

import { createPinia } from "pinia";

const pinia = createPinia();

const app = createApp(App);

app.use(InstantSearch);
app.use(GlobalCmComponent);
app.use(pinia);
app.use(router);
app.mount("#app");
