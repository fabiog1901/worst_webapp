import { computed, ref } from "vue";
import { defineStore } from "pinia";

import axios from "axios";

import type { Model, Account } from "@/types";

export const useAdminStore = defineStore("admin", () => {
  const accounts = ref<AccountOverview[]>([]);
  const account_model = ref([]);

  const selectedOwners = ref<string[]>([]);

  const fetch_all_models = async () => {
    const r = await axios.get<Model[]>(
      `${import.meta.env.VITE_APP_API_URL}/account-overview`
    );
    console.info("accountStore: fetched all accounts");
    accounts.value = r.data;
  };

  const fetch_account = async (account_id: string) => {
    const r = await axios.get<Account>(
      // `${import.meta.env.VITE_APP_API_URL}/account/${account_id}`
      `${import.meta.env.VITE_APP_API_URL}/account`
    );
    console.info(`accountStore: fetched account ${account_id}`);
    return r.data;
  };

  const fetch_account_model = async () => {
    const r = await axios.get(
      `${import.meta.env.VITE_APP_API_URL}/account-model`
    );
    console.info("accountStore: fetched account model");
    account_model.value = r.data;
  };

  const add_selected_owners = (owners: string[]) => {
    selectedOwners.value = owners;
  };
  const get_unique_account_owners = computed(() => {
    const s = new Set<string>();
    accounts.value.forEach((acc) => s.add(acc.owned_by));
    return Array.from(s).sort();
  });

  const clear_filters = () => {
    selectedOwners.value = [];
  };

  const include_accounts_by_owners = (x: AccountOverview) => {
    if (selectedOwners.value.length === 0) return true;
    return selectedOwners.value.includes(x.owned_by);
  };

  const get_filtered_accounts = () => {
    return accounts.value.filter((x) => include_accounts_by_owners(x));
  };

  return {
    fetch_all_accounts,
    fetch_account,
    fetch_account_model,
    accounts,
    account_model,
    selectedOwners,
    clear_filters,
    add_selected_owners,
    get_unique_account_owners,
    get_filtered_accounts,
  };
});
