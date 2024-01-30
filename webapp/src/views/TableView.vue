<template>
  <div class="flex h-full w-full">
    <section
      id="context-bar"
      class="flex w-88 bg-gray-300 dark:bg-gray-500 dark:text-white"
    >
      Context bar
    </section>

    <section
      id="content-container"
      class="flex h-full w-full flex-col bg-gray-300 dark:bg-gray-700"
    >
      <FabTable
        v-bind:data="modelStore.get_filtered_models()"
        v-bind:model-fields="
          modelStore.models[model_name]
            ? modelStore.models[model_name]['skema']['fields']
            : []
        "
        v-bind:model-default-fields="modelDefaultFields"
        v-on:row-clicked="modelLink($event)"
        v-on:delete-clicked="confirm_delete_instance($event)"
        v-on:new-clicked="showCreateNewInstanceModal = true"
      />
      <ModalCreateNewInstance
        v-if="showCreateNewInstanceModal"
        v-bind:model-name="model_name"
        v-bind:model-base-fields="modelBaseFields"
        v-on:cancel-clicked="showCreateNewInstanceModal = false"
        v-on:create-clicked="create_instance($event)"
      ></ModalCreateNewInstance>
      <ModalDelete
        v-if="showDeleteInstanceModal"
        v-bind:model-name="model_name"
        v-bind:instance-name="instance_name"
        v-on:cancel-clicked="showDeleteInstanceModal = false"
        v-on:delete-clicked="delete_instance"
      ></ModalDelete>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch, ref, onBeforeUnmount } from "vue";

import { useRoute, useRouter } from "vue-router";
import { useModelStore } from "@/stores/modelStore";
import FabTable from "@/components/FabTable.vue";
import ModalCreateNewInstance from "@/components/ModalCreateNewInstance.vue";
import ModalDelete from "@/components/ModalDelete.vue";

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

const router = useRouter();
const route = useRoute();
const showCreateNewInstanceModal = ref(false);
const showDeleteInstanceModal = ref(false);
const id = ref("");
const instance_name = ref("");

const confirm_delete_instance = (m: Model) => {
  showDeleteInstanceModal.value = true;
  id.value = m.id;
  instance_name.value = m.name;
};

const delete_instance = async () => {
  showDeleteInstanceModal.value = false;

  await modelStore.delete_instance(model_name.value, id.value);

  // refresh list
  modelStore.instances = await modelStore.get_all_instances(model_name.value);
};

const create_instance = async (m_json: any) => {
  const f: { [key: string]: any } = {};
  for (const x of modelBaseFields.value) {
    f[x.name] = m_json[x.name];
  }
  const i = await modelStore.create_instance(
    model_name.value,
    JSON.stringify(f)
  );
  showCreateNewInstanceModal.value = false;

  // go to the new instance
  router.push(`/${model_name.value}/${i.id}`);
};

const modelLink = (m: Model) => {
  router.push(`/${model_name.value}/${m.id}`);
};

const model_name = computed(() => {
  return route.params.model as string;
});

const modelBaseFields = computed(() => {
  return [
    { name: "name", type: "string" },
    { name: "id", type: "string" },
    { name: "owned_by", type: "string" },
    { name: "tags", type: "string" },
    { name: "parent_id", type: "string" },
    { name: "parent_type", type: "string" },
    { name: "permissions", type: "string" },
  ].concat(
    modelStore.models[model_name.value]
      ? modelStore.models[model_name.value]["skema"]["fields"]
      : []
  );
});

onMounted(async () => {
  modelStore.instances = await modelStore.get_all_instances(model_name.value);
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
      modelStore.instances = await modelStore.get_all_instances(model_name.value);
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
