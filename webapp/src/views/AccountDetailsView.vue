<template>
  <div class="flex">
    <ContextBarAccounts />
    <h1>{{ account_id }}</h1>
  </div>
</template>



<script setup lang="ts">
import ContextBarAccounts from "@/components/ContextBarAccounts.vue";
import ContentContainer from "@/components/ContentContainer.vue";

import { computed } from "vue";
import { useRoute } from "vue-router";

const account_id = computed(() => {
  return useRoute().params.account_id;
});
</script>
