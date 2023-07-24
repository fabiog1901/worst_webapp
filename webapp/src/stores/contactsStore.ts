import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { getContacts } from "@/utils/utils";

import type { ContactWithAccountName } from "@/types";

export const useStore = defineStore("contacts", () => {
  const contacts = ref<ContactWithAccountName[]>([]);

  const get_contacts = async () => {
    contacts.value = await getContacts();
  };

  const get_unique_account_names = computed(() => {
    const s = new Set<string>();
    contacts.value.forEach((x) => s.add(x.account_name));
    return Array.from(s).sort();
  });

  return {
    get_contacts,
    get_unique_account_names,
  };
});
