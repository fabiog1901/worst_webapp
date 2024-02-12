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
      <FabToolbar
        v-model="keyword"
        v-on:new-clicked="showCreateNewInstanceModal = true"
        v-on:delete-clicked="showDeleteInstanceModal = true"
        v-on:export-clicked="exportData"
      ></FabToolbar>

      <div class="h-8"></div>

      <TableLite
        v-bind:has-checkbox="true"
        checked-return-type="key"
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
        v-if="showDeleteInstanceModal && selected_instances_ids.length > 0"
        model-name="selected item(s)"
        instance-name=""
        v-on:cancel-clicked="showDeleteInstanceModal = false"
        v-on:delete-clicked="delete_instances"
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
import FabToolbar from "@/components/FabToolbar.vue";
import TableLite from "@/components/TableLiteTs.vue";

import type { Model } from "@/types";

const modelStore = useModelStore();
const router = useRouter();
const route = useRoute();

const selected_instances_ids = ref<string[]>([]);
const selected_instances = ref<Model[]>([]);

const instance_type = computed(() => {
  return route.params.model as string;
});

const keyword = ref("");

import { save_to_csv } from "@/utils/utils";

const exportData = () => {
  console.log(selected_instances.value);

  //  save_to_csv(modelStore.instances, instance_type.value);
};

const model_default_fields = [
  {
    name: "id",
    type: "",
    is_key: true,
    link: instance_type.value,
    display: (x: any) => {
      return x.id.substring(0, 8).concat("...");
    },
  },
  { name: "name", type: "", link: instance_type.value },
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
      isKey: x.is_key ?? false,
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
  selected_instances_ids.value = rowsKey;
  selected_instances.value = modelStore.instances.filter((x) =>
    include_checked_rows(x),
  ) as Model[];
};

const include_checked_rows = (x: any) => {
  if (selected_instances_ids.value.length === 0) return true;
  return selected_instances_ids.value.includes(x.id);
};

// const include_by_search_term = () => {
//   let newData = fakeData.filter(
//           (x) =>
//             x.email.toLowerCase().includes(keyword.toLowerCase()) ||
//             x.name.toLowerCase().includes(keyword.toLowerCase()),
//         );
// };



// include_job_by_degree: () => (job: Job) => {
//       const userStore = useUserStore();
//       if (userStore.selectedDegrees.length === 0) return true;
//       return userStore.selectedDegrees.includes(job.degree);
//     },
//     include_job_by_search_term: () => (job: Job) => {
//       const userStore = useUserStore();
//       return job.title
//         .toLowerCase()
//         .includes(userStore.searchTerm.toLowerCase());
//     },
//     get_filtered_jobs(state): Job[] {
//       return state.jobs
//         .filter((job) => this.include_job_by_org(job))
//         .filter((job) => this.include_job_by_job_type(job))
//         .filter((job) => this.include_job_by_degree(job))
//         .filter((job) => this.include_job_by_search_term(job));
//     },

const delete_instances = async () => {
  showDeleteInstanceModal.value = false;

  selected_instances_ids.value.forEach(async (x) => {
    await modelStore.delete_instance(instance_type.value, x);
  });

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

const modelBaseFields = computed(() => {
  return [
    { name: "name", type: "string" },
    { name: "id", type: "string" },
    { name: "owned_by", type: "string" },
    { name: "tags", type: "string" },
    { name: "parent_id", type: "string" },
    { name: "parent_type", type: "string" },
    { name: "permissions", type: "string" },
  ].concat(modelStore.models[instance_type.value]?.["skema"]["fields"] ?? []);
});

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
