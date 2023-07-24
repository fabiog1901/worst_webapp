import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { getAccounts } from "@/utils/utils";

import type { Account } from "@/types";

export const useStore = defineStore("accounts", () => {
  const accounts = ref<Account[]>([]);

  const get_accounts = async () => {
    accounts.value = await getAccounts();
  };

  const get_unique_account_owners = computed(() => {
    const s = new Set<string>();
    accounts.value.forEach((acc) => s.add(acc.owned_by));
    return Array.from(s).sort();
  });

  return {
    get_accounts,
    get_unique_account_owners,
  };
});
