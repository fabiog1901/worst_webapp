<template>
  <VMarkdownEditor v-model="source" locale="en" />
</template>

<script setup lang="ts">
import { VMarkdownEditor } from "vue3-markdown";
import "vue3-markdown/dist/style.css";

const source = defineModel();
</script>
