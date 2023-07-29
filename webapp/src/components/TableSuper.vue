<template>
  <div>
    <div>
      <div
        id="toolbar"
        class="m-2 flex rounded border-2 border-gray-500 bg-gray-200 p-2 dark:border-gray-500 dark:bg-gray-700"
      >
        <div
          id="new-button"
          class="mx-2 flex cursor-pointer items-center justify-between rounded-xl bg-blue-600 p-2 text-white"
          v-on:click="openNew"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="h-6 w-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 6v12m6-6H6"
            />
          </svg>

          <span class="mx-1">New</span>
        </div>
        <div
          id="delete-button"
          class="mx-2 flex cursor-pointer items-center justify-between rounded-xl bg-red-600 p-2 text-white"
          v-on:click="confirmDeleteSelected"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="h-6 w-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
            />
          </svg>

          <span class="mx-1">Delete</span>
        </div>
        <div
          id="query-input"
          class="ml-20 flex cursor-pointer items-center justify-between rounded-xl bg-gray-300 p-2 text-gray-600"
        >
          <input
            v-model="filters['global'].value"
            class="mx-2 w-80 rounded px-2"
            placeholder="Filter by keyword..."
          />
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="h-6 w-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
            />
          </svg>
        </div>
        <div
          id="export-button"
          class="mx-2 ml-auto flex cursor-pointer justify-between rounded-xl bg-green-600 p-2 text-white"
          v-on:click="exportCSV()"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="h-6 w-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
            />
          </svg>

          <span class="mx-1" value="Mona">Export</span>
        </div>
      </div>

      <DataTable
        ref="dt"
        v-model:selection="selectedProducts"
        v-bind:value="props.data"
        data-key="id"
        v-bind:paginator="true"
        v-bind:rows="5"
        v-bind:filters="filters"
        paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport JumpToPageDropdown RowsPerPageDropdown"
        v-bind:rows-per-page-options="[5, 10, 25]"
        current-page-report-template="Showing {first} to {last} of {totalRecords} products"
        v-bind:pt="{
          root: {
            class:
              'rounded m-2 border-solid flex-col items-center dark:bg-gray-700 bg-gray-200',
          },
          bodyRow: {
            class: 'rounded border-2 bg-gray-600 text-white',
          },
          headerRow: {
            class: 'rounded border-2 bg-gray-900 text-white',
          },
          column: {
            root: {
              class: 'rounded border-2 m-3',
            },
          },
          paginator: {
            root: {
              class:
                'my-2 flex rounded border-2 border-gray-500 bg-gray-200 p-2 dark:border-gray-500 dark:bg-gray-700 justify-center',
            },
            firstPageButton: {
              class:
                'hover:dark:bg-gray-500 dark:text-gray-200 hover:bg-gray-400 text-gray-700 mx-2 w-12 h-12 rounded-[50%]',
            },
            previousPageButton: {
              class:
                'hover:dark:bg-gray-500 dark:text-gray-200 hover:bg-gray-400 text-gray-700 mx-2 w-12 h-12 rounded-[50%]',
            },
            lastPageButton: {
              class:
                'hover:dark:bg-gray-500 dark:text-gray-200 hover:bg-gray-400 text-gray-700 mx-2 w-12 h-12 rounded-[50%]',
            },
            nextPageButton: {
              class:
                'hover:dark:bg-gray-500 dark:text-gray-200 hover:bg-gray-400 text-gray-700 mx-2 w-12 h-12 rounded-[50%]',
            },
            pages: {
              class: 'mx-4',
            },
            // pageButton: {
            //   class:
            //     'bg-gray-400 text-gray-200 min-w-[3rem] h-12 transition-shadow duration-[0.2s] m-[0.143rem] rounded-[50%] border-0 border-none',
            // },
            pageButton: ({ context }) => ({
              class: context.active
                ? 'hover:dark:bg-gray-500 dark:text-gray-200 hover:bg-gray-400 text-gray-700 mx-2 w-12 h-12 rounded-[50%] border-2 border-black dark:border-gray-400'
                : 'hover:dark:bg-gray-500 dark:text-gray-200 hover:bg-gray-400 text-gray-700 mx-2 w-12 h-12 rounded-[50%]',
            }),
            current: {
              class:
                'dark:text-gray-200 text-gray-700 h-12 mx-2 rounded-[50%] flex items-center',
            },
            rowPerPageDropdown: {
              root: {
                class:
                  'flex justify-between bg-gray-400 dark:text-gray-200 text-gray-700 mx-2 px-2 align-baseline rounded',
              },
            },
            jumpToPageDropdown: {
              root: {
                class:
                  'flex hover:dark:bg-gray-500 dark:text-gray-200 hover:bg-gray-400 text-gray-700 mx-2 px-2 rounded',
              },
            },
          },
        }"
      >
        <Column
          v-for="col in props.model.filter((x) => x.visible)"
          v-bind:key="col.field"
          v-bind:field="col.field"
          v-bind:header="col.header"
          sortable
          v-bind:pt="{
            root: {
              class: 'p-2',
            },
          }"
        >
          <template v-if="col.type === 'tag'" v-slot:body="slotProps">
            <div
              v-for="tag in slotProps.data[col.field].split(',')"
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

          <template v-else-if="col.type === 'date'" v-slot:body="slotProps">
            <div class="p-1">
              {{ formatDate(slotProps.data[col.field]) }}
            </div>
          </template>
        </Column>

        <Column v-bind:exportable="false" header="">
          <template v-slot:body="slotProps">
            <div class="flex justify-between p-1">
              <div
                id="goto-button"
                class="mx-1 flex h-8 w-8 cursor-pointer items-center justify-center rounded-[50%] bg-blue-600 text-white"
                v-on:click="accountLink(slotProps.data.account_id)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke="currentColor"
                  class="h-6 w-6"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M10.343 3.94c.09-.542.56-.94 1.11-.94h1.093c.55 0 1.02.398 1.11.94l.149.894c.07.424.384.764.78.93.398.164.855.142 1.205-.108l.737-.527a1.125 1.125 0 011.45.12l.773.774c.39.389.44 1.002.12 1.45l-.527.737c-.25.35-.272.806-.107 1.204.165.397.505.71.93.78l.893.15c.543.09.94.56.94 1.109v1.094c0 .55-.397 1.02-.94 1.11l-.893.149c-.425.07-.765.383-.93.78-.165.398-.143.854.107 1.204l.527.738c.32.447.269 1.06-.12 1.45l-.774.773a1.125 1.125 0 01-1.449.12l-.738-.527c-.35-.25-.806-.272-1.203-.107-.397.165-.71.505-.781.929l-.149.894c-.09.542-.56.94-1.11.94h-1.094c-.55 0-1.019-.398-1.11-.94l-.148-.894c-.071-.424-.384-.764-.781-.93-.398-.164-.854-.142-1.204.108l-.738.527c-.447.32-1.06.269-1.45-.12l-.773-.774a1.125 1.125 0 01-.12-1.45l.527-.737c.25-.35.273-.806.108-1.204-.165-.397-.505-.71-.93-.78l-.894-.15c-.542-.09-.94-.56-.94-1.109v-1.094c0-.55.398-1.02.94-1.11l.894-.149c.424-.07.765-.383.93-.78.165-.398.143-.854-.107-1.204l-.527-.738a1.125 1.125 0 01.12-1.45l.773-.773a1.125 1.125 0 011.45-.12l.737.527c.35.25.807.272 1.204.107.397-.165.71-.505.78-.929l.15-.894z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </div>
              <div
                id="delete-button"
                class="mx-1 flex h-8 w-8 cursor-pointer items-center justify-center rounded-[50%] bg-red-600 text-white"
                v-on:click="console.log(slotProps.data.account_id)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke="currentColor"
                  class="h-6 w-6"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M15 12H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import DataTable from "primevue/datatable";
import Column from "primevue/column";

import { ref } from "vue";
import { FilterMatchMode } from "primevue/api";

import { useRouter } from "vue-router";

const router = useRouter();

const accountLink = (account_id: string) => {
  router.push(`/accounts/${account_id}`);
};

const props = defineProps({
  data: {
    type: Array<any>,
    required: true,
  },
  model: {
    type: Array<{}>,
    required: true,
  },
});

const dt = ref();
// const products = ref();

const selectedProducts = ref();
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
});

const formatDate = (value: string) => {
  if (value) {
    return new Date(value).toDateString();
  }

  return "";
};

const exportCSV = () => {
  dt.value.exportCSV();
};

const getStatusLabel = (status: string) => {
  switch (status) {
    case "NEW":
      return "bg-green-500 rounded-2xl p-2";

    case "OPEN":
      return "bg-blue-500 rounded-2xl p-2";

    case "CLOSED":
      return "bg-gray-500 rounded-2xl p-2";

    case "ON HOLD":
      return "bg-gray-500 rounded-2xl p-2";

    default:
      return getLabel(status);
  }
};

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
</script>
