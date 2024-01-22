<template>
  <div class="h-full w-full flex-col bg-gray-700">
    <section class="p-2">
      <div class="flex">
        <button
          class="mb-2 border bg-green-700 p-2 text-white hover:cursor-pointer hover:bg-green-400"
          v-on:click="execute_sql(sql_stmt)"
        >
          Run SQL
        </button>
        <div class="flex-grow"></div>
        <div>
          <button
            class="mx-2 border bg-slate-700 p-2 text-white hover:cursor-pointer hover:bg-slate-400"
            v-on:click="copySqlInput"
          >
            Copy all
          </button>

          <button
            class="mx-2 border bg-slate-700 p-2 text-white hover:cursor-pointer hover:bg-slate-400"
            v-on:click="clearSqlInput"
          >
            Clear
          </button>
        </div>

        <!-- <button
            v-if="state.text.value != ''"
            class="ml-2 border bg-green-700 p-2 text-white hover:cursor-pointer hover:bg-green-400"
            v-on:click="execute_sql(state.text.value)"
          >
            Run Selected SQL
          </button> -->
      </div>
      <div class="flex">
        <Codemirror
          v-model:value="sql_stmt"
          v-bind:options="cmOptions"
          v-bind:height="300"
          v-on:keyup.ctrl.enter="execute_sql(sql_stmt)"
        />
      </div>
    </section>

    <section>
      <!--
        <div style="text-align: left">
        <label>SearchBy:</label><input v-model="searchTerm" />
        </div>
      -->
      <div class="p-2">
        <table-lite
          v-bind:has-checkbox="false"
          v-bind:is-static-mode="true"
          v-bind:columns="cols"
          v-bind:rows="rows"
          v-bind:page-size="5"
          v-bind:page-options="[
            { value: 5, text: 5 },
            { value: 10, text: 10 },
            { value: 25, text: 25 },
            { value: 100, text: 100 },
          ]"
          v-bind:total="rows.length"
          v-bind:sortable="sortable"
          v-on:return-checked-rows="updateCheckedRows"
        ></table-lite>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useModelStore } from "@/stores/modelStore";
import TableLite from "vue3-table-lite/ts";

// import { useTextSelection } from "@vueuse/core";
// const state = useTextSelection();

// ===
import "codemirror/mode/sql/sql.js";
import "codemirror/theme/ayu-mirage.css";
import { useClipboard } from "@vueuse/core";
// import { vOnClickOutside } from "@vueuse/components";
// import { tablesSchemaData, outputTableData, availableTablesData } from "@/data";
// import type { TableSchemaModel, TableModel } from "@/data";
// import TableSchema from "@/components/TableSchema.vue";
// import BaseTable from "@/components/BaseTable.vue";
// import BaseButton from "@/components/BaseButton.vue";
// import IconMenu from "@/components/icons/IconMenu.vue";

// const tablesSchema = ref<TableSchemaModel[]>(tablesSchemaData);

// const outputTable = ref<TableModel>(outputTableData);

// const availableTables = ref<TableModel[]>(availableTablesData);

const cmOptions = ref({
  mode: "text/x-sql",
  theme: "ayu-mirage",
  indentUnit: 4,
  smartIndent: true,
});

const { copy } = useClipboard();

const clearSqlInput = (): void => {
  sql_stmt.value = "";
};

const copySqlInput = (): void => {
  copy(sql_stmt.value);
};

//===

const modelStore = useModelStore();

const sql_stmt = ref(`-- Use 'Ctrl+Enter' to run

select a, now() from generate_series(0,100) as a;

`);

const execute_sql = async (stmt: string) => {
  await modelStore.execute_sql_select(stmt);
  // console.log(JSON.stringify(modelStore.result_set, undefined, 4));
};

const searchTerm = ref(""); // Search text

const rows = computed(() => {
  const data = [];
  if (modelStore.result_set?.rows) {
    for (const r of modelStore.result_set.rows) {
      var dict: any = {};
      for (var i = 0; i < r.length; i++) {
        dict[cols.value[i].label] = r[i];
      }
      data.push(dict);
    }
  }
  return data;
});

const cols = computed(() => {
  const data = [];
  if (modelStore.result_set?.col_names) {
    for (const x of modelStore.result_set.col_names) {
      data.push({
        label: x,
        field: x,
        // headerClasses: ["bg-slate-200", "text-black"],
        columnClasses: ["dark:bg-gray-600", "text-white"],
        // isKey: true,
      });
    }
  }
  return data;
});

const sortable = {
  order: "id",
  sort: "asc",
};

/**
 * Loading finish event
 */
// const tableLoadingFinish = (elements) => {
// table.isLoading = false;
// Array.prototype.forEach.call(elements, function (element) {
//   if (element.classList.contains("name-btn")) {
//     element.addEventListener("click", function () {
//       console.log(dataset.id + " name-btn click!!");
//     });
//   }
//   if (element.classList.contains("quick-btn")) {
//     element.addEventListener("click", function () {
//       console.log(dataset.id + " quick-btn click!!");
//     });
//   }
// });
// };

/**
 * Row checked event
 */
const updateCheckedRows = (rowsKey: any) => {
  console.log(rowsKey);
};
</script>

<style scoped>
.codemirror-container.bordered {
  border-radius: 0;
  border: none;
}

.codemirror-container {
  font-family: "Consolas", monospace;
  font-size: 20px;
}

:deep(.CodeMirror) {
  background-color: #1c2130;
}

:deep(.CodeMirror-gutter) {
  background-color: #1c2130;
}
</style>
