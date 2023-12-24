<template>
  <section class="flex">
    <div class="mx-2">
      <div
        v-for="m in Object.keys(modelStore.worst_models)"
        id="models"
        v-bind:key="m"
        class="m-1"
      >
        <div
          class="cursor-pointer rounded-3xl border-b bg-blue-600 p-2 text-center text-white hover:bg-blue-400"
          v-on:click="get_model(m)"
        >
          {{ m }}
        </div>
        <!-- <span class="">{{ m }} - {{ modelStore.worst_models[m] }}</span> -->
      </div>
    </div>
    <div class="m-2 w-96 rounded-md border-2 border-blue-700 bg-gray-200">
      <textarea v-model="m_json" class="h-full w-full"></textarea>
    </div>

    <div class="mx-2">
      <div
        v-for="m in Object.keys(modelStore.worst_models)"
        id="models"
        v-bind:key="m"
        class="m-1"
      >
        <div
          class="cursor-pointer rounded-3xl border-b bg-red-600 p-2 text-center text-white hover:bg-red-400"
          v-on:click="delete_worst_model(m)"
        >
          {{ m }}
        </div>
        <!-- <span class="">{{ m }} - {{ modelStore.worst_models[m] }}</span> -->
      </div>
    </div>
    <div
      class="m-1 h-10 cursor-pointer rounded-3xl border-b bg-green-600 p-2 text-center text-white hover:bg-green-400"
      v-on:click="create_worst_model"
    >
      Create Model
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

// import { useRoute, useRouter } from "vue-router";
import { useModelStore } from "@/stores/modelStore";

const modelStore = useModelStore();

const m_json = ref();

const get_model = (m: string) => {
  m_json.value = JSON.stringify(modelStore.worst_models[m], undefined, 8);
};

const delete_worst_model = (m: string) => {
  modelStore.delete_model(m);
  modelStore.get_all_models();
};

const create_worst_model = () => {
  modelStore.create_model(m_json.value);
  modelStore.get_all_models();
};

onMounted(async () => {
  await modelStore.get_all_models();
});
</script>
