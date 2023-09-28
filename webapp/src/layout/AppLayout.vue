<template>
  <div class="flex h-screen flex-col">
    <AppHeader />

    <div class="flex flex-grow">
      <AppSidebar />
      <div class="flex w-full">
        <router-view></router-view>
      </div>
    </div>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import AppSidebar from "@/layout/AppSidebar.vue";
import AppHeader from "@/layout/AppHeader.vue";
import AppFooter from "@/layout/AppFooter.vue";
</script>
