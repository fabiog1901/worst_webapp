import { ref, computed } from "vue";
import { defineStore } from "pinia";

import { axiosWrapper } from "@/utils/utils";

import type { Model } from "@/types";

export const useModelStore = defineStore("model", () => {
  const worst_models: { [key: string]: any } = ref<{}>({});
  const model_instances = ref<Model[]>([]);
  const model_instance = ref<Model>();
  const model_instance_children = ref<any>();
  const model_instance_parent_chain = ref<any[]>([]);

  const selectedOwners = ref<string[]>([]);

  const fetch_all_worst_models = async () => {
    worst_models.value = await axiosWrapper.get(`/admin/models`);
    console.info("modelStore::fetch_all_worst_models");
  };

  const fetch_all_instances = async (model_name: string) => {
    model_instances.value = await axiosWrapper.get(`/${model_name}`);
    console.info(`modelStore::fetch_all_instances(${model_name})`);
  };

  const fetch_instance = async (model_name: string, id: string) => {
    model_instance.value = await axiosWrapper.get(`/${model_name}/${id}`);
    console.info(`modelStore::fetch_instance(${model_name}, ${id})`);
  };

  const fetch_instance_children = async (model_name: string, id: string) => {
    model_instance_children.value = await axiosWrapper.get(
      `/${model_name}/${id}/children`
    );
    console.info(`modelStore::fetch_instance_children(${model_name}, ${id})`);
  };

  const fetch_parent_chain = async (model_name: string, id: string) => {
    model_instance_parent_chain.value = await axiosWrapper.get(
      `/${model_name}/${id}/parent_chain`
    );
    console.info(`modelStore::fetch_parent_chain(${model_name}, ${id})`);
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
    fetch_instance,
    fetch_instance_children,
    fetch_parent_chain,
    model_instances,
    model_instance,
    model_instance_children,
    model_instance_parent_chain,
  };
});
