import { defineStore } from "pinia";
import { computed, ref } from "vue";
import axios from "axios";

import type { ContactWithAccountName } from "@/types";

export const useStore = defineStore("contacts", () => {
  const contacts = ref<ContactWithAccountName[]>([]);

  const get_all_contacts = async () => {
    const r = await axios.get<ContactWithAccountName[]>(
      `${import.meta.env.VITE_APP_API_URL}/contacts`
    );
    contacts.value = r.data;
  };

  const get_unique_account_names = computed(() => {
    const s = new Set<string>();
    contacts.value.forEach((x) => s.add(x.account_name));
    return Array.from(s).sort();
  });

  return {
    get_all_contacts,
    get_unique_account_names,
  };
});
