<template>
  <div class="flex w-16 flex-grow flex-col bg-white shadow-lg dark:bg-gray-900">
    <div id="home" class="sidebar-icon group">
      <router-link to="/"
        ><svg
          id="home-icon"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          class="h-8 w-8"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"
          />
        </svg>
      </router-link>
      <span class="sidebar-tooltip group-hover:scale-100">Home</span>
    </div>

    <hr
      id="linebreaker"
      class="mx-2 rounded-full border border-gray-200 bg-gray-200 dark:border-gray-800 dark:bg-gray-800"
    />

    <div id="sql" class="sidebar-icon group">
      <router-link to="/sql">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          class="h-8 w-8"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="m6.75 7.5 3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0 0 21 18V6a2.25 2.25 0 0 0-2.25-2.25H5.25A2.25 2.25 0 0 0 3 6v12a2.25 2.25 0 0 0 2.25 2.25Z"
          />
        </svg>
      </router-link>
      <span class="sidebar-tooltip group-hover:scale-100">SQL Prompt</span>
    </div>

    <hr
      id="linebreaker"
      class="mx-2 rounded-full border border-gray-200 bg-gray-200 dark:border-gray-800 dark:bg-gray-800"
    />

    <div
      v-for="m in Object.keys(modelStore.models ?? [])"
      id="models"
      v-bind:key="m"
      class="sidebar-icon group"
    >
      <router-link v-bind:to="'/' + m">
        <svg
          id="briefcase-icon"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          class="h-8 w-8"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            v-bind:d="modelStore.models[m].skema.svg_path"
          />
        </svg>
      </router-link>
      <span class="sidebar-tooltip group-hover:scale-100">{{
        m.charAt(0).toUpperCase() + m.slice(1)
      }}</span>
    </div>

    <div id="space-divider" class="flex-grow"></div>

    <hr
      id="linebreaker"
      class="mx-2 rounded-full border border-gray-200 bg-gray-200 dark:border-gray-800 dark:bg-gray-800"
    />

    <div id="admin" class="sidebar-icon group">
      <router-link to="/admin">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          class="h-8 w-8"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z"
          />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      </router-link>
      <span class="sidebar-tooltip group-hover:scale-100">Admin</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useModelStore } from "@/stores/modelStore";

const modelStore = useModelStore();

onMounted(async () => {
  await modelStore.get_all_models();
});
</script>

<style scoped>
.sidebar-icon {
  @apply relative mx-auto mb-2 mt-2 
      flex h-12 w-12 cursor-pointer items-center  
    justify-center rounded-3xl bg-gray-400 
    text-green-500 shadow-lg
      transition-all duration-300
      ease-linear hover:rounded-xl hover:bg-green-600
      hover:text-white dark:bg-gray-800;
}

.sidebar-tooltip {
  @apply absolute left-14 m-2 w-auto min-w-max origin-left scale-0 rounded-md
      bg-gray-900 p-2 
      text-xs font-bold 
      text-white shadow-md transition-all duration-100;
}
</style>
