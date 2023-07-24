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
        <div class="flex justify-between">
          <h3
            class="my-4 text-base font-semibold text-gray-600 dark:text-gray-400"
          >
            What do you want to do?
          </h3>
          <div class="flex items-center text-sm">
            <action-button
              text="Clear Filters"
              btn-type="secondary"
              v-on:click="userStore.clear_filters()"
            />
          </div>
        </div>

        <div class="mt-2 flex">
          <input
            v-model.lazy.trim="userStore.searchTerm"
            type="text"
            class="border-brand-gray-1 shadow-gray h-12 flex-auto rounded border border-solid pl-3 text-sm"
            placeholder="Computer programming"
          />
        </div>

        <collapsible-accordion header="Degree">
          <div class="mt-5">
            <fieldset>
              <ul class="flex flex-wrap">
                <li v-for="x in UNIQUE_DEGREES" v-bind:key="x" class="h8 w-1/2">
                  <input
                    v-bind:id="x"
                    v-model="userStore.selectedDegrees"
                    v-bind:value="x"
                    type="checkbox"
                    class="mr-3"
                    v-on:change="
                      userStore.add_selected_degrees(userStore.selectedDegrees);
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
                    v-model="userStore.selectedJobTypes"
                    v-bind:value="x"
                    type="checkbox"
                    class="mr-3"
                    v-on:change="
                      userStore.add_selected_job_types(
                        userStore.selectedJobTypes
                      );
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
                    v-model="userStore.selectedOrgs"
                    v-bind:value="x"
                    type="checkbox"
                    class="mr-3"
                    v-on:change="
                      userStore.add_selected_orgs(userStore.selectedOrgs);
                      backToPageOne();
                    "
                  />
                  <label v-bind:for="x">{{ x }}</label>
                </li>
              </ul>
            </fieldset>
          </div>
        </collapsible-accordion>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import ActionButton from "@/components/ActionButton.vue";
import CollapsibleAccordion from "@/components/CollapsibleAccordion.vue";

import { useRouter } from "vue-router";
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";

// import { useJobsStore } from "@/stores/jobs";
import { useUserStore } from "@/stores/user";
// import { useDegreeStore } from "@/stores/degree";

const userStore = useUserStore();
// const jobsStore = useJobsStore();
// const degreeStore = useDegreeStore();

const router = useRouter();

// const UNIQUE_ORGANIZATIONS = computed(() => jobsStore.get_unique_orgs);
// const UNIQUE_JOB_TYPES = computed(() => jobsStore.get_unique_job_types);
// const UNIQUE_DEGREES = computed(() => degreeStore.get_unique_degrees);

onMounted(() => {
  const route = useRoute();
  userStore.searchTerm = route.query.role as string;
});

const backToPageOne = () => {
  router.push({ name: "JobResults" });
};
</script>
