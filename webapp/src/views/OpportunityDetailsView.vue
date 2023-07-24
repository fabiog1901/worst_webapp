<template>
  <h1>Opp View ID: {{ account_id }} / {{ opportunity_id }}</h1>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

const account_id = computed(() => {
  return useRoute().params.account_id;
});
const opportunity_id = computed(() => {
  return useRoute().params.opportunity_id;
});
</script>
