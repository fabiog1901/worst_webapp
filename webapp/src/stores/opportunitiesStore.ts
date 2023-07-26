import { defineStore } from "pinia";
import { computed, ref } from "vue";
import axios from "axios";

import type { OpportunityOverviewWithAccountName } from "@/types";

export const useStore = defineStore("opportunities", () => {
  const opportunities = ref<OpportunityOverviewWithAccountName[]>([]);

  const get_all_opportunities = async () => {
    const r = await axios.get<OpportunityOverviewWithAccountName[]>(
      `${import.meta.env.VITE_APP_API_URL}/opportunities`
    );
    opportunities.value = r.data;
  };

  const get_unique_opportunity_owners = computed(() => {
    const s = new Set<string>();
    opportunities.value.forEach((opp) => s.add(opp.owned_by));
    return Array.from(s).sort();
  });

  return {
    get_all_opportunities,
    get_unique_opportunity_owners,
  };
});
