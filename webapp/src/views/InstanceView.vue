<template>
  <div class="flex h-full w-full">
    <section id="context-bar" class="flex w-96 flex-col">
      <div v-for="(v, k) in modelStore.instance_children" v-bind:key="k">
        <router-link v-bind:to="route.path + '/' + k"
          ><span
            class="m-1 flex w-32 cursor-pointer justify-center rounded border-b bg-red-500 p-2 align-middle text-white hover:font-bold"
            >{{ k }}</span
          >
        </router-link>
        <div
          v-for="n in v"
          v-bind:key="n"
          class="m-2 mx-4 flex cursor-pointer justify-center rounded-full border-b bg-blue-500 p-2 align-middle text-white hover:font-bold"
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
      <div class="w-96 bg-gray-300 dark:bg-gray-600">
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
              class="flex h-8 w-16 items-center justify-center text-sm font-semibold"
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
            class="p-1"
          >
            <div
              class="flex h-8 w-16 items-center justify-center text-sm font-semibold"
              v-bind:class="getLabel(att)"
            >
              {{ att }}
            </div>
          </div>
        </div>
      </div>
      <div></div>
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
import { computed, onMounted, watch } from "vue";

import { useRoute } from "vue-router";
import { useModelStore } from "@/stores/modelStore";
import FabMark from "@/components/FabMark.vue";

import { formatDecimal, formatDate, getLabel } from "@/utils/utils";

import type { Model } from "@/types";

const modelStore = useModelStore();
//const router = useRouter();
const route = useRoute();

// const createNewModel = () => {
//   console.log(`new model ${model_name.value}`);
// };

// const deleteModel = (m: Model) => {
//   console.log(`delete model: ${model_name.value}/${m.id}`);
// };

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
