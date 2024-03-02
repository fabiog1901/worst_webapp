<template>
  <head>
    <meta charset="utf-8" />

    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/@meilisearch/instant-meilisearch/templates/basic_search.css"
    />
  </head>
  <section
    class="flex h-14 w-full flex-row items-center bg-gray-300 p-2 dark:bg-gray-800"
  >
    <FabBreadcrumb
      id="left-div"
      class="flex-1"
      v-bind:chain="modelStore.instance_parent_chain ?? []"
      v-bind:worst-models="modelStore.models ?? {}"
      v-on:clicked="routerLinker($event)"
    />
    <ais-instant-search
      id="center-div"
      class="flex-1"
      v-bind:search-client="customSearchClient"
      index-name="worst"
    >
      <ais-search-box
        placeholder="Search..."
        reset-title="Remove the query"
        v-on:focus="open_ais_hits = true"
      ></ais-search-box>
      <div
        v-if="open_ais_hits"
        class="fixed left-0 top-0 z-10 flex h-full w-full items-center justify-center"
      >
        <div
          class="absolute h-full w-full"
          v-on:click="open_ais_hits = false"
        ></div>
      </div>
      <ais-hits v-if="open_ais_hits">
        <template v-slot:item="{ item }">
          <ais-highlight
            class="font-bold text-xl hover:cursor-pointer hover:underline"
            v-bind:hit="item"
            attribute="name"
            v-on:click="routerSearchLinker(item.comp_id)"
          ></ais-highlight>
          <br />
          <div
            v-for="k in Object.keys(item).filter((x) => {
              return (
                [
                  'comp_id',
                  'name',
                  'parent_type',
                  'parent_id',
                  'permissions',
                  '_highlightResult',
                  '_snippetResult',
                  '__position',
                ].indexOf(x) === -1
              );
            })"
          >
            <div v-if="item[k] && Array.isArray(item[k]) && item[k].length > 0">
              <label
                class="font-semibold hover:cursor-pointer hover:underline"
                v-on:click="routerSearchLinker(item.comp_id)"
                >{{ k }}:
              </label>
              <div v-for="i in item[k]" v-bind:key="i" class="flex">
                <div
                  class="hover:cursor-pointer hover:underline"
                  v-on:click="routerSearchLinker(item.comp_id)"
                >
                  - {{ i }}
                </div>
              </div>
            </div>
            <div v-if="item[k] && !Array.isArray(item[k])">
              <label
                class="font-semibold hover:cursor-pointer hover:underline"
                v-on:click="routerSearchLinker(item.comp_id)"
                >{{ k }}:
              </label>
              <ais-snippet
                v-bind:attribute="k"
                class="hover:cursor-pointer hover:underline"
                v-bind:hit="item"
                v-on:click="routerSearchLinker(item.comp_id)"
              ></ais-snippet>
            </div>
          </div>
        </template>
      </ais-hits>
      <ais-configure v-bind:attributes-to-snippet.camel="['text:50']" />
    </ais-instant-search>
    <div id="right-div" class="flex flex-1 flex-row items-center">
      <div class="flex-grow"></div>
      <div id="dark-theme" class="top-navigation-icon" v-on:click="toggleTheme">
        <svg
          v-if="userTheme === 'dark'"
          id="sun-icon"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="h-6 w-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z"
          />
        </svg>

        <svg
          v-else
          id="moon-icon"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="h-6 w-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z"
          />
        </svg>
      </div>
      <div class="top-navigation-icon">
        <svg
          id="bell-icon"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="h-6 w-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0"
          />
        </svg>
      </div>
      <div class="top-navigation-icon" v-on:click="authStore.logout">
        <svg
          id="user-circle-icon"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="h-6 w-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      </div>
      <div class="top-navigation-icon">
        {{ authStore.fullname }}
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useAuthStore } from "@/stores/authStore";
import { useModelStore } from "@/stores/modelStore";
import FabBreadcrumb from "@/components/FabBreadcrumb.vue";
import { useRouter } from "vue-router";
import { instantMeiliSearch } from "@meilisearch/instant-meilisearch";

const userTheme = ref("light");
const authStore = useAuthStore();
const modelStore = useModelStore();
const router = useRouter();
const open_ais_hits = ref(false);

const customSearchClient = instantMeiliSearch(
  `${import.meta.env.VITE_APP_API_URL}/search`,
  authStore.access_token,
).searchClient;

onMounted(() => {
  const initUserTheme = getTheme() || getMediaPreference();
  setTheme(initUserTheme);
});

const toggleTheme = () => {
  const activeTheme = localStorage.getItem("user-theme");
  if (activeTheme === "dark") {
    setTheme("light");
  } else {
    setTheme("dark");
  }
};

const getTheme = () => {
  return localStorage.getItem("user-theme");
};

const setTheme = (theme: string) => {
  localStorage.setItem("user-theme", theme);
  userTheme.value = theme;
  document.documentElement.className = theme;
};

const getMediaPreference = () => {
  const hasDarkPreference = window.matchMedia(
    "(prefers-color-scheme: dark)",
  ).matches;
  if (hasDarkPreference) {
    return "dark";
  } else {
    return "light";
  }
};

const routerLinker = (x: Array<any>) => {
  if (x.length == 1) {
    router.push(`/${x[0]}`);
  } else {
    router.push(`/${x[0]}/${x[1]}`);
  }
};

const routerSearchLinker = (x: string) => {
  const comp_id = x.split("_");
  open_ais_hits.value = false;
  router.push(`/${comp_id[0]}/${comp_id[1]}`);
};
</script>

<style scoped>
.top-navigation-icon {
  @apply mx-3 cursor-pointer
      text-gray-600 transition duration-300 ease-in-out 
      hover:text-pink-400 dark:text-gray-400 
      dark:hover:text-pink-400;
}
</style>
