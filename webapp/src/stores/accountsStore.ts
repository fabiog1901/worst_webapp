import { defineStore } from "pinia";
import { computed, ref } from "vue";
import axios from "axios";
import type { AccountOverview } from "@/types";

export const useStore = defineStore("accounts", () => {
  const accounts = ref<AccountOverview[]>([]);

  const account_model = ref({});

  const acc_cols = computed(() => Object.keys(account_model.value));

  const filterKey = ref("");

  const get_all_accounts = async () => {
    const r = await axios.get<AccountOverview[]>(
      `${import.meta.env.VITE_APP_API_URL}/account-overview`
    );
    accounts.value = r.data;
  };

  const get_account_model = async () => {
    const r = await axios.get(
      `${import.meta.env.VITE_APP_API_URL}/account-model`
    );
    account_model.value = r.data;
  };

  const get_unique_account_owners = computed(() => {
    const s = new Set<string>();
    accounts.value.forEach((acc) => s.add(acc.owned_by));
    return Array.from(s).sort();
  });

  return {
    accounts,
    account_model,
    acc_cols,
    filterKey,
    get_all_accounts,
    get_account_model,
    get_unique_account_owners,
  };
});
