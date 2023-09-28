import { ref, computed } from "vue";
import { defineStore } from "pinia";

import axios from "axios";
import { useAuthStore } from "@/stores/authStore";

import type { Model } from "@/types";

export const useModelStore = defineStore("model", () => {
  const worst_models: { [key: string]: any } = ref<{}>({});
  const model_instances = ref<Model[]>([]);

  const selectedOwners = ref<string[]>([]);

  const authStore = useAuthStore();

  const fetch_all_worst_models = async () => {
    const r = await axios.get<{}>(
      `${import.meta.env.VITE_APP_API_URL}/admin/models`,
      { headers: { Authorization: `Bearer ${authStore.user.access_token}` } }
    );
    console.info("modelStore: fetched all worst_models");
    worst_models.value = r.data;
  };

  const fetch_all_instances = async (model_name: string) => {
    const r = await axios.get<Model[]>(
      `${import.meta.env.VITE_APP_API_URL}/${model_name}`,
      { headers: { Authorization: `Bearer ${authStore.user.access_token}` } }
    );
    console.info(`modelStore: fetched all instances for '${model_name}'`);
    model_instances.value = r.data;
  };

  const add_selected_owners = (owners: string[]) => {
    selectedOwners.value = owners;
  };
  const get_unique_owners = computed(() => {
    const s = new Set<string>();
    model_instances.value.forEach((instance) => s.add(instance.owned_by));
    return Array.from(s).sort();
  });

  const clear_filters = () => {
    selectedOwners.value = [];
  };

  const include_models_by_owners = (x: Model) => {
    if (selectedOwners.value.length === 0) return true;
    return selectedOwners.value.includes(x.owned_by);
  };

  const get_filtered_models = () => {
    // console.log(model_instances.value.filter((x) => include_models_by_owners(x)));
    return model_instances.value.filter((x) => include_models_by_owners(x));
  };

  return {
    get_filtered_models,
    clear_filters,
    add_selected_owners,
    get_unique_owners,
    fetch_all_worst_models,
    worst_models,
    fetch_all_instances,
    model_instances,
  };
});
