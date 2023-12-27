<template>
  <div class="flex h-full w-full">
    <section id="context-bar" class="flex w-88">Context bar</section>

    <section
      id="content-container"
      class="flex h-full w-full flex-col bg-gray-300 dark:bg-gray-700"
    >
      <FabTable
        v-bind:data="modelStore.get_filtered_models()"
        v-bind:model-fields="modelStore.models[model_name]['skema']['fields']"
        v-bind:model-default-fields="modelDefaultFields"
        v-on:row-clicked="modelLink($event)"
        v-on:delete-clicked="delete_instance($event)"
        v-on:new-clicked="showModal = true"
      />
      <div
        v-if="showModal"
        class="fixed left-0 top-0 z-10 flex h-full w-full items-center justify-center"
      >
        <div
          class="absolute h-full w-full bg-gray-900 opacity-50"
          v-on:click="showModal = false"
        ></div>

        <div class="absolute max-h-full max-w-xl">
          <div class="container overflow-hidden bg-white md:rounded">
            <div
              class="flex select-none items-center justify-between border-b bg-gray-100 px-4 py-4 text-sm font-medium leading-none"
            >
              <h3>New {{ model_name }}</h3>
              <div
                class="cursor-pointer text-2xl hover:text-gray-600"
                v-on:click="showModal = false"
              >
                &#215;
              </div>
            </div>

            <div class="max-h-full px-4 py-4">
              <p class="text-gray-800">Enter JSON string</p>
              <textarea
                id=""
                v-model="m_json"
                class="rounded-md border-2 border-gray-500"
                name=""
                cols="30"
                rows="10"
              ></textarea>

              <div class="mt-4 text-right">
                <button
                  class="px-4 py-2 text-sm text-gray-600 hover:underline focus:outline-none"
                  v-on:click="showModal = false"
                >
                  Cancel
                </button>
                <button
                  class="mr-2 rounded bg-green-500 px-4 py-2 text-sm text-white hover:bg-green-400 focus:outline-none"
                  v-on:click="create_instance"
                >
                  Create
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch, ref, onBeforeUnmount } from "vue";

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
  {
    name: "attachments",
    in_overview: false,
    type: "list",
  },
];

// "store.worst_models[model_name]['skema']['fields']"
const router = useRouter();
const route = useRoute();
const showModal = ref(false);
const m_json = ref("");

const delete_instance = (m: Model) => {
  modelStore.delete_instance(model_name.value, m.id);
  console.log(`delete model: ${model_name.value}/${m.id}`);
};

const create_instance = () => {
  console.log(`create model: ${m_json.value}`);
  modelStore.create_instance(model_name.value, m_json.value);
  showModal.value = false;
};

const modelLink = (m: Model) => {
  router.push(`/${model_name.value}/${m.id}`);
};

const model_name = computed(() => {
  return route.params.model as string;
});

const formatDate = (value: string) => {
  if (value) {
    return new Date(value).toDateString();
  }

  return "";
};

onMounted(async () => {
  console.log("modelview-mount", model_name.value);
  await modelStore.get_all_instances(model_name.value);
  modelStore.instance_parent_chain = [
    [
      model_name.value,
      "",
      `${
        model_name.value.charAt(0).toUpperCase() + model_name.value.slice(1)
      } Overview`,
    ],
  ];
});

watch(
  () => route.fullPath,
  async () => {
    if (route.params.model && !route.params.id) {
      console.info("modelview-watch", model_name.value);
      await modelStore.get_all_instances(model_name.value);
      modelStore.instance_parent_chain = [
        [
          model_name.value,
          "",
          `${
            model_name.value.charAt(0).toUpperCase() + model_name.value.slice(1)
          } Overview`,
        ],
      ];
    }
  }
);

const onEscape = (e: any) => {
  if (e.key === "Esc" || e.key === "Escape") {
    showModal.value = false;
  }
};

document.addEventListener("keydown", onEscape);

onBeforeUnmount(() => {
  document.removeEventListener("keydown", onEscape);
});
</script>
