<template>
  <div class="flex h-full w-full">
    <section id="context-bar" class="flex w-96 flex-col">
      <div v-for="(v, k) in modelStore.model_instance_children" v-bind:key="k">
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
          <router-link v-bind:to="'/' +   k + '/' + n.id">
            <span class="">{{ n.name }}</span>
          </router-link>
        </div>
      </div>
    </section>

    <section
      id="content-container"
      class="flex h-full w-full flex-wrap bg-gray-300 dark:bg-gray-700"
    >
      <div v-for="(v, k) in modelStore.model_instance" v-bind:key="k">
        <div class="m-2 text-lg font-semibold dark:text-slate-200">
          {{ k }}
        </div>

        <!-- <template v-if="modelStore.worst_models[model_name].skema.fields[].type === 'tag'">
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
        </template> -->

        <span
          v-show="!editing"
          class="m-2 h-12 w-44 bg-slate-500 p-2 dark:text-slate-100"
          v-on:dblclick="editing = !editing"
        >
          <label for="value">{{ v }}</label>
        </span>
        <!-- <span v-show="editing" class="bg-gray-100">
          <input
            focus="true"
            class="h-12"
            v-bind:value="value"
            type="text"
            v-on:input="value = $event.target.value"
            v-on:focusout="editing = !editing"
          />
        </span> -->
        <br />
        <br />
        <!-- {{k}}
        {{
          modelStore.worst_models[model_name].skema.fields
        }} -->
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import { useRoute, useRouter } from "vue-router";
import { useModelStore } from "@/stores/modelStore";

import type { Model } from "@/types";

const modelStore = useModelStore();

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

const id = computed(() => {
  return route.params.id as string;
});

const model_name = computed(() => {
  return route.params.model as string;
});

const editing = ref<boolean>(false);

const titleCase = (s: string) =>
  s
    .replace(/^[-_]*(.)/, (_, c) => c.toUpperCase()) // Initial char (after -/_)
    .replace(/[-_]+(.)/g, (_, c) => "_" + c.toUpperCase()); // First char after each -/_

const hashCode = (str: string) => {
  var hash = 0,
    i,
    chr;
  if (str.length === 0) return hash;
  for (i = 0; i < str.length; i++) {
    chr = str.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
};

const getLabel = (str: string) => {
  const crc = hashCode(str);
  switch (crc % 9) {
    case 0:
      return "bg-indigo-400 rounded-2xl p-2";
    case 1:
      return "bg-purple-600 rounded-2xl p-2";
    case 2:
      return "bg-teal-400 rounded-2xl p-2";
    case 3:
      return "bg-orange-400 rounded-2xl p-2";
    case 4:
      return "bg-rose-500 rounded-2xl p-2";
    case 5:
      return "bg-amber-400 rounded-2xl p-2";
    case 6:
      return "bg-lime-600 rounded-2xl p-2";
    case 7:
      return "bg-emerald-600 rounded-2xl p-2";
    case 8:
      return "bg-fuchsia-400 rounded-2xl p-2";
  }
};

onMounted(async () => {
  await modelStore.fetch_instance(model_name.value, id.value);
  await modelStore.fetch_instance_children(model_name.value, id.value);
  await modelStore.fetch_parent_chain(model_name.value, id.value);
});

watch(
  () => route.fullPath,
  async () => {
    if (id.value && !route.params.child_model_name) {
      console.log("modeldetailsview-watch", id.value, route.params);
      await modelStore.fetch_instance(model_name.value, id.value);
      await modelStore.fetch_instance_children(model_name.value, id.value);
      await modelStore.fetch_parent_chain(model_name.value, id.value);
    }
  }
);
</script>
