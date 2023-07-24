import { defineStore } from "pinia";
import { ref } from "vue";

export const useUserStore = defineStore("user", () => {
  const isLoggedIn = ref(false);
  const selectedOrgs = ref<string[]>([]);
  const selectedJobTypes = ref<string[]>([]);
  const selectedDegrees = ref<string[]>([]);
  const searchTerm = ref("");

  const loginUser = () => {
    isLoggedIn.value = true;
  };

  const add_selected_orgs = (orgs: string[]) => {
    selectedOrgs.value = orgs;
  };

  const add_selected_job_types = (job_types: string[]) => {
    selectedJobTypes.value = job_types;
  };

  const add_selected_degrees = (degrees: string[]) => {
    selectedDegrees.value = degrees;
  };

  const clear_filters = () => {
    selectedDegrees.value = [];
    selectedOrgs.value = [];
    selectedJobTypes.value = [];
    searchTerm.value = "";
  };

  return {
    isLoggedIn,
    selectedOrgs,
    selectedDegrees,
    selectedJobTypes,
    searchTerm,
    loginUser,
    add_selected_orgs,
    add_selected_job_types,
    add_selected_degrees,
    clear_filters,
  };
});
