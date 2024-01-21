<template>
  <div class="h-full w-full flex-col bg-gray-700">
    <section class="p-2">
      <textarea
        class="w-full bg-slate-600 text-white"
        name=""
        id=""
        cols="120"
        rows="15"
        v-model="sql_stmt"
      ></textarea>
    </section>
    <div
      class="flex h-12 w-32 items-center justify-center rounded-3xl bg-green-500 p-2 font-semibold text-white hover:cursor-pointer hover:bg-green-400"
      v-on:click="execute_sql"
    >
      Execute SQL
    </div>

    <section></section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useModelStore } from "@/stores/modelStore";

const modelStore = useModelStore();

const sql_stmt = ref("");

const execute_sql = async () => {
  console.log(sql_stmt.value);

  await modelStore.execute_sql_select(sql_stmt.value);

  console.log(JSON.stringify(modelStore.result_set, undefined, 4));
};
</script>
