<template>
  <div class="flex h-full w-full">
    <!-- <section
      id="context-bar"
      class="flex w-88 bg-gray-300 dark:bg-gray-500 dark:text-white"
    >
      Context bar
    </section> -->

    <section
      id="content-container"
      class="flex h-full w-full p-2 flex-col bg-gray-300 dark:bg-gray-700"
    >
      <div class="h-8"></div>
      <TableLite
        v-bind:has-checkbox="false"
        v-bind:is-static-mode="true"
        v-bind:columns="cols"
        v-bind:rows="modelStore.instances"
        v-bind:page-size="5"
        v-bind:page-options="[
          { value: 5, text: 5 },
          { value: 10, text: 10 },
          { value: 25, text: 25 },
          { value: 100, text: 100 },
        ]"
        v-bind:total="modelStore.instances.length"
        v-bind:sortable="sortable"
        v-on:return-checked-rows="updateCheckedRows"
      ></TableLite>

      <ModalCreateNewInstance
        v-if="showCreateNewInstanceModal"
        v-bind:model-name="instance_type"
        v-bind:model-base-fields="modelBaseFields"
        v-on:cancel-clicked="showCreateNewInstanceModal = false"
        v-on:create-clicked="create_instance($event)"
      ></ModalCreateNewInstance>
      <ModalDelete
        v-if="showDeleteInstanceModal"
        v-bind:model-name="instance_type"
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

import ModalCreateNewInstance from "@/components/ModalCreateNewInstance.vue";
import ModalDelete from "@/components/ModalDelete.vue";

// import TableLite from "vue3-table-lite/ts";
import TableLite from "@/components/TableLiteTs.vue";

import type { Model } from "@/types";

const modelStore = useModelStore();
const router = useRouter();
const route = useRoute();

const instance_id = ref("");
const instance_name = ref("");
const instance_type = computed(() => {
  return route.params.model as string;
});

const model_default_fields = [
  { name: "name", type: "", display: null, link: instance_type.value },
  { name: "owned_by", type: "" },
  { name: "tags", type: "tag" },
  { name: "updated_by", type: "" },
  {
    name: "updated_at",
    type: "date",
  },
  { name: "created_by", type: "" },
  {
    name: "created_at",
    type: "date",
  },
];

const showCreateNewInstanceModal = ref(false);
const showDeleteInstanceModal = ref(false);

// TABLE
const cols = computed(() => {
  const data = [];
  for (const x of model_default_fields.concat(
    modelStore.models[instance_type.value]?.["skema"]["fields"] ?? [],
  )) {
    data.push({
      label: x.name,
      field: x.name,
      // headerClasses: ["bg-slate-200", "text-black"],
      columnClasses: ["dark:bg-gray-600", "text-white"],
      isKey: false,
      sortable: true,
      display: x.display || null,
      link: x.link,
    });
  }

  return data;
});

const sortable = {
  order: "id",
  sort: "asc",
};

/**
 * Row checked event
 */
const updateCheckedRows = (rowsKey: any) => {
  console.log(rowsKey);
};

const confirm_delete_instance = (m: Model) => {
  showDeleteInstanceModal.value = true;
  instance_id.value = m.id;
  instance_name.value = m.name;
};

const delete_instance = async () => {
  showDeleteInstanceModal.value = false;

  await modelStore.delete_instance(instance_type.value, instance_id.value);

  // refresh list
  modelStore.instances = await modelStore.get_all_instances(
    instance_type.value,
  );
};

const create_instance = async (m_json: any) => {
  const f: { [key: string]: any } = {};
  for (const x of modelBaseFields.value) {
    f[x.name] = m_json[x.name];
  }
  const i = await modelStore.create_instance(
    instance_type.value,
    JSON.stringify(f),
  );
  showCreateNewInstanceModal.value = false;

  // go to the new instance
  router.push(`/${instance_type.value}/${i.id}`);
};

onMounted(async () => {
  modelStore.instances = await modelStore.get_all_instances(
    instance_type.value,
  );
  modelStore.instance_parent_chain = [
    [
      instance_type.value,
      "",
      `${
        instance_type.value.charAt(0).toUpperCase() +
        instance_type.value.slice(1)
      } Overview`,
    ],
  ];
});

watch(
  () => route.fullPath,
  async () => {
    if (route.params.model && !route.params.id) {
      modelStore.instances = await modelStore.get_all_instances(
        instance_type.value,
      );
      modelStore.instance_parent_chain = [
        [
          instance_type.value,
          "",
          `${
            instance_type.value.charAt(0).toUpperCase() +
            instance_type.value.slice(1)
          } Overview`,
        ],
      ];
    }
  },
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
