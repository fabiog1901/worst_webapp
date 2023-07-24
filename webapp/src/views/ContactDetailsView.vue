<template>
  <h1>JobView {{ currentJobId }}</h1>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

const currentJobId = computed(() => {
  return useRoute().params.job_id;
});
</script>
