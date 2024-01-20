<template>
  <section class="flex flex-grow bg-gray-300 dark:bg-gray-500 dark:text-white">
    <div class="">
      <div
        v-for="m in Object.keys(modelStore.models)"
        id="models"
        v-bind:key="m"
        class="m-1"
      >
        <div
          class="cursor-pointer rounded-3xl border bg-blue-600 p-2 text-center text-white hover:bg-blue-400"
          v-on:click="get_model(m)"
        >
          {{ m }}
        </div>
        <!-- <span class="">{{ m }} - {{ modelStore.worst_models[m] }}</span> -->
      </div>
    </div>
    <div
      class="m-2 w-96 rounded-md border-2 border-blue-700 bg-gray-200 text-black"
    >
      <textarea v-model="m_json" class="h-full w-full"></textarea>
    </div>

    <div class="mx-2">
      <div
        v-for="m in Object.keys(modelStore.models)"
        id="models"
        v-bind:key="m"
        class="m-1"
      >
        <div
          class="cursor-pointer rounded-3xl border bg-red-600 p-2 text-center text-white hover:bg-red-400"
          v-on:click="delete_worst_model(m)"
        >
          {{ m }}
        </div>
        <!-- <span class="">{{ m }} - {{ modelStore.worst_models[m] }}</span> -->
      </div>
    </div>
    <div
      class="m-1 h-10 cursor-pointer rounded-3xl border bg-green-600 p-2 text-center text-white hover:bg-green-400"
      v-on:click="create_worst_model"
    >
      Create Model
    </div>
  </section>

  <section
    class="mx-1 flex flex-grow bg-gray-300 dark:bg-gray-500 dark:text-white"
  >
    <div class="">
      <div
        v-for="r in Object.keys(modelStore.reports)"
        id="reports"
        v-bind:key="r"
        class="m-1"
      >
        <div
          class="cursor-pointer rounded-3xl border bg-blue-600 p-2 text-center text-white hover:bg-blue-400"
          v-on:click="get_report(r)"
        >
          {{ r }}
        </div>
        <!-- <span class="">{{ m }} - {{ modelStore.worst_models[m] }}</span> -->
      </div>
    </div>
    <div
      class="m-2 w-96 rounded-md border-2 border-blue-700 bg-gray-200 text-black"
    >
      <textarea v-model="report " class="h-full w-full"></textarea>
    </div>

    <div class="mx-2">
      <div
        v-for="r in Object.keys(modelStore.reports)"
        id="models"
        v-bind:key="r"
        class="m-1"
      >
        <div
          class="cursor-pointer rounded-3xl border bg-red-600 p-2 text-center text-white hover:bg-red-400"
          v-on:click="delete_worst_report(r)"
        >
          {{ r }}
        </div>
        <!-- <span class="">{{ m }} - {{ modelStore.worst_models[m] }}</span> -->
      </div>
    </div>
    <div>
      <div
        class="m-1 h-10 cursor-pointer rounded-3xl border bg-green-600 p-2 text-center text-white hover:bg-green-400"
        v-on:click="create_worst_report(report_name, report)"
      >
        Create Report
      </div>
      <input v-model="report_name" class="text-black" type="text" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

// import { useRoute, useRouter } from "vue-router";
import { useModelStore } from "@/stores/modelStore";

const modelStore = useModelStore();

const m_json = ref();
const report = ref("");
const report_name = ref("");

const get_model = (m: string) => {
  m_json.value = JSON.stringify(modelStore.models[m], undefined, 4);
};

const get_report = (name: string) => {
  report.value = JSON.stringify(modelStore.reports[name], undefined, 4);
};

const delete_worst_model = (m: string) => {
  modelStore.delete_model(m);
  modelStore.get_all_models();
};

const delete_worst_report = (name: string) => {
  modelStore.delete_report(name);
  modelStore.get_all_reports();
};

const create_worst_model = () => {
  modelStore.create_model(m_json.value);
  modelStore.get_all_models();
};

const create_worst_report = (name: string, sql_stmt: string) => {
  modelStore.create_report(name, sql_stmt);
  modelStore.get_all_reports();
};

onMounted(async () => {
  await modelStore.get_all_models();
  await modelStore.get_all_reports();
});
</script>
