<template>
  <section class="flex">
    <section id="context-bar" class="flex">
      <div
        class="m-0 ml-16 h-screen w-80 overflow-hidden bg-gray-200 shadow-lg dark:bg-gray-700"
      >
        <div class="m-0 flex h-16 items-center justify-center p-0">
          <h5
            class="justify-center align-middle text-3xl tracking-wider text-gray-600 dark:text-gray-400"
          >
            {{ account.name }}
          </h5>
        </div>

        <div class="m-0 flex flex-col items-center justify-start p-1">
          <section class="pb-5">
            <div
              id="clear-filter-button"
              class="mx-8 mb-2 flex cursor-pointer items-center justify-between rounded-xl bg-gray-600 p-2 text-white"
              v-on:click="store.clear_filters"
            >
              <svg
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
                  d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 01-.659 1.591l-5.432 5.432a2.25 2.25 0 00-.659 1.591v2.927a2.25 2.25 0 01-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 00-.659-1.591L3.659 7.409A2.25 2.25 0 013 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0112 3z"
                />
              </svg>
              <span class="mx-1">Clear Filters</span>
            </div>
          </section>
        </div>
      </div>
    </section>

    <div class="flex flex-col">
      <div class="text-900 mb-3 text-3xl font-medium">Movie Information</div>
      <div class="text-500 mb-5">
        Morbi tristique blandit turpis. In viverra ligula id nulla hendrerit
        rutrum.
      </div>
      <ul class="m-0 list-none p-0">
        <li
          class="align-items-center border-top-1 flex justify-between px-2 py-3"
        >
          <div class="bg-teal-400 font-medium">Title</div>
          <div class="bg-orange-500">Heat</div>

          <span
            v-show="!editing"
            class="h-12 w-44 bg-blue-500"
            v-on:dblclick="editing = !editing"
          >
            <label for="value">{{ value }}</label>
          </span>
          <span v-show="editing" class="bg-gray-300">
            <input
              focus="true"
              class="h-12"
              v-bind:value="value"
              type="text"
              v-on:input="value = $event.target.value"
              v-on:focusout="editing = !editing"
            />
          </span>

          <div class="justify-content-end flex">
            <div class="h-12 w-12 bg-red-700" v-on:click="editing = !editing">
              <svg
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
                  d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"
                />
              </svg>
            </div>
          </div>
        </li>
        <!-- <li
          class="align-items-center border-top-1 surface-border flex flex-wrap px-2 py-3"
        >
          <div class="text-500 w-6 font-medium md:w-2">Genre</div>
          <div class="text-900 md:flex-order-0 flex-order-1 w-full md:w-8">
            <Chip label="Crime" class="mr-2"></Chip>
            <Chip label="Drama" class="mr-2"></Chip>
            <Chip label="Thriller"></Chip>
          </div>
          <div class="justify-content-end flex w-6 md:w-2">
            <Button
              label="Edit"
              icon="pi pi-pencil"
              class="p-button-text"
            ></Button>
          </div>
        </li>
        <li
          class="align-items-center border-top-1 surface-border flex flex-wrap px-2 py-3"
        >
          <div class="text-500 w-6 font-medium md:w-2">Director</div>
          <div class="text-900 md:flex-order-0 flex-order-1 w-full md:w-8">
            Michael Mann
          </div>
          <div class="justify-content-end flex w-6 md:w-2">
            <Button
              label="Edit"
              icon="pi pi-pencil"
              class="p-button-text"
            ></Button>
          </div>
        </li>
        <li
          class="align-items-center border-top-1 surface-border flex flex-wrap px-2 py-3"
        >
          <div class="text-500 w-6 font-medium md:w-2">Actors</div>
          <div class="text-900 md:flex-order-0 flex-order-1 w-full md:w-8">
            Robert De Niro, Al Pacino
          </div>
          <div class="justify-content-end flex w-6 md:w-2">
            <Button
              label="Edit"
              icon="pi pi-pencil"
              class="p-button-text"
            ></Button>
          </div>
        </li>
        <li
          class="align-items-center border-top-1 border-bottom-1 surface-border flex flex-wrap px-2 py-3"
        >
          <div class="text-500 w-6 font-medium md:w-2">Plot</div>
          <div
            class="text-900 md:flex-order-0 flex-order-1 line-height-3 w-full md:w-8"
          >
            A group of professional bank robbers start to feel the heat from
            police when they unknowingly leave a clue at their latest heist.
          </div>
          <div class="justify-content-end flex w-6 md:w-2">
            <Button
              label="Edit"
              icon="pi pi-pencil"
              class="p-button-text"
            ></Button>
          </div>
        </li> -->
      </ul>
    </div>
    <!-- <section
      id="content-container"
      class="flex h-full w-full flex-col bg-gray-300 dark:bg-gray-700"
    >
      <TopNav />

      <div class="text-gray-200">

        
        <div class="text-3xl font-semibold">Description</div>
        <div>
          {{ account.text }}
        </div>
      </div>

      <BottomNav />
    </section> -->
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { onMounted } from "vue";
import { useStore } from "@/stores/accountsStore";
import { useRoute, useRouter } from "vue-router";

import BottomNav from "@/components/BottomNav.vue";
import TopNav from "@/components/TopNav.vue";

import Button from "primevue/button";
import Chip from "primevue/button";

import type { Account } from "@/types";

const store = useStore();

const editing = ref<boolean>(false);
const value = ref("");

const router = useRouter();

const account_id = computed(() => {
  return useRoute().params.account_id;
});

const account = ref<Account>({});

onMounted(async () => {
  account.value = await store.fetch_account(account_id.value);
});
</script>
