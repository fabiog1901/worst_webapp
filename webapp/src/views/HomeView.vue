<template>
  <section class="flex flex-grow bg-gray-300 dark:bg-gray-500 dark:text-white">
    <div class="flex w-full">HOMEVIEW</div>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useModelStore } from "@/stores/modelStore";

const modelStore = useModelStore();

onMounted(async () => {
  modelStore.instance_parent_chain = [];
});
</script>
