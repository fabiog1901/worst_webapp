<template>
  <div class="flex h-full w-full">
    <section id="context-bar" class="flex w-88">Context bar</section>

    <section
      id="content-container"
      class="flex h-full w-full flex-col bg-gray-300 dark:bg-gray-700"
    >
      <FabTable
        v-bind:data="modelStore.get_filtered_models()"
        v-bind:model-fields="getSkemaFields"
        v-bind:model-default-fields="modelDefaultFields"
        v-on:row-clicked="modelLink($event)"
        v-on:delete-clicked="confirm_delete_instance($event)"
        v-on:new-clicked="create_instance_modal"
      />
      <div
        v-if="showCreateNewInstanceModal"
        class="fixed left-0 top-0 z-10 flex h-full w-full items-center justify-center"
      >
        <div
          class="absolute h-full w-full bg-gray-900 opacity-50"
          v-on:click="showCreateNewInstanceModal = false"
        ></div>

        <div class="absolute h-4/5 w-2/3 bg-yellow-500">
          <div
            class="container h-full w-full overflow-y-scroll bg-white md:rounded dark:bg-slate-600"
          >
            <div
              class="flex select-none items-center justify-between border-b bg-gray-100 px-4 py-4 text-sm font-medium leading-none dark:bg-gray-700 dark:text-white"
            >
              <h3>New {{ model_name }}</h3>
              <div
                class="cursor-pointer text-2xl hover:text-gray-600"
                v-on:click="showCreateNewInstanceModal = false"
              >
                &#215;
              </div>
            </div>

            <div class="max-h-full px-4 py-4">
              <div class="w-96 flex-1 bg-gray-300 dark:bg-gray-700">
                <div class="p-2 text-sm text-gray-700 dark:text-white">
                  name
                </div>
                <div
                  class="bg-slate-300 p-2 text-xl font-semibold dark:bg-slate-500"
                >
                  <input
                    v-model="m_json['name']"
                    type="text"
                    placeholder="account_1"
                  />
                </div>
                <div v-for="x in modelBaseFields" v-bind:key="x">
                  <div class="p-2 text-sm text-gray-700 dark:text-white">
                    {{ x.name }} <i>[{{ x.type }}]</i>
                  </div>
                  <div
                    v-if="x.type === 'decimal'"
                    class="h-12 bg-slate-300 p-2 text-black dark:bg-slate-500"
                  >
                    <input v-model="m_json[x.name]" type="text" />
                  </div>
                  <div
                    v-else-if="x.type === 'date'"
                    class="h-12 bg-slate-300 p-2 dark:bg-slate-500"
                  >
                    <input v-model="m_json[x.name]" type="text" />
                  </div>
                  <div
                    v-else-if="x.type === 'enum'"
                    class="h-12 bg-slate-300 p-2 dark:bg-slate-500"
                  >
                    <input v-model="m_json[x.name]" type="text" />
                  </div>
                  <div
                    v-else-if="x.type === 'markdown'"
                    class="max-h-80 w-full overflow-y-scroll p-2 dark:bg-slate-500"
                  >
                    <input v-model="m_json[x.name]" type="text" />
                  </div>

                  <div v-else class="h-12 bg-slate-300 p-2 dark:bg-slate-500">
                    <input v-model="m_json[x.name]" type="text" />
                  </div>
                </div>

                <div class="p-2 text-sm text-gray-700 dark:text-white">
                  id <i>[uuid]</i>
                </div>
                <div class="h-12 bg-slate-300 p-2 dark:bg-slate-500">
                  <input type="text" />
                </div>
              </div>

              <div class="mt-4 text-right">
                <button
                  class="px-4 py-2 text-sm text-gray-600 hover:underline focus:outline-none"
                  v-on:click="showCreateNewInstanceModal = false"
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
  <div
    v-if="showDeleteInstanceModal"
    class="fixed left-0 top-0 z-10 flex h-full w-full items-center justify-center"
  >
    <div
      class="absolute h-full w-full bg-gray-900 opacity-50"
      v-on:click="showDeleteInstanceModal = false"
    ></div>

    <div class="absolute max-h-full max-w-xl">
      <div class="container overflow-hidden bg-white md:rounded">
        <div
          class="flex select-none items-center justify-between border-b bg-gray-100 px-4 py-4 text-sm font-medium leading-none"
        >
          <h3 class="text-2xl">Delete {{ model_name }}</h3>
          <div
            class="cursor-pointer text-2xl hover:text-gray-600"
            v-on:click="showDeleteInstanceModal = false"
          >
            &#215;
          </div>
        </div>

        <div class="max-h-full px-4 py-4">
          <p class="text-gray-800">
            Are you sure you want to delete {{ model_name }}:
            <span class="font-semibold">{{ instance_name }}</span>
            ?
          </p>

          <div class="mt-4 text-right">
            <button
              class="px-4 py-2 text-sm text-gray-600 hover:underline focus:outline-none"
              v-on:click="showDeleteInstanceModal = false"
            >
              Cancel
            </button>
            <button
              class="mr-2 rounded bg-red-500 px-4 py-2 text-sm text-white hover:bg-red-400 focus:outline-none"
              v-on:click="delete_instance"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
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
const showCreateNewInstanceModal = ref(false);
const showDeleteInstanceModal = ref(false);
const m_json = ref<{ [key: string]: any }>({});
const id = ref("");
const instance_name = ref("");
// const delete_instance = async (m: Model) => {
//   modelStore.delete_instance(model_name.value, m.id);
//   await modelStore.get_all_instances(model_name.value);
// };

const confirm_delete_instance = (m: Model) => {
  showDeleteInstanceModal.value = true;
  id.value = m.id;
  instance_name.value = m.name;
};
const create_instance_modal = () => {
  showCreateNewInstanceModal.value = true;
  m_json.value["name"] = ref();
  for (const x of modelBaseFields.value) {
    m_json.value[x.name] = ref(null);
  }
};

const delete_instance = async () => {
  showDeleteInstanceModal.value = false;

  await modelStore.delete_instance(model_name.value, id.value);

  // refresh list
  await modelStore.get_all_instances(model_name.value);
};

const create_instance = async () => {
  const f: { [key: string]: any } = {};
  f.name = m_json.value.name;
  for (const x of modelBaseFields.value) {
    f[x.name] = m_json.value[x.name];
  }

  const i = await modelStore.create_instance(
    model_name.value,
    JSON.stringify(f)
  );
  showCreateNewInstanceModal.value = false;
  console.log(i.id);
  router.push(`/${model_name.value}/${i.id}`);
};

const modelLink = (m: Model) => {
  router.push(`/${model_name.value}/${m.id}`);
};

const model_name = computed(() => {
  return route.params.model as string;
});

const getSkemaFields = computed(() => {
  if (modelStore.models[model_name.value])
    return modelStore.models[model_name.value]["skema"]["fields"];
  return [];
});

const modelBaseFields = computed(() => {
  return [
    { name: "id", type: "" },
    { name: "name", type: "" },
    { name: "owned_by", type: "" },
    { name: "tags", type: "tag" },
    { name: "parent_id", type: "string" },
    { name: "parent_type", type: "string" },
    { name: "permissions", type: "string" },
  ].concat(getSkemaFields.value);
});

onMounted(async () => {
  console.log("tableview-onMounted", model_name.value);
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
    showCreateNewInstanceModal.value = false;
  }
};

document.addEventListener("keydown", onEscape);

onBeforeUnmount(() => {
  document.removeEventListener("keydown", onEscape);
});
</script>
