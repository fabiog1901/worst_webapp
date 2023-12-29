import { ref, computed } from "vue";
import { defineStore } from "pinia";

import { axiosWrapper } from "@/utils/utils";

import type { Model } from "@/types";

export const useModelStore = defineStore("model", () => {
  // models
  const models: { [key: string]: any } = ref<{}>({});

  const get_all_models = async () => {
    models.value = await axiosWrapper.get(`/admin/models`);
    console.info("modelStore::get_all_models");
  };

  const get_model = async (m: string) => {
    models.value = await axiosWrapper.get(`/admin/models/${m}`);
    console.info(`modelStore::get_model(${m}`);
  };

  const create_model = async (m: string) => {
    await axiosWrapper.post(`/admin/models/`, m);
    console.info(`modelStore::create_model(${m})`);
  };

  const update_model = async (m: string) => {
    await axiosWrapper.put(`/admin/models/`, m);
    console.info(`modelStore::update_model`, m);
  };

  const delete_model = async (m: string) => {
    await axiosWrapper.delete(`/admin/models/${m}`);
    console.info(`modelStore::delete_model(${m})`);
  };

  // instances
  const instances = ref<Model[]>([]);
  const instance: { [index: string]: any } = ref<Model>({} as Model);
  const instance_children = ref<any>();
  const instance_parent_chain = ref<any[]>([]);

  const get_all_instances = async (model_name: string) => {
    instances.value = await axiosWrapper.get(`/${model_name}`);
    console.info(`modelStore::get_all_instances(${model_name})`);
  };

  const get_instance = async (model_name: string, id: string) => {
    instance.value = await axiosWrapper.get(`/${model_name}/${id}`);
    console.info(`modelStore::get_instance(${model_name}, ${id})`);
  };

  const get_instance_children = async (model_name: string, id: string) => {
    instance_children.value = await axiosWrapper.get(
      `/${model_name}/${id}/children`
    );
    console.info(`modelStore::get_instance_children(${model_name}, ${id})`);
  };

  const get_instance_children_for_model = async (
    model_name: string,
    id: string,
    child_model_name: string
  ) => {
    instances.value = await axiosWrapper.get(
      `/${model_name}/${id}/${child_model_name}`
    );
    console.info(
      `modelStore::get_instance_children_for_model(${model_name}, ${id}, ${child_model_name})`
    );
  };

  const get_instance_parent_chain = async (model_name: string, id: string) => {
    instance_parent_chain.value = await axiosWrapper.get(
      `/${model_name}/${id}/parent_chain`
    );
    console.info(`modelStore::get_instance_parent_chain(${model_name}, ${id})`);
  };

  const create_instance = async (model_name: string, m: string) => {
    const i = await axiosWrapper.post(`/${model_name}`, m);
    console.info(`modelStore::create_instance(${model_name}): ${m}`);
  };

  const update_instance = async (model_name: string, m: string) => {
    const i = await axiosWrapper.put(`/${model_name}`, m);
    console.info(`modelStore::update_instance(${model_name}): ${m}`);
  };

  const delete_instance = async (model_name: string, id: string) => {
    const i = await axiosWrapper.delete(`/${model_name}/${id}`);
    console.info(`modelStore::delete_instance(${model_name}): ${id}`);
  };

  // misc
  const selectedOwners = ref<string[]>([]);

  const add_selected_owners = (owners: string[]) => {
    selectedOwners.value = owners;
  };

  const get_unique_owners = computed(() => {
    const s = new Set<string>();
    instances.value.forEach((instance) => s.add(instance.owned_by));
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
    // console.log(instances.value.filter((x) => include_models_by_owners(x)));
    return instances.value.filter((x) => include_models_by_owners(x));
  };

  return {
    // models
    models,
    get_all_models,
    get_model,
    create_model,
    update_model,
    delete_model,

    // instances
    instances,
    instance,
    instance_children,
    instance_parent_chain,
    get_all_instances,
    get_instance,
    get_instance_parent_chain,
    get_instance_children,
    get_instance_children_for_model,
    create_instance,
    update_instance,
    delete_instance,

    // misc
    get_unique_owners,
    get_filtered_models,
    clear_filters,
    add_selected_owners,
  };
});
