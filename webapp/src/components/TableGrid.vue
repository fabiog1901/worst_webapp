<template>
  <div class="mx-8 my-8">
    <table v-if="filteredData.length" class="text-sm">
      <thead>
        <tr>
          <th
            v-for="x in columns"
            v-bind:key="x"
            class="min-w-[120px] cursor-pointer bg-gray-200 px-5 py-2.5 text-gray-600 dark:bg-gray-600 dark:text-gray-200"
            v-bind:class="sortKey == x ? 'underline' : ''"
            v-on:click="sortBy(x)"
          >
            {{ capitalize(x) }}

            <svg
              v-if="sortOrders[x] > 0"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="h-4 w-4"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M19.5 8.25l-7.5 7.5-7.5-7.5"
              />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="h-4 w-4"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M4.5 15.75l7.5-7.5 7.5 7.5"
              />
            </svg>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="entry in filteredData"
          v-bind:key="entry"
          class="top-navigation-icon"
          v-on:click="
            () => {
              console.log(entry['account_id']);
            }
          "
        >
          <td
            v-for="x in columns"
            v-bind:key="x"
            class="min-w-[120px] border-b-2 border-r-2 bg-gray-100 px-5 py-2.5 text-gray-600 dark:bg-gray-500 dark:text-gray-200"
          >
            {{ entry[x] }}
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else>No matches found.</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

const props = defineProps({
  data: {
    type: Array<any>,
    required: true,
  },
  columns: {
    type: Array<string>,
    required: true,
  },
  filterKey: {
    type: String,
    default: "",
  },
});

const sortKey = ref("");

const sortOrders = ref(
  props.columns.reduce((o: any, key: string) => ((o[key] = 1), o), {})
);

const filteredData = computed(() => {
  let { data, filterKey } = props;
  if (filterKey) {
    filterKey = filterKey.toLowerCase();
    data = data.filter((row) => {
      return Object.keys(row).some((key) => {
        return String(row[key]).toLowerCase().indexOf(filterKey) > -1;
      });
    });
  }
  const key = sortKey.value;
  if (key) {
    const order = sortOrders.value[key];
    data = data.slice().sort((a, b) => {
      a = a[key];
      b = b[key];
      return (a === b ? 0 : a > b ? 1 : -1) * order;
    });
  }
  return data;
});

function sortBy(key: string) {
  console.log("sorting by " + key);
  sortKey.value = key;
  sortOrders.value[key] *= -1;
}

function capitalize(str: string) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
</script>

<style>
.top-navigation-icon {
  @apply ml-4
    mr-3 cursor-pointer
    text-gray-600 transition duration-300 ease-in-out 
    hover:text-pink-400 dark:text-gray-400 
    dark:hover:text-pink-400;
}

.arrow {
  @apply ml-[5px] inline-block h-0 w-0 align-middle opacity-[0.66];
}

.arrow.asc {
  @apply border-x-4 border-b-4 border-solid border-x-transparent border-b-[#070707];
}

.arrow.dsc {
  @apply border-x-4 border-t-4 border-solid border-x-transparent border-t-[#020202];
}
</style>
