<template>
  <button v-bind:class="buttonClass">
    {{ text }}
  </button>
</template>

<script setup lang="ts">
import { computed, toRefs } from "vue";

const props = defineProps({
  text: {
    type: String,
    required: true,
  },
  btnType: {
    type: String,
    required: false,
    default: "primary",
    validator(value: string) {
      return ["primary", "secondary"].includes(value);
    },
  },
});

const { btnType } = toRefs(props);

const buttonClass = computed(() => {
  return {
    [btnType.value]: true,
  };
});
</script>

<style scoped>
button {
  @apply px-5 py-3 font-medium;
}

.primary {
  @apply rounded bg-blue-700 text-white hover:shadow-blue-200;
}

.secondary {
  @apply bg-transparent text-blue-700 hover:bg-blue-200 hover:text-white;
}
</style>
