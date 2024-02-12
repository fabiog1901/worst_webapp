<template>
  <div class="flex w-full">
    <section
      id="context-bar"
      class="flex w-96 flex-col bg-gray-50 dark:bg-gray-600"
    >
      <div v-for="(v, k) in modelStore.instance_children" v-bind:key="k">
        <router-link v-bind:to="route.path + '/' + k"
          ><span
            class="m-1 flex w-32 cursor-pointer justify-center rounded-xl border bg-gray-400 p-2 align-middle hover:font-bold dark:bg-slate-700 dark:text-white"
            >{{ k }}</span
          >
        </router-link>
        <div
          v-for="n in v"
          v-bind:key="n"
          class="mx-12 my-1 flex cursor-pointer justify-center rounded-full border bg-green-400 p-2 align-middle hover:font-bold dark:bg-green-700 dark:text-white"
        >
          <router-link v-bind:to="'/' + k + '/' + n.id">
            <span class="">{{ n.name }}</span>
          </router-link>
        </div>
      </div>
    </section>

    <section
      id="content-container"
      class="flex w-full bg-gray-300 dark:bg-gray-700"
    >
      <main class="w-96 flex-1 bg-gray-300 dark:bg-gray-700">
        <FabEditableField
          v-bind:instance="modelStore.instance"
          item_name="name"
          item_type="header"
          v-on:save_new_value="save_new_value($event[0], $event[1], $event[2])"
        ></FabEditableField>

        <div v-for="x in getSkemaFields" v-bind:key="x" class="">
          <FabEditableField
            v-bind:instance="modelStore.instance"
            v-bind:item_name="x.name"
            v-bind:item_type="x.type"
            v-on:save_new_value="
              save_new_value($event[0], $event[1], $event[2])
            "
          ></FabEditableField>
        </div>
      </main>

      <main
        class="flex flex-col w-96 bg-gray-300 dark:bg-gray-900 dark:text-white"
      >
        <div class="m-1 text-sm dark:text-white">
          id: {{ modelStore.instance?.id }}
        </div>
        <div class="mb-1 mx-1 text-sm">
          created_by: {{ modelStore.instance?.created_by }}
        </div>
        <div class="mb-1 mx-1 text-sm">
          created_at: {{ modelStore.instance?.created_at }}
        </div>
        <div class="mb-1 mx-1 text-sm">
          updated_by: {{ modelStore.instance?.updated_by }}
        </div>
        <div class="mb-1 mx-1 text-sm">
          updated_at: {{ modelStore.instance?.updated_at }}
        </div>

        <hr
          id="linebreaker"
          class="m-1 rounded-full border border-gray-200 bg-gray-200 dark:border-gray-800 dark:bg-gray-800"
        />

        <div class="flex">
          <div class="p-2 text-sm text-gray-700 dark:text-white">parent</div>
          <div class="flex-grow"></div>
          <button
            v-if="edit_field !== 'parent'"
            class="m-2 rounded-xl bg-green-400 px-2 text-sm hover:cursor-pointer hover:bg-green-300"
            v-on:click="
              new_value =
                modelStore.instance.parent_type +
                '/' +
                modelStore.instance.parent_id;
              edit_field = 'parent';
            "
          >
            Edit
          </button>
          <button v-else class="flex">
            <div
              class="m-2 px-2 text-sm underline hover:cursor-pointer dark:text-white"
              v-on:click="edit_field = ''"
            >
              Cancel
            </div>

            <div
              class="m-2 rounded-xl bg-orange-400 px-2 text-sm hover:cursor-pointer hover:bg-orange-300"
              v-on:click="
                save_new_parent(
                  modelStore.instance?.parent_type,
                  modelStore.instance?.parent_id,
                )
              "
            >
              Save
            </div>
          </button>
        </div>
        <div>
          <div
            v-if="edit_field !== 'parent'"
            class="m-1 flex h-8 items-center rounded border bg-slate-300 p-1 text-sm font-semibold dark:bg-slate-500 dark:text-white"
          >
            <label v-if="modelStore.instance?.parent_type"
              >{{ modelStore.instance?.parent_type }}/{{
                modelStore.instance?.parent_id
              }}</label
            >
          </div>
          <div
            v-else
            class="m-1 h-8 rounded border bg-slate-300 text-sm dark:bg-slate-500 dark:text-white"
          >
            <input
              v-bind:id="instance_id"
              v-model="new_value"
              class="h-full w-full p-2 text-black"
              type="text"
              autocomplete="off"
            />
          </div>
        </div>

        <FabEditableField
          v-bind:instance="modelStore.instance"
          item_name="owned_by"
          item_type="string"
          v-on:save_new_value="save_new_value($event[0], $event[1], $event[2])"
        ></FabEditableField>

        <FabEditableField
          v-bind:instance="modelStore.instance"
          item_name="permissions"
          item_type="string"
          v-on:save_new_value="save_new_value($event[0], $event[1], $event[2])"
        ></FabEditableField>

        <hr
          id="linebreaker"
          class="m-1 rounded-full border border-gray-200 bg-gray-200 dark:border-gray-800 dark:bg-gray-800"
        />

        <div class="mb-1 mx-1 text-sm">
          tags
          <div class="flex flex-wrap mt-2">
            <div
              v-for="tag in modelStore.instance?.tags"
              v-bind:key="tag"
              class="flex p-1"
            >
              <div class="flex h-8 w-fit items-center justify-start rounded-md">
                <div
                  class="flex h-8 min-w-10 w-fit items-center justify-center font-semibold pl-2 rounded-l-2xl"
                  v-bind:class="getLabel(tag)"
                >
                  {{ tag }}
                </div>
                <div
                  class="flex h-8 items-center text-2xl justify-center rounded-r-2xl pl-1 pr-2 hover:cursor-pointer hover:bg-red-500 hover:dark:bg-red-500"
                  v-bind:class="getLabel(tag)"
                  v-on:click="confirm_delete_item(tag, 'tag')"
                >
                  &#215;
                </div>
              </div>
            </div>
            <div class="flex-grow"></div>
            <div
              class="bg-green-500 hover:cursor-pointer hover:bg-green-300 text-white rounded-3xl h-8 w-8 m-1 text-center text-2xl font-semibold"
              v-on:click="showModalNewInput = true"
            >
              +
            </div>
          </div>
        </div>

        <hr
          id="linebreaker"
          class="m-1 rounded-full border border-gray-200 bg-gray-200 dark:border-gray-800 dark:bg-gray-800"
        />

        <div class="mb-1 mx-1 text-sm">
          attachments
          <div
            v-for="att in modelStore.instance?.attachments"
            v-bind:key="att"
            class="flex p-1"
          >
            <div
              class="flex h-8 w-fit items-center justify-start rounded-md bg-gray-300 shadow-md transition duration-300 ease-in-out dark:bg-gray-500 dark:text-gray-400"
            >
              <div
                class="flex h-8 w-full items-center rounded bg-transparent pl-2 pr-4 font-sans font-semibold outline-none hover:cursor-pointer hover:bg-gray-400 hover:underline hover:dark:bg-gray-600"
                v-on:click="download_file(att)"
              >
                {{ att }}
              </div>
              <div
                class="flex h-8 items-center justify-center rounded-r bg-gray-400 px-2 hover:cursor-pointer hover:bg-red-500 hover:dark:bg-red-500 dark:bg-gray-700"
                v-on:click="confirm_delete_item(att, 'attachment')"
              >
                <svg
                  id="garbage-bin-icon"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke="currentColor"
                  class="top-navigation-icon h-5 w-5"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <button
          id="upload-file"
          class="m-2 flex h-8 w-fit items-center justify-start"
        >
          <label
            class="flex h-8 w-full items-center rounded bg-green-700 p-2 font-sans font-semibold text-white outline-none hover:cursor-pointer hover:bg-green-400"
            for="upload_file"
            >Upload New File
            <input
              id="upload_file"
              hidden
              type="file"
              v-on:change="upload_file"
            />
            <svg
              id="magnifying-glass-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="top-navigation-icon ml-2 h-5 w-5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"
              />
            </svg>
          </label>
        </button>

        <div id="spacer" class="flex-grow"></div>

        <hr
          id="linebreaker"
          class="m-1 rounded-full border border-gray-200 bg-gray-200 dark:border-gray-800 dark:bg-gray-800"
        />

        <button id="delete-instance" class="m-2 flex justify-center">
          <label
            class="flex h-8 w-fit items-center justify-center rounded bg-red-500 p-2 font-sans font-semibold text-white outline-none hover:cursor-pointer hover:bg-red-400"
            v-on:click="
              confirm_delete_item(modelStore.instance?.name, 'instance')
            "
            >Delete instance

            <svg
              id="magnifying-glass-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="top-navigation-icon ml-2 h-5 w-5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
              />
            </svg>
          </label>
        </button>
      </main>

      <ModalDelete
        v-if="showModalDelete"
        v-bind:model-name="item_type_to_delete"
        v-bind:instance-name="item_to_delete"
        v-on:cancel-clicked="showModalDelete = false"
        v-on:delete-clicked="delete_item"
      ></ModalDelete>

      <ModalNewInput
        v-if="showModalNewInput"
        title="New Tag"
        field_name="Tag"
        v-on:cancel-clicked="showModalNewInput = false"
        v-on:create-clicked="create_new_tag($event)"
      >
      </ModalNewInput>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch, ref } from "vue";

import { useRoute, useRouter } from "vue-router";
import { useModelStore } from "@/stores/modelStore";

import ModalDelete from "@/components/ModalDelete.vue";
import ModalNewInput from "@/components/ModalNewInput.vue";

import { saveAs } from "file-saver";

import FabEditableField from "@/components/FabEditableField.vue";

const modelStore = useModelStore();
const route = useRoute();
const router = useRouter();

const showModalDelete = ref(false);
const showModalNewInput = ref(false);

const item_to_delete = ref("");
const item_type_to_delete = ref("");

const edit_field = ref("");
const new_value = ref("");

import { getLabel } from "@/utils/utils";

const instance_id = computed(() => {
  return route.params.id as string;
});

const create_new_tag = async (new_tag: string) => {

  const tags = modelStore.instance?.tags ?? [];

  if (!tags.includes(new_tag)) {
    tags.push(new_tag);

    modelStore.instance = await modelStore.partial_update_instance(
      instance_type.value,
      instance_id.value,
      "tags",
      tags,
    );
  }
  showModalNewInput.value = false
};

const save_new_value = async (new_v: string, old_v: string, field: string) => {
  if (old_v !== new_v) {
    modelStore.instance = await modelStore.partial_update_instance(
      instance_type.value,
      instance_id.value,
      field,
      new_v,
    );
  }

  edit_field.value = "";
};

const save_new_parent = async (parent_type: string, parent_id: string) => {
  const [new_parent_type, new_parent_id] = new_value.value.split("/");

  // check a new parent was added and not the same one
  if (parent_type !== new_parent_type || parent_id !== new_parent_id) {
    // check new parent is not itself
    if (
      new_parent_type === instance_type.value &&
      new_parent_id === modelStore.instance.id
    ) {
      console.warn("Parent cannot be the instance itself!");
      alert("The instance parent cannot be the instance itself!");
      return;
    }

    // check new parent exists:
    const parent = await modelStore.get_instance(
      new_parent_type,
      new_parent_id,
    );

    // if exists, update to new parent
    if (!parent) {
      console.warn("Parent does not exist!");
      alert("The requested parent does not exist!");
      return;
    }

    // check that parent is not one of its children
    // TODO

    await modelStore.partial_update_instance(
      instance_type.value,
      instance_id.value,
      "parent_type",
      new_parent_type,
    );

    modelStore.instance = await modelStore.partial_update_instance(
      instance_type.value,
      instance_id.value,
      "parent_id",
      new_parent_id,
    );
  }
  edit_field.value = "";
};

const instance_type = computed(() => {
  return route.params.instance_type as string;
});

const getSkemaFields = computed(() => {
  if (modelStore.models[instance_type.value])
    return modelStore.models[instance_type.value]["skema"]["fields"];
  return [];
});

const upload_file = async (e: any) => {
  const presigned_url = await modelStore.get_presigned_put_url(
    instance_type.value,
    instance_id.value,
    e.target.files[0].name,
  );

  await fetch(presigned_url, {
    method: "PUT",
    body: e.target.files[0],
  });

  modelStore.instance = await modelStore.get_instance(
    instance_type.value,
    instance_id.value,
  );
};

const download_file = async (filename: string) => {
  const presigned_url = await modelStore.get_presigned_get_url(
    instance_type.value,
    instance_id.value,
    filename,
  );

  saveAs(presigned_url, filename);
};

const confirm_delete_item = async (s: any, t: string) => {
  item_type_to_delete.value = t;
  showModalDelete.value = true;
  item_to_delete.value = s;
};

const delete_item = async () => {
  showModalDelete.value = false;

  switch (item_type_to_delete.value) {
    case "attachment":
      await modelStore.delete_attachment(
        instance_type.value,
        instance_id.value,
        item_to_delete.value,
      );

      // refresh to get updated list of attachments
      modelStore.instance = await modelStore.get_instance(
        instance_type.value,
        instance_id.value,
      );
      break;
    case "tag":
      const new_tags = (modelStore.instance.tags as Array<string>).filter(
        (x) => x !== item_to_delete.value,
      );

      modelStore.instance = await modelStore.partial_update_instance(
        instance_type.value,
        instance_id.value,
        "tags",
        new_tags,
      );
      break;
    case "instance":
      await modelStore.delete_instance(instance_type.value, instance_id.value);

      // go back to TableView for the same model name
      router.push(`/${instance_type.value}`);
      break;
  }
};

// const ff = computed(() => {
//   if (modelStore.instance !== undefined) {
//     return Object.keys(modelStore.instance)
//       .filter(
//         (key) =>
//           [
//             "id",
//             "name",
//             "owned_by",
//             "permissions",
//             "parent_type",
//             "parent_id",
//             "created_by",
//             "created_at",
//             "updated_at",
//             "updated_by",
//             "attachments",
//             "tags",
//           ].indexOf(key) === -1
//       )
//       .reduce((cur, key) => {
//         return Object.assign(cur, {
//           [key]: modelStore.instance?.[key as keyof Model],
//         });
//       }, {});
//   } else {
//     return {};
//   }
// });

onMounted(async () => {
  modelStore.instance = await modelStore.get_instance(
    instance_type.value,
    instance_id.value,
  );
  modelStore.instance_children = await modelStore.get_instance_children(
    instance_type.value,
    instance_id.value,
  );
  modelStore.instance_parent_chain = await modelStore.get_instance_parent_chain(
    instance_type.value,
    instance_id.value,
  );
});

watch(
  () => route.fullPath,
  async () => {
    if (instance_id.value && !route.params.child_model_name) {
      modelStore.instance = await modelStore.get_instance(
        instance_type.value,
        instance_id.value,
      );
      modelStore.instance_children = await modelStore.get_instance_children(
        instance_type.value,
        instance_id.value,
      );
      modelStore.instance_parent_chain =
        await modelStore.get_instance_parent_chain(
          instance_type.value,
          instance_id.value,
        );
    }
  },
);
</script>
