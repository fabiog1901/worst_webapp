<template>
  <div
    class="m-0 flex h-full w-full flex-col overflow-hidden bg-gray-300 dark:bg-gray-700"
  >
    <TopNavigation />
    <div
      class="mx-auto ml-0 mt-0 flex h-screen w-full flex-col items-center overflow-y-scroll px-0 pb-12"
    ></div>
    <div
      class="fixed bottom-2 left-88 right-8 flex h-12 flex-row items-center justify-between rounded-lg bg-gray-400 px-2 shadow-lg dark:bg-gray-600"
    >
      <input
        type="text"
        placeholder="Enter message..."
        class="ml-0 mr-auto w-full cursor-text bg-transparent font-semibold text-gray-600 placeholder-gray-500 outline-none dark:text-gray-200"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import TopNavigation from "@/components/TopNavigation.vue";
</script>
