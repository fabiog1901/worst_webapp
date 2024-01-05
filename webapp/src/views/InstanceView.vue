<template>
  <div class="flex h-full w-full">
    <section
      id="context-bar"
      class="flex w-96 flex-col bg-gray-50 dark:bg-gray-700"
    >
      <div v-for="(v, k) in modelStore.instance_children" v-bind:key="k">
        <router-link v-bind:to="route.path + '/' + k"
          ><span
            class="m-1 flex w-32 cursor-pointer justify-center rounded-xl border bg-gray-400 p-2 align-middle hover:font-bold dark:bg-slate-700 dark:text-white"
            >{{ k }}</span
          >
        </router-link>
        <div
          v-for="n in v"
          v-bind:key="n"
          class="mx-12 my-1 flex cursor-pointer justify-center rounded-full border bg-green-400 p-2 align-middle hover:font-bold dark:bg-green-700 dark:text-white"
        >
          <router-link v-bind:to="'/' + k + '/' + n.id">
            <span class="">{{ n.name }}</span>
          </router-link>
        </div>
      </div>
    </section>

    <section
      id="content-container"
      class="flex h-full w-full bg-gray-300 dark:bg-gray-700"
    >
      <div class="w-96 flex-1 bg-gray-300 dark:bg-gray-700">
        <div class="p-2 text-sm text-gray-700 dark:text-white">name</div>
        <div
          class="bg-slate-300 p-2 text-xl font-semibold dark:bg-slate-500 dark:text-white"
        >
          {{ modelStore.instance?.name }}
        </div>
        <div v-for="x in getSkemaFields" v-bind:key="x" class="">
          <div class="p-2 text-sm text-gray-700 dark:text-white">
            {{ x.name }} <i>[{{ x.type }}]</i>
          </div>
          <div
            v-if="x.type === 'decimal'"
            class="h-12 bg-slate-300 p-2 dark:bg-slate-500 dark:text-white"
          >
            {{ formatDecimal(modelStore.instance?.[x.name as keyof Model]) }}
          </div>

          <div
            v-else-if="x.type === 'date'"
            class="h-12 bg-slate-300 p-2 dark:bg-slate-500 dark:text-white"
          >
            {{ formatDate(modelStore.instance?.[x.name as keyof Model]) }}
          </div>
          <div
            v-else-if="x.type === 'enum'"
            class="h-12 bg-slate-300 p-2 dark:bg-slate-500 dark:text-white"
          >
            <div
              class="flex h-8 w-fit min-w-16 items-center justify-center rounded border p-2 text-sm font-semibold"
              v-bind:class="getLabel(modelStore.instance?.[x.name as keyof Model] as string)"
            >
              {{ modelStore.instance?.[x.name as keyof Model] }}
            </div>
          </div>
          <div
            v-else-if="x.type === 'markdown'"
            class="max-h-80 w-full overflow-y-scroll dark:bg-slate-500 dark:text-white"
          >
            <FabMark
              class="h-fit dark:bg-slate-500 dark:text-white"
              v-bind:source="modelStore.instance?.[x.name] ?? ''"
              v-bind:theme="getTheme"
            />
          </div>

          <div
            v-else
            class="h-12 bg-slate-300 p-2 dark:bg-slate-500 dark:text-white"
          >
            {{ modelStore.instance?.[x.name as keyof Model] }}
          </div>
        </div>
      </div>
      <div class="w-96 bg-gray-300 dark:bg-gray-900 dark:text-white">
        <div class="mx-2 text-sm dark:text-white">
          id: {{ modelStore.instance?.id }}
        </div>
        <div class="mx-2 text-sm dark:text-white">
          parent_type: {{ modelStore.instance?.parent_type }}
        </div>
        <div class="mx-2 text-sm">
          parent_id: {{ modelStore.instance?.parent_id }}
        </div>
        <div class="mx-2 text-sm">
          owned_by: {{ modelStore.instance?.owned_by }}
        </div>
        <div class="mx-2 text-sm">
          permissions: {{ modelStore.instance?.permissions }}
        </div>
        <div class="mx-2 text-sm">
          created_by: {{ modelStore.instance?.created_by }}
        </div>
        <div class="mx-2 text-sm">
          created_at: {{ modelStore.instance?.created_at }}
        </div>
        <div class="mx-2 text-sm">
          updated_by: {{ modelStore.instance?.updated_by }}
        </div>
        <div class="mx-2 text-sm">
          updated_at: {{ modelStore.instance?.updated_at }}
        </div>

        <div class="mx-2 text-sm">
          tags:
          <div
            v-for="tag in modelStore.instance?.tags"
            v-bind:key="tag"
            class="p-1"
          >
            <div
              class="flex h-8 w-fit min-w-16 items-center justify-center rounded-2xl p-2 text-sm font-semibold"
              v-bind:class="getLabel(tag)"
            >
              {{ tag }}
            </div>
          </div>
        </div>
        <div class="mx-2 text-sm">
          attachments:
          <div
            v-for="att in modelStore.instance?.attachments"
            v-bind:key="att"
            class="flex p-1"
          >
            <div
              class="flex h-8 w-fit items-center justify-start rounded-md bg-gray-300 shadow-md transition duration-300 ease-in-out dark:bg-gray-500 dark:text-gray-400"
            >
              <div
                class="flex h-8 w-full items-center rounded bg-transparent pl-2 pr-4 font-sans font-semibold outline-none hover:cursor-pointer hover:bg-gray-400 hover:underline hover:dark:bg-gray-600"
                v-on:click="download_file(att)"
              >
                {{ att }}
              </div>
              <div
                class="flex h-8 items-center justify-center rounded-r bg-gray-400 px-2 hover:cursor-pointer hover:bg-red-500 dark:bg-gray-700"
                v-on:click="confirm_delete_attachment(att)"
              >
                <svg
                  id="magnifying-glass-icon"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke="currentColor"
                  class="top-navigation-icon h-5 w-5"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div
          class="m-2 flex h-8 w-fit items-center justify-start rounded-md bg-gray-300 text-gray-400 shadow-md transition duration-300 ease-in-out dark:bg-gray-500"
        >
          <label
            class="flex h-8 w-full items-center rounded bg-green-700 p-2 font-sans font-semibold text-white outline-none hover:cursor-pointer hover:bg-green-400"
            for="upload_file"
            >Upload New File
            <input
              id="upload_file"
              hidden
              type="file"
              v-on:change="upload_file"
            />
            <svg
              id="magnifying-glass-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="top-navigation-icon ml-2 h-5 w-5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"
              />
            </svg>
          </label>
        </div>
        <div class="flex-grow bg-yellow-400"></div>
        <hr
          id="linebreaker"
          class="mx-2 rounded-full border border-gray-200 bg-gray-200 dark:border-gray-800 dark:bg-gray-800"
        />
        <div
          class="m-2 flex h-8 w-48 items-center justify-start rounded-md bg-gray-300 text-gray-400 shadow-md transition duration-300 ease-in-out"
        >
          <label
            class="flex h-8 w-full items-center justify-center rounded bg-red-500 p-2 font-sans font-semibold text-white outline-none hover:cursor-pointer hover:bg-red-400"
            v-on:click="showDeleteInstanceModal = true"
            >Delete {{ modelStore.instance?.name }}

            <svg
              id="magnifying-glass-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="top-navigation-icon ml-2 h-5 w-5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
              />
            </svg>
          </label>
        </div>
      </div>

      <ModalDelete
        v-if="showDeleteInstanceModal"
        v-bind:model-name="model_name"
        v-bind:instance-name="modelStore.instance?.name"
        v-on:cancel-clicked="showDeleteInstanceModal = false"
        v-on:delete-clicked="delete_instance"
      ></ModalDelete>
      <ModalDelete
        v-if="showDeleteAttachmentModal"
        model-name="attachment"
        v-bind:instance-name="attachment"
        v-on:cancel-clicked="showDeleteAttachmentModal = false"
        v-on:delete-clicked="delete_attachment"
      ></ModalDelete>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch, ref } from "vue";

import { useRoute, useRouter } from "vue-router";
import { useModelStore } from "@/stores/modelStore";
import FabMark from "@/components/FabMark.vue";
import ModalDelete from "@/components/ModalDelete.vue";

import { formatDecimal, formatDate, getLabel } from "@/utils/utils";
import { saveAs } from "file-saver";

import type { Model } from "@/types";

const modelStore = useModelStore();
const route = useRoute();
const router = useRouter();

const showDeleteAttachmentModal = ref(false);
const showDeleteInstanceModal = ref(false);
const attachment = ref("");

const delete_attachment = async () => {
  showDeleteAttachmentModal.value = false;

  await modelStore.delete_attachment(
    model_name.value,
    id.value,
    attachment.value
  );

  // refresh to get updated list of attachments
  modelStore.get_instance(model_name.value, id.value);
};

const delete_instance = async () => {
  showDeleteInstanceModal.value = false;

  await modelStore.delete_instance(model_name.value, id.value);

  // go back to TableView for the same model name
  router.push(`/${model_name.value}`);
};

const id = computed(() => {
  return route.params.id as string;
});

const model_name = computed(() => {
  return route.params.model as string;
});

const getSkemaFields = computed(() => {
  if (modelStore.models[model_name.value])
    return modelStore.models[model_name.value]["skema"]["fields"];
  return [];
});

const upload_file = async (e: any) => {
  const presigned_url = await modelStore.get_presigned_put_url(
    model_name.value,
    id.value,
    e.target.files[0].name
  );

  await fetch(presigned_url, {
    method: "PUT",
    body: e.target.files[0],
  });

  modelStore.get_instance(model_name.value, id.value);
};

const download_file = async (filename: string) => {
  const presigned_url = await modelStore.get_presigned_get_url(
    model_name.value,
    id.value,
    filename
  );

  saveAs(presigned_url, filename);
};

const confirm_delete_attachment = async (s: any) => {
  showDeleteAttachmentModal.value = true;
  attachment.value = s;
};

// const ff = computed(() => {
//   if (modelStore.instance !== undefined) {
//     return Object.keys(modelStore.instance)
//       .filter(
//         (key) =>
//           [
//             "id",
//             "name",
//             "owned_by",
//             "permissions",
//             "parent_type",
//             "parent_id",
//             "created_by",
//             "created_at",
//             "updated_at",
//             "updated_by",
//             "attachments",
//             "tags",
//           ].indexOf(key) === -1
//       )
//       .reduce((cur, key) => {
//         return Object.assign(cur, {
//           [key]: modelStore.instance?.[key as keyof Model],
//         });
//       }, {});
//   } else {
//     return {};
//   }
// });

const getTheme = computed(() => {
  const theme = localStorage.getItem("user-theme");
  if (!theme) {
    return "dark";
  }
  return theme;
});

//const editing = ref<boolean>(false);

onMounted(async () => {
  console.log("instance-view-onMounted", model_name.value);
  await modelStore.get_instance(model_name.value, id.value);
  await modelStore.get_instance_children(model_name.value, id.value);
  await modelStore.get_instance_parent_chain(model_name.value, id.value);
});

watch(
  () => route.fullPath,
  async () => {
    if (id.value && !route.params.child_model_name) {
      console.log("instance-view-watch", id.value, route.params);
      await modelStore.get_instance(model_name.value, id.value);
      await modelStore.get_instance_children(model_name.value, id.value);
      await modelStore.get_instance_parent_chain(model_name.value, id.value);
    }
  }
);
</script>
