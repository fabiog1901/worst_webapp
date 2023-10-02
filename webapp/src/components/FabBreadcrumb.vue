<template>
  <div class="ml-2 mr-auto flex dark:text-gray-400">
    <router-link to="/">
      <div
        v-if="chain.length == 0"
        class="flex h-9 cursor-pointer items-center rounded-r-full border-2 border-gray-50 bg-green-600 p-2 text-white"
      >
        <svg
          id="home-icon"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          class="h-8 w-8"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"
          />
        </svg>
      </div>
      <div
        v-else
        class="flex h-9 cursor-pointer items-center rounded-r-full border-2 border-gray-50 bg-gray-600 p-2 text-white"
        v-on:click="$emit('clicked', ['/'])"
      >
        <svg
          id="home-icon"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          class="h-8 w-8"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"
          />
        </svg>
      </div>
    </router-link>

    <div
      v-for="x in chain"
      v-bind:key="x.name"
      class="ml-1 flex h-9 cursor-pointer items-center rounded-r-full border-2 border-gray-50 bg-gray-600 p-2 text-white last:bg-green-600"
    >
      <router-link v-bind:to="'/' + x[0] + '/' + x[1]">
        <div class="flex items-center">
          <svg
            id="home-icon"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="2"
            stroke="currentColor"
            class="h-8 w-8"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              v-bind:d="worstModels[x[0]].skema.svg_path"
            />
          </svg>
          <span class="mx-1">{{ x[2] }}</span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  // if the prop is 'modelValue', we can use v-model
  chain: {
    type: Array<any>,
    required: true,
  },
  worstModels: {
    type: Object,
    required: true,
  },
});

defineEmits(["clicked"]);
</script>
