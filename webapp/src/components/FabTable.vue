<template>
  <section class="h-full">
    <FabToolbar
      v-model="filters['global'].value"
      v-on:new="$emit('new-clicked')"
      v-on:delete="$emit('delete-clicked')"
      v-on:export="exportCSV()"
    />

    <DataTable
      ref="dt"
      v-model:selection="selectedProducts"
      v-bind:value="props.data"
      v-bind:paginator="true"
      v-bind:rows="25"
      v-bind:filters="filters"
      scrollable
      scroll-height="600px"
      paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport JumpToPageDropdown RowsPerPageDropdown"
      v-bind:rows-per-page-options="[5, 10, 25]"
      current-page-report-template="Showing {first} to {last} of {totalRecords}"
      v-bind:pt="{
        root: {
          class: 'rounded mx-2 border-solid dark:bg-gray-700 bg-gray-200',
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
      <!-- <Column
        field="name"
        header="Name"
        sortable
        v-bind:pt="{
          root: {
            class: 'p-2',
          },
        }"
      >
      </Column> -->

      <Column
        v-for="col in props.modelFields
          .concat(modelDefaultFields)
          .filter((x) => x.in_overview)"
        v-bind:key="col.name"
        v-bind:field="col.name"
        v-bind:header="col.name.toUpperCase()"
        sortable
        v-bind:pt="{
          root: {
            class: 'p-2',
          },
        }"
      >
        <template v-if="col.type === 'tag'" v-slot:body="slotProps">
          <div
            v-for="tag in slotProps.data[col.name]"
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
        </template>

        <template v-else-if="col.type === 'date'" v-slot:body="slotProps">
          <div class="p-1">
            {{ formatDate(slotProps.data[col.name]) }}
          </div>
        </template>
      </Column>

      <Column v-bind:exportable="false" header="">
        <template v-slot:body="slotProps">
          <div class="flex justify-between p-1">
            <div
              id="goto-button"
              class="group mx-1 flex h-8 w-8 cursor-pointer items-center justify-center rounded-[50%] bg-blue-600 text-white"
              v-on:click="$emit('row-clicked', slotProps.data)"
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
                  d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"
                />
              </svg>
              <!-- <span class="sidebar-tooltip group-hover:scale-100">Edit</span> -->
            </div>
            <div
              id="delete-button"
              class="group mx-1 flex h-8 w-8 cursor-pointer items-center justify-center rounded-[50%] bg-red-600 text-white"
              v-on:click="$emit('delete-clicked', slotProps.data)"
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
              <!-- <span class="sidebar-tooltip group-hover:scale-100">Delete</span> -->
            </div>
          </div>
        </template>
      </Column>
    </DataTable>
  </section>
</template>

<script setup lang="ts">
import { FilterMatchMode } from "primevue/api";
import { ref } from "vue";

import Column from "primevue/column";
import DataTable from "primevue/datatable";
import FabToolbar from "@/components/FabToolbar.vue";

import { formatDate, getLabel, formatDecimal } from "@/utils/utils";

defineEmits(["row-clicked", "delete-clicked", "new-clicked"]);

const props = defineProps({
  data: {
    type: Array<any>,
    required: true,
  },
  modelFields: {
    type: Array<any>,
    required: true,
  },
  modelDefaultFields: {
    type: Array<any>,
    required: true,
  },
});

const dt = ref();

const selectedProducts = ref();
const filters = ref({
  global: { value: "", matchMode: FilterMatchMode.CONTAINS },
});

const exportCSV = () => {
  dt.value.exportCSV();
};
</script>

<style scoped>
/* .sidebar-tooltip {
  @apply relative left-10 m-2 w-auto min-w-max origin-left scale-0 rounded-md
    bg-gray-900 p-2 
    text-xs font-bold 
    text-white shadow-md transition-all duration-100;
} */
</style>
