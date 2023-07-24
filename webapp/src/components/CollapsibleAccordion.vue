<template>
  <div class="border-brand-gray-1 border-b border-solid py-5">
    <div
      class="flex cursor-pointer flex-wrap items-center justify-between"
      v-on:click="open"
    >
      <h3 class="text-base font-semibold text-gray-600 dark:text-gray-400">
        {{ header }}
      </h3>
      <span v-if="isOpen" class="text-gray-600 dark:text-gray-400"
        ><svg
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
            d="M19.5 8.25l-7.5 7.5-7.5-7.5"
          />
        </svg>
      </span>
      <span v-else class="text-gray-600 dark:text-gray-400"
        ><svg
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
            d="M4.5 15.75l7.5-7.5 7.5 7.5"
          />
        </svg>
      </span>
    </div>

    <div v-if="isOpen" class="mt-5 w-full">
      <slot>
        <p>Pippo!</p>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

defineProps({
  header: {
    type: String,
    required: true,
  },
});

const isOpen = ref(false);

const open = () => {
  isOpen.value = !isOpen.value;
};
</script>
