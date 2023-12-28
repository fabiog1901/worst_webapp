<template>
  <VMarkdownView v-bind:content="source" v-bind:mode="theme" />
</template>

<script setup lang="ts">
import { VMarkdownView } from "vue3-markdown";
import "vue3-markdown/dist/style.css";

defineProps({
  source: {
    type: String,
    default: "",
  },
  theme: {
    type: String,
    default: "dark",
  },
});
</script>
