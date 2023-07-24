import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { getOpportunities } from "@/utils/utils";

import type { Opportunity } from "@/types";

export const useStore = defineStore("opportunities", () => {
  const opportunities = ref<Opportunity[]>([]);

  const get_opportunities = async () => {
    opportunities.value = await getOpportunities();
  };

  const get_unique_opportunity_owners = computed(() => {
    const s = new Set<string>();
    opportunities.value.forEach((opp) => s.add(opp.owned_by));
    return Array.from(s).sort();
  });

  return {
    get_opportunities,
    get_unique_opportunity_owners,
  };
});
