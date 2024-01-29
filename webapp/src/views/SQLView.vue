<template>
  <div class="h-full w-full flex-col bg-gray-700">
    <section class="p-2">
      <div class="flex mb-2">
        <button
          class="rounded border bg-green-700 p-2 text-white hover:cursor-pointer hover:bg-green-400"
          v-on:click="execute_sql(sql_stmt)"
        >
          Run SQL
        </button>
        <div class="mx-2 flex items-center flex-grow border rounded">
          <div v-for="report in modelStore.reports">
            <div
              class="flex ml-2 h-8 w-fit items-center justify-start rounded-md bg-gray-300 shadow-md transition duration-300 ease-in-out dark:bg-gray-500 dark:text-gray-400"
            >
              <div
                class="flex h-8 w-full items-center rounded-l bg-transparent pl-2 pr-4 font-sans font-semibold outline-none hover:cursor-pointer hover:bg-gray-500 hover:underline"
                v-on:click="
                  sql_stmt = report.sql_stmt;
                  execute_sql_report(report.name);
                "
              >
                {{ report.name }}
              </div>
              <div
                class="flex hover:dark:bg-red-500 h-8 items-center justify-center rounded-r bg-gray-400 px-2 hover:cursor-pointer hover:bg-red-500 dark:bg-gray-600"
                v-on:click="confirm_delete_report(report.name)"
              >
                <svg
                  id="garbage-bin-icon"
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
        <div>
          <button
            class="mr-2 rounded border bg-slate-700 p-2 text-white hover:cursor-pointer hover:bg-slate-400"
            v-on:click="showCreateNewReportModal = true"
          >
            New Report
          </button>
          <button
            class="mr-2 rounded border bg-slate-700 p-2 text-white hover:cursor-pointer hover:bg-slate-400"
            v-on:click="copySqlInput"
          >
            Copy all
          </button>

          <button
            class="rounded border bg-slate-700 p-2 text-white hover:cursor-pointer hover:bg-slate-400"
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
      <div class="text-white mx-2 px-2 border flex-grow h-8">
        {{ modelStore.result_set?.status }}
      </div>
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

  <ModalDelete
    v-if="showDeleteReportModal"
    model-name="report"
    v-bind:instance-name="report"
    v-on:cancel-clicked="showDeleteReportModal = false"
    v-on:delete-clicked="delete_report()"
  ></ModalDelete>
  <ModalCreateNewReport
    v-if="showCreateNewReportModal"
    v-on:cancel-clicked="showCreateNewReportModal = false"
    v-on:create-clicked="create_report($event, sql_stmt)"
  >
  </ModalCreateNewReport>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import { useModelStore } from "@/stores/modelStore";
import TableLite from "vue3-table-lite/ts";
import ModalDelete from "@/components/ModalDelete.vue";
import ModalCreateNewReport from "@/components/ModalCreateNewReport.vue";
import "codemirror/mode/sql/sql.js";
import "codemirror/theme/ayu-mirage.css";
import { useClipboard } from "@vueuse/core";

const modelStore = useModelStore();

// RUN SQL
const sql_stmt = ref(`-- Use 'Ctrl+Enter' to run

select id, gen_random_uuid(), now(), floor(random()*100000000) as amount, concat('tag-', floor(random()*10)::string) as tags
from generate_series(0,100) as id;
`);

const execute_sql = async (stmt: string) => {
  //await modelStore.execute_sql_select(stmt, []);
  await modelStore.execute_sql_dml(stmt, []);
};

const execute_sql_report = async (name: string) => {
  await modelStore.execute_sql_report(name);
};

// REPORTS
const showDeleteReportModal = ref(false);
const showCreateNewReportModal = ref(false);
const report = ref("");
const report_name = ref("");

const create_report = async (name: string, sql_stmt: string) => {
  await modelStore.create_report(name, sql_stmt);
  await modelStore.get_all_reports();
  showCreateNewReportModal.value = false;
};

const confirm_delete_report = async (s: any) => {
  showDeleteReportModal.value = true;
  report.value = s;
};

const delete_report = async () => {
  showDeleteReportModal.value = false;
  await modelStore.delete_report(report.value);
  await modelStore.get_all_reports();
};

// SQL EDITOR
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

// TABLE
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
  if (modelStore.result_set?.cols) {
    for (const x of modelStore.result_set.cols) {
      data.push({
        label: x,
        field: x,
        // headerClasses: ["bg-slate-200", "text-black"],
        columnClasses: ["dark:bg-gray-600", "text-white"],
        // isKey: true,
        sortable: true,
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

onMounted(async () => {
  await modelStore.get_all_reports();
});
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
