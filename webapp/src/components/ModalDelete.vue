<template>
  <div
    class="fixed left-0 top-0 z-10 flex h-full w-full items-center justify-center"
  >
    <div
      class="absolute h-full w-full bg-gray-900 opacity-50"
      v-on:click="$emit('cancel-clicked')"
    ></div>

    <div class="absolute max-h-full max-w-xl">
      <div class="container overflow-hidden bg-white md:rounded">
        <div
          class="flex select-none items-center justify-between border-b bg-gray-100 px-4 py-4 text-sm font-medium leading-none"
        >
          <h3 class="text-2xl">Delete {{ props.modelName }}</h3>
          <div
            class="cursor-pointer text-2xl hover:text-gray-600"
            v-on:click="$emit('cancel-clicked')"
          >
            &#215;
          </div>
        </div>

        <div class="max-h-full px-4 py-4">
          <p class="text-gray-800">
            Are you sure you want to delete {{ props.modelName }}:
            <span class="font-semibold">{{ props.instanceName }}</span>
            ?
          </p>

          <div class="mt-4 text-right">
            <button
              class="px-4 py-2 text-sm text-gray-600 hover:underline focus:outline-none"
              v-on:click="$emit('cancel-clicked')"
            >
              Cancel
            </button>
            <button
              class="mr-2 rounded bg-red-500 px-4 py-2 text-sm text-white hover:bg-red-400 focus:outline-none"
              v-on:click="$emit('delete-clicked')"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits(["delete-clicked", "cancel-clicked"]);

const props = defineProps({
  modelName: {
    type: String,
    required: true,
  },
  instanceName: {
    type: String,
    required: true,
  },
});
</script>

<style scoped>
/* .my-tag {
  @apply m-2 w-auto min-w-max origin-left scale-0 rounded-md
    bg-gray-900 p-2 
    text-xs font-bold 
    text-white shadow-md transition-all duration-100;
} */
</style>
