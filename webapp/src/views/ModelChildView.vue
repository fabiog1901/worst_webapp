<template>
  <div class="flex h-full w-full">
    <section id="context-bar" class="flex w-88">Context bar</section>

    <section
      id="content-container"
      class="flex h-full w-full flex-col bg-gray-300 dark:bg-gray-700"
    >
      <div class="m-2 text-3xl dark:text-slate-300">
        {{ titleCase(model_name) }}
        <b> {{ modelStore.model_instance.name }}</b> -
        {{ titleCase(child_model_name) }} List
      </div>
      <FabTable
        v-bind:data="modelStore.get_filtered_models()"
        v-bind:model-fields="
          modelStore.worst_models[model_name]['skema']['fields']
        "
        v-bind:model-default-fields="modelDefaultFields"
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

const modelDefaultFields = [
  { name: "id", in_overview: false, type: "" },
  { name: "name", in_overview: true, type: "" },
  { name: "owned_by", in_overview: true, type: "" },
  { name: "tags", in_overview: true, type: "tag" },
  { name: "updated_by", in_overview: false, type: "" },
  {
    name: "updated_at",
    in_overview: false,
    type: "date",
  },
  { name: "created_by", header: "Created By ", in_overview: false, type: "" },
  {
    name: "created_at",
    in_overview: false,
    type: "date",
  },
];

// "store.worst_models[model_name]['skema']['fields']"
const router = useRouter();
const route = useRoute();

const createNewModel = () => {
  console.log(
    `new model ${child_model_name.value} under ${model_name.value}/${id.value}`
  );
};

const deleteModel = (m: Model) => {
  console.log(`delete model: ${child_model_name.value}/${m.id}`);
};

const modelLink = (m: Model) => {
  router.push(`/${child_model_name.value}/${m.id}`);
};

const model_name = computed(() => {
  return route.params.model as string;
});

const id = computed(() => {
  return route.params.id as string;
});

const child_model_name = computed(() => {
  return route.params.child_model_name as string;
});

onMounted(async () => {
  console.log("modelchildview-mount", model_name.value, child_model_name.value);
  await modelStore.fetch_instance_children_for_model(
    model_name.value,
    id.value,
    child_model_name.value
  );
  modelStore.model_instance_parent_chain.push([
    child_model_name.value,
    "",
    `${
      child_model_name.value.charAt(0).toUpperCase() +
      child_model_name.value.slice(1)
    } List`,
  ]);
});

watch(
  () => route.fullPath,
  async () => {
    if (route.params.model && !route.params.id) {
      console.info("modelchildview-watch", model_name.value);
      await modelStore.fetch_instance_children_for_model(
        model_name.value,
        id.value,
        child_model_name.value
      );
      modelStore.model_instance_parent_chain.push([
        child_model_name.value,
        "",
        `${
          child_model_name.value.charAt(0).toUpperCase() +
          child_model_name.value.slice(1)
        } List`,
      ]);
    }
  }
);

const titleCase = (s: string) =>
  s
    .replace(/^[-_]*(.)/, (_, c) => c.toUpperCase()) // Initial char (after -/_)
    .replace(/[-_]+(.)/g, (_, c) => "_" + c.toUpperCase()); // First char after each -/_
</script>
