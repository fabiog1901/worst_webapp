<template>
  <div
    class="m-0 ml-16 h-screen w-80 overflow-hidden bg-gray-200 shadow-lg dark:bg-gray-800"
  >
    <div class="m-0 flex h-16 items-center justify-center p-0">
      <h5
        class="justify-center align-middle text-3xl tracking-wider text-gray-600 dark:text-gray-400"
      >
        Accounts
      </h5>
    </div>

    <div class="m-0 flex flex-col items-center justify-start p-1">
      <section class="pb-5">
        <label
          class="h-12 flex-auto pl-3 text-sm text-gray-600 dark:text-gray-400"
          >Owned By</label
        >
        <div class="flex">
          <select v-model="owned_by" class="flex flex-auto">
            <option
              v-for="x in store.get_unique_account_owners"
              v-bind:key="x"
              v-bind:value="x"
            >
              {{ x }}
            </option>
          </select>
        </div>

        <!--<div class="flex justify-between">
          <h3
            class="my-4 text-base font-semibold text-gray-600 dark:text-gray-400"
          >
            What do you want to do?
          </h3>
          <div class="flex items-center text-sm">
            <action-button
              text="Clear Filters"
              btn-type="secondary"
              v-on:click="store.clear_filters()"
            />
          </div>
        </div>

        <div class="mt-2 flex">
          <input
            v-model.lazy.trim="store.searchTerm"
            type="text"
            class="border-brand-gray-1 shadow-gray h-12 flex-auto rounded border border-solid pl-3 text-sm"
            placeholder="Computer programming"
          />
        </div>

         <collapsible-accordion header="Owner">
          <div class="mt-5">
            <fieldset>
              <ul class="flex flex-wrap">
                <li v-for="x in UNIQUE_DEGREES" v-bind:key="x" class="h8 w-1/2">
                  <input
                    v-bind:id="x"
                    v-model="store.selectedDegrees"
                    v-bind:value="x"
                    type="checkbox"
                    class="mr-3"
                    v-on:change="
                      store.add_selected_degrees(store.selectedDegrees);
                      backToPageOne();
                    "
                  />
                  <label v-bind:for="x">{{ x }}</label>
                </li>
              </ul>
            </fieldset>
          </div>
        </collapsible-accordion>

        <collapsible-accordion header="Job Type">
          <div class="mt-5">
            <fieldset>
              <ul class="flex flex-wrap">
                <li
                  v-for="x in UNIQUE_JOB_TYPES"
                  v-bind:key="x"
                  class="h8 w-1/2"
                >
                  <input
                    v-bind:id="x"
                    v-model="store.selectedJobTypes"
                    v-bind:value="x"
                    type="checkbox"
                    class="mr-3"
                    v-on:change="
                      store.add_selected_job_types(store.selectedJobTypes);
                      backToPageOne();
                    "
                  />
                  <label v-bind:for="x">{{ x }}</label>
                </li>
              </ul>
            </fieldset>
          </div>
        </collapsible-accordion>

        <collapsible-accordion header="Organization">
          <div class="mt-5">
            <fieldset>
              <ul class="flex flex-wrap">
                <li
                  v-for="x in UNIQUE_ORGANIZATIONS"
                  v-bind:key="x"
                  class="h8 w-1/2"
                >
                  <input
                    v-bind:id="x"
                    v-model="store.selectedOrgs"
                    v-bind:value="x"
                    type="checkbox"
                    class="mr-3"
                    v-on:change="
                      store.add_selected_orgs(store.selectedOrgs);
                      backToPageOne();
                    "
                  />
                  <label v-bind:for="x">{{ x }}</label>
                </li>
              </ul>
            </fieldset>
          </div>
        </collapsible-accordion> -->
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import ActionButton from "@/components/ActionButton.vue";
import CollapsibleAccordion from "@/components/CollapsibleAccordion.vue";

import { useRouter } from "vue-router";
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import { useStore } from "@/stores/accountsStore";

const owned_by = ref("");

const store = useStore();
const router = useRouter();

onMounted(() => {
  store.get_accounts();

  const route = useRoute();

  // store.searchTerm = route.query.role as string;
});
</script>
