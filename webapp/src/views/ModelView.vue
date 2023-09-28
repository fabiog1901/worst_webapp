<template>
  <div class="flex h-full w-full">
    <section id="context-bar" class="flex w-88">Context bar</section>

    <section
      id="content-container"
      class="flex h-full w-full flex-col bg-gray-300 dark:bg-gray-700"
    >
      <FabTable
        v-bind:data="modelStore.get_filtered_models()"
        v-bind:model="modelStore.worst_models[model_name]['skema']['fields']"
        v-bind:model-default-fields="defaultFields"
        v-on:row-clicked="modelLink($event)"
        v-on:delete-clicked="deleteModel($event)"
        v-on:new-clicked="createNewModel()"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from "vue";

import { useRoute, useRouter } from "vue-router";
import { useModelStore } from "@/stores/modelStore";
import FabTable from "@/components/FabTable.vue";

import type { Model } from "@/types";

const modelStore = useModelStore();

const defaultFields = [
  { name: "id", header: "ID ", visible: false, type: "" },
  { name: "name", header: "Name ", visible: true, type: "" },
  { name: "owned_by", header: "Owner ", visible: true, type: "" },
  { name: "tags", header: "Tags ", visible: true, type: "tag" },
  { name: "updated_by", header: "Updated By ", visible: true, type: "" },
  { name: "updated_at", header: "Last Updated ", visible: true, type: "date" },
  { name: "created_by", header: "Created By ", visible: true, type: "" },
  { name: "created_at", header: "Created At ", visible: true, type: "date" },
];

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

const model_name = computed(() => {
  return route.params.model as string;
});

onMounted(async () => {
  await modelStore.fetch_all_instances(model_name.value);
});

watch(
  () => route.fullPath,
  async () => {
    await modelStore.fetch_all_instances(model_name.value);
  }
);
</script>
