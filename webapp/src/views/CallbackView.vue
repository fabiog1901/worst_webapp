<template>
  <section></section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/authStore";

const authStore = useAuthStore();
const route = useRoute();

onMounted(async () => {
  authStore.get_token(route.query.code as string);
});
</script>
