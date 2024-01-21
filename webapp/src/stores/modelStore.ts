import { ref, computed } from "vue";
import { defineStore } from "pinia";

import { axiosWrapper } from "@/utils/utils";

import type { Model } from "@/types";

export const useModelStore = defineStore("model", () => {
  // models
  const models: { [key: string]: any } = ref<{}>({});

  const get_all_models = async () => {
    models.value = await axiosWrapper.get(`/admin/models`);
    console.info("GET /admin/models");
  };

  const get_model = async (m: string) => {
    models.value = await axiosWrapper.get(`/admin/models/${m}`);
    console.info(`GET /admin/models/${m}`);
  };

  const create_model = async (m: string) => {
    await axiosWrapper.post(`/admin/models/`, m);
    console.info(`POST /admin/models/ (${m})`);
  };

  const update_model = async (m: string) => {
    await axiosWrapper.put(`/admin/models/`, m);
    console.info(`PUT /admin/models/`, m);
  };

  const delete_model = async (m: string) => {
    await axiosWrapper.delete(`/admin/models/${m}`);
    console.info(`DELETE /admin/models/${m}`);
  };

  // reports
  const reports: { [key: string]: any } = ref<{}>({});

  const get_all_reports = async () => {
    reports.value = await axiosWrapper.get(`/admin/reports`);
    console.info("GET /admin/reports");
  };

  const get_report = async (name: string) => {
    await axiosWrapper.get(`/admin/reports/${name}`);
    console.info(`GET /admin/reports/${name}`);
  };

  const create_report = async (name: string, sql_stmt: string) => {
    await axiosWrapper.post(`/admin/reports/`, {
      name: name,
      sql_stmt: sql_stmt,
    });
    console.info(`POST /admin/reports/ (${name}, ${sql_stmt})`);
  };

  const update_report = async (name: string, sql_stmt: string) => {
    await axiosWrapper.put(`/admin/reports/${name}`, { sql_stmt: sql_stmt });
    console.info(`PUT /admin/reports/${name}`, sql_stmt);
  };

  const delete_report = async (name: string) => {
    await axiosWrapper.delete(`/admin/reports/${name}`);
    console.info(`DELETE /admin/reports/${name}`);
  };

  // sql
  const result_set = ref<any>([]);

  const execute_sql_report = async (name: string) => {
    result_set.value = await axiosWrapper.post(`/sql/report/${name}`);
    console.info(`POST /sql/report/${name}`);
  };

  const execute_sql_select = async (select_stmt: string) => {
    result_set.value = await axiosWrapper.post(`/sql/select`, select_stmt);
    console.info("POST /sql/select", select_stmt);
  };

  const execute_sql_dml = async (sql_stmt: string) => {
    result_set.value = await axiosWrapper.post(`/sql/dml`, sql_stmt);
    console.info("POST /sql/dml", sql_stmt);
  };

  // instances
  const instances = ref<Model[]>([]);
  const instance: { [index: string]: any } = ref<Model>({} as Model);
  const instance_children = ref<any>();
  const instance_parent_chain = ref<any[]>([]);

  const get_all_instances = async (model_name: string) => {
    instances.value = await axiosWrapper.get(`/${model_name}`);
    console.info(`GET /${model_name}`);
  };

  const get_instance = async (model_name: string, id: string) => {
    instance.value = await axiosWrapper.get(`/${model_name}/${id}`);
    console.info(`GET /${model_name}/${id}`);
  };

  const get_instance_children = async (model_name: string, id: string) => {
    instance_children.value = await axiosWrapper.get(
      `/${model_name}/${id}/children`
    );
    console.info(`GET /${model_name}/${id}/children`);
  };

  const get_instance_children_for_model = async (
    model_name: string,
    id: string,
    child_model_name: string
  ) => {
    instances.value = await axiosWrapper.get(
      `/${model_name}/${id}/${child_model_name}`
    );
    console.info(`GET /${model_name}/${id}/${child_model_name}`);
  };

  const get_instance_parent_chain = async (model_name: string, id: string) => {
    instance_parent_chain.value = await axiosWrapper.get(
      `/${model_name}/${id}/parent_chain`
    );
    console.info(`GET /${model_name}/${id}/parent_chain`);
  };

  const get_presigned_get_url = async (
    model_name: string,
    id: string,
    filename: string
  ) => {
    console.info(`GET /${model_name}/${id}/presigned-get-url/${filename}`);
    return await axiosWrapper.get(
      `/${model_name}/${id}/presigned-get-url/${filename}`
    );
  };

  const get_presigned_put_url = async (
    model_name: string,
    id: string,
    filename: string
  ) => {
    console.info(`GET /${model_name}/${id}/presigned-put-url/${filename}`);
    return await axiosWrapper.get(
      `/${model_name}/${id}/presigned-put-url/${filename}`
    );
  };

  const delete_attachment = async (
    model_name: string,
    id: string,
    filename: string
  ) => {
    const i = await axiosWrapper.delete(
      `/${model_name}/${id}/attachments/${filename}`
    );
    console.info(`DELETE /${model_name}/${id}/attachments/${filename}`);
  };

  const create_instance = async (model_name: string, m: string) => {
    console.info(`POST /${model_name}`, m);
    return await axiosWrapper.post(`/${model_name}`, m);
  };

  const update_instance = async (model_name: string, m: string) => {
    console.info(`PUT /${model_name}`, m);
    return await axiosWrapper.put(`/${model_name}`, m);
  };

  const partial_update_instance = async (
    model_name: string,
    id: string,
    field: string,
    val: any
  ) => {
    instance.value = await axiosWrapper.patch(`/${model_name}/${id}`, {
      field: field,
      value: val,
    });
    console.info(`PATCH /${model_name}`, id, field, val);
  };

  const delete_instance = async (model_name: string, id: string) => {
    await axiosWrapper.delete(`/${model_name}/${id}`);
    console.info(`DELETE /${model_name}/${id}`);
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
    if (instances.value)
      return instances.value.filter((x) => include_models_by_owners(x));
    return [];
  };

  return {
    // models
    models,
    get_all_models,
    get_model,
    create_model,
    update_model,
    delete_model,

    // sql
    result_set,
    execute_sql_report,
    execute_sql_dml,
    execute_sql_select,

    // reports
    reports,
    get_all_reports,
    get_report,
    create_report,
    update_report,
    delete_report,

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
    get_presigned_get_url,
    get_presigned_put_url,
    delete_attachment,
    create_instance,
    update_instance,
    partial_update_instance,
    delete_instance,

    // misc
    get_unique_owners,
    get_filtered_models,
    clear_filters,
    add_selected_owners,
  };
});
