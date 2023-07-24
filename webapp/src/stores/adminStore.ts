import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { getAccounts, getOpportunities, getContacts } from "@/utils/utils";

import type { Account, Opportunity, Contact } from "@/types";

export const useStore = defineStore("store", () => {
  const isLoggedIn = ref(false);
  const selectedOrgs = ref<string[]>([]);
  const selectedJobTypes = ref<string[]>([]);
  const selectedDegrees = ref<string[]>([]);
  const searchTerm = ref("");

  const accounts = ref<Account[]>([]);
  const opportunities = ref<Opportunity[]>([]);
  const contacts = ref<Contact[]>([]);

  const get_accounts = async () => {
    accounts.value = await getAccounts();
  };

  const get_opportunities = async () => {
    opportunities.value = await getOpportunities();
  };

  const get_contacts = async () => {
    contacts.value = await getContacts();
  };

  const get_unique_account_owners = computed(() => {
    const s = new Set<string>();
    accounts.value.forEach((acc) => s.add(acc.owned_by));
    return Array.from(s).sort();
  });

  const get_unique_opportunity_owners = computed(() => {
    const s = new Set<string>();
    opportunities.value.forEach((opp) => s.add(opp.owned_by));
    return Array.from(s).sort();
  });

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
    accounts,
    get_accounts,
    get_opportunities,
    get_contacts,
    get_unique_opportunity_owners,
    get_unique_account_owners,
    loginUser,
    add_selected_orgs,
    add_selected_job_types,
    add_selected_degrees,
    clear_filters,
  };
});
