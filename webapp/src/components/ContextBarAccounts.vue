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

        <label
          class="h-12 flex-auto pl-3 text-sm text-gray-600 dark:text-gray-400"
          >Owned By</label
        >
        <div class="flex">
          <select
            v-model="store.selectedOwners"
            class="flex flex-auto"
            multiple
            v-on:change="store.add_selected_owners(store.selectedOwners)"
          >
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
import { onMounted } from "vue";
import { useStore } from "@/stores/accountsStore";

const store = useStore();

onMounted(() => {});
</script>
