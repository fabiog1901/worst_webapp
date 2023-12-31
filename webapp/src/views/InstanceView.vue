<template>
  <div class="flex h-full w-full">
    <section id="context-bar" class="flex w-96 flex-col dark:bg-gray-700">
      <div v-for="(v, k) in modelStore.instance_children" v-bind:key="k">
        <router-link v-bind:to="route.path + '/' + k"
          ><span
            class="m-1 flex w-32 cursor-pointer justify-center rounded-xl border bg-slate-700 p-2 align-middle text-white hover:font-bold"
            >{{ k }}</span
          >
        </router-link>
        <div
          v-for="n in v"
          v-bind:key="n"
          class="mx-12 my-1 flex cursor-pointer justify-center rounded-full border p-2 align-middle text-white hover:font-bold dark:bg-green-700"
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
        <div class="bg-slate-500 p-2 text-xl font-semibold dark:text-white">
          {{ modelStore.instance?.name }}
        </div>
        <div v-for="x in getSkemaFields" v-bind:key="x" class="">
          <div class="p-2 text-sm text-gray-700 dark:text-white">
            {{ x.name }} [{{ x.type }}]
          </div>
          <div
            v-if="x.type === 'decimal'"
            class="h-12 bg-slate-500 p-2 dark:text-white"
          >
            {{ formatDecimal(modelStore.instance?.[x.name as keyof Model]) }}
          </div>

          <div
            v-else-if="x.type === 'date'"
            class="h-12 bg-slate-500 p-2 dark:text-white"
          >
            {{ formatDate(modelStore.instance?.[x.name as keyof Model]) }}
          </div>
          <div
            v-else-if="x.type === 'enum'"
            class="h-12 bg-slate-500 p-2 dark:text-white"
          >
            <div
              class="flex h-8 w-16 items-center justify-center text-sm font-semibold"
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
              v-bind:source="modelStore.instance?.[x.name]"
              v-bind:theme="getTheme"
            />
          </div>

          <div v-else class="h-12 bg-slate-500 p-2 dark:text-white">
            {{ modelStore.instance?.[x.name as keyof Model] }}
          </div>
        </div>
      </div>
      <div class="w-96 bg-gray-300 dark:bg-gray-900">
        <div class="mx-2 text-sm dark:text-white">
          id: {{ modelStore.instance?.id }}
        </div>
        <div class="mx-2 text-sm dark:text-white">
          parent_type: {{ modelStore.instance?.parent_type }}
        </div>
        <div class="mx-2 text-sm text-white">
          parent_id: {{ modelStore.instance?.parent_id }}
        </div>
        <div class="mx-2 text-sm text-white">
          owned_by: {{ modelStore.instance?.owned_by }}
        </div>
        <div class="mx-2 text-sm text-white">
          permissions: {{ modelStore.instance?.permissions }}
        </div>
        <div class="mx-2 text-sm text-white">
          created_by: {{ modelStore.instance?.created_by }}
        </div>
        <div class="mx-2 text-sm text-white">
          created_at: {{ modelStore.instance?.created_at }}
        </div>
        <div class="mx-2 text-sm text-white">
          updated_by: {{ modelStore.instance?.updated_by }}
        </div>
        <div class="mx-2 text-sm text-white">
          updated_at: {{ modelStore.instance?.updated_at }}
        </div>

        <div class="mx-2 text-sm text-white">
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
        <div class="mx-2 text-sm text-white">
          attachments:
          <div
            v-for="att in modelStore.instance?.attachments"
            v-bind:key="att"
            class="flex p-1"
          >
            <div
              class="flex h-8 w-fit items-center justify-start rounded-md bg-gray-300 text-gray-400 shadow-md transition duration-300 ease-in-out dark:bg-gray-500"
            >
              <div
                class="flex h-8 w-full items-center rounded bg-transparent pl-2 pr-4 font-sans font-semibold text-gray-400 outline-none hover:cursor-pointer hover:bg-gray-600 hover:underline"
              >
                {{ att }}
              </div>
              <div
                class="flex h-8 items-center justify-center rounded-r bg-gray-700 px-2 hover:cursor-pointer hover:bg-red-500"
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
        <div class="border bg-green-500">
          <input type="file" v-on:change="uploadfile" />
        </div>
      </div>
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
              <h3 class="text-2xl">Delete Object</h3>
              <div
                class="cursor-pointer text-2xl hover:text-gray-600"
                v-on:click="showModal = false"
              >
                &#215;
              </div>
            </div>

            <div class="max-h-full px-4 py-4">
              <p class="text-gray-800">
                Are you sure you want to delete:
                <span class="font-semibold">{{ att }}</span> ?
              </p>

              <div class="mt-4 text-right">
                <button
                  class="px-4 py-2 text-sm text-gray-600 hover:underline focus:outline-none"
                  v-on:click="showModal = false"
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
      <!--
        <div v-for="(v, k) in modelStore.instance" v-bind:key="k">
        <div class="m-2 text-lg font-semibold dark:text-slate-200">
          {{ k }}
        </div>

         <template v-if="modelStore.worst_models[model_name].skema.fields[].type === 'tag'">
          <div
            v-for="tag in slotProps.data[col.name]"
            v-bind:key="tag"
            class="p-1"
          >
            <div
              class="flex h-8 w-16 items-center justify-center text-sm font-semibold"
              v-bind:class="getStatusLabel(tag)"
            >
              {{ tag }}
            </div>
          </div>
        </template> 

        <span
          v-show="!editing"
          class="m-2 h-12 w-44 bg-slate-500 p-2 dark:text-slate-100"
          v-on:dblclick="editing = !editing"
        >
          <label for="value">{{ v }}</label>
        </span>
      </div>
      -->
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch, ref } from "vue";

import { useRoute } from "vue-router";
import { useModelStore } from "@/stores/modelStore";
import FabMark from "@/components/FabMark.vue";

import { formatDecimal, formatDate, getLabel } from "@/utils/utils";

import type { Model } from "@/types";

const modelStore = useModelStore();
//const router = useRouter();
const route = useRoute();

const showModal = ref(false);
const att = ref("");

// const createNewModel = () => {
//   console.log(`new model ${model_name.value}`);
// };

const delete_instance = async () => {
  showModal.value = false;

  await modelStore.delete_attachment(model_name.value, id.value, att.value);

  // refresh to get updated list of attachments
  modelStore.get_instance(model_name.value, id.value);
};

// const modelLink = (m: Model) => {
//   router.push(`/${model_name.value}/${m.id}`);
// };

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

const uploadfile = async (e: any) => {
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

const confirm_delete_attachment = async (s: any) => {
  showModal.value = true;
  att.value = s;
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
