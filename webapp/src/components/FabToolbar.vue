<template>
  <div
    id="toolbar"
    class="m-2 flex justify-between rounded border-2 border-gray-500 bg-gray-200 p-2 dark:border-gray-500 dark:bg-gray-700"
  >
    <div
      id="new-button"
      class="mx-2 flex cursor-pointer items-center rounded-xl hover:bg-blue-400 bg-blue-600 p-2 text-white"
      v-on:click="$emit('new-clicked')"
    >
      <span class="mx-1">New</span>
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
    </div>
    <div
      id="delete-button"
      class="mx-2 flex cursor-pointer items-center justify-between rounded-xl hover:bg-green-400 bg-red-600 p-2 text-white"
      v-on:click="$emit('delete-clicked')"
    >
      <span class="mx-1">Delete</span>
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
    </div>
    <div
      id="query-input"
      class="ml-2 flex cursor-pointer items-center rounded-xl bg-gray-300 p-2 text-gray-600"
    >
      <input
        class="mx-2 w-640 rounded px-2"
        placeholder="Filter by keyword..."
        v-model="keyword"
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
      class="mx-2 ml-auto flex cursor-pointer rounded-xl hover:bg-green-400 bg-green-600 p-2 text-white"
      v-on:click="$emit('export-clicked')"
    >
      <span class="mx-1" value="Mona">Export</span>
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
    </div>
  </div>
</template>

<script setup lang="ts">


const keyword = defineModel()

defineEmits(["new-clicked", "delete-clicked", "export-clicked"]);
</script>
