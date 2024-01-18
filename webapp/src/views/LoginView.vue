<template>
  <section
    class="align-center flex h-screen flex-col justify-center bg-slate-300 dark:bg-slate-700"
  >
    <div
      class="m-8 flex justify-center text-5xl font-semibold text-gray-700 dark:text-gray-200"
    >
      Worst
    </div>
    <div class="flex justify-center">
      <div
        class="h-16 w-fit cursor-pointer rounded-lg bg-slate-500 p-4 text-center text-2xl text-white hover:bg-slate-400"
        v-on:click="sso_login"
      >
        Login with SSO
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/authStore";

const authStore = useAuthStore();

const sso_login = () => {
  authStore.get_auth_code_url();
};
</script>
