<template>
  <h1>Account View ID: {{ account_id }}</h1>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

const account_id = computed(() => {
  return useRoute().params.account_id;
});
</script>
