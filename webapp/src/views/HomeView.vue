<template>
  <section class="flex">
    <div class="flex w-full">HOMEVIEW</div>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useModelStore } from "@/stores/modelStore";

const modelStore = useModelStore();

onMounted(async () => {
  console.log("homeview-mount");
  modelStore.model_instance_parent_chain = [];
});
</script>
