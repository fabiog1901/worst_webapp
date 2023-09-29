<template>
  <div class="flex h-full w-full">
    <section id="context-bar" class="flex w-88">Context bar</section>

    <section
      id="content-container"
      class="flex h-full w-full flex-col bg-gray-300 dark:bg-gray-700"
    >
      Modelname: {{ model_name }} <br />id: {{ id }}
      <br />
      <br />
      {{ modelStore.model_instance }}
      <br />
      <br />
      {{ modelStore.model_instance_children }}
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from "vue";

import { useRoute, useRouter } from "vue-router";
import { useModelStore } from "@/stores/modelStore";

import type { Model } from "@/types";

const modelStore = useModelStore();

// "store.worst_models[model_name]['skema']['fields']"
const router = useRouter();
const route = useRoute();

const createNewModel = () => {
  console.log(`new model ${model_name.value}`);
};

const deleteModel = (m: Model) => {
  console.log(`delete model: ${model_name.value}/${m.id}`);
};

const modelLink = (m: Model) => {
  router.push(`/${model_name.value}/${m.id}`);
};

const id = computed(() => {
  return route.params.id as string;
});

const model_name = computed(() => {
  return route.params.model as string;
});

onMounted(async () => {
  await modelStore.fetch_instance(model_name.value, id.value);
  await modelStore.fetch_instance_children(model_name.value, id.value);
});

watch(
  () => route.fullPath,
  async () => {
    if (id.value) {
      console.log("watch", id.value, route.params.id);
      await modelStore.fetch_instance(model_name.value, id.value);
      await modelStore.fetch_instance_children(model_name.value, id.value);
    }
  }
);
</script>
