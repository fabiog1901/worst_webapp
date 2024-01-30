<template>
  <div class="flex">
            <div class="p-2 text-sm text-gray-700 dark:text-white">
              {{ x.name }} <i>[{{ x.type }}]</i>
            </div>
            <div class="flex-grow"></div>
            <div>
              <button
                v-if="edit_field !== x.name"
                class="m-2 rounded-xl bg-green-400 px-2 text-sm hover:cursor-pointer hover:bg-green-300"
                v-on:click="
                  new_value = modelStore.instance[x.name];
                  edit_field = x.name;
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
                    save_new_value(modelStore.instance[x.name as keyof Model])
                  "
                >
                  Save
                </div>
              </button>
            </div>
          </div>
          <div v-if="x.type === 'decimal'">
            <div
              v-if="edit_field !== x.name"
              class="m-1 flex h-8 items-center rounded border bg-slate-300 p-1 dark:bg-slate-500 dark:text-white"
            >
              <label>{{
                formatDecimal(modelStore.instance?.[x.name as keyof Model])
              }}</label>
            </div>
            <div
              v-else
              class="m-1 h-8 rounded border bg-slate-300 dark:bg-slate-500 dark:text-white"
            >
              <input
                v-bind:id="instance_id"
                v-model.number="new_value"
                class="h-full w-full p-2 text-black"
                type="number"
                autocomplete="off"
              />
            </div>
          </div>

          <div v-else-if="x.type === 'date'">
            <div
              v-if="edit_field !== x.name"
              class="m-1 flex h-8 items-center rounded border bg-slate-300 p-1 dark:bg-slate-500 dark:text-white"
            >
              <label>{{
                formatDate(modelStore.instance?.[x.name as keyof Model])
              }}</label>
            </div>

            <div
              v-else
              class="m-1 h-8 rounded border bg-slate-300 dark:bg-slate-500 dark:text-white"
            >
              <input
                v-bind:id="instance_id"
                v-model="new_value"
                class="h-full w-full p-2 text-black"
                type="date"
                autocomplete="off"
              />
            </div>
          </div>
          <div v-else-if="x.type === 'enum'">
            <div v-if="edit_field !== x.name" class="m-1 flex h-8 items-center">
              <div
                class="flex h-8 w-fit min-w-16 items-center justify-center rounded border p-2 text-sm font-semibold"
                v-bind:class="
                  getLabel(
                    modelStore.instance?.[x.name as keyof Model] as string,
                  )
                "
              >
                {{ modelStore.instance?.[x.name as keyof Model] }}
              </div>
            </div>
            <div
              v-else
              class="m-1 h-8 rounded border bg-slate-300 dark:bg-slate-500 dark:text-white"
            >
              <input
                v-bind:id="instance_id"
                v-model.lazy.trim="new_value"
                class="h-full w-full p-2 text-black"
                type="text"
                autocomplete="off"
              />
            </div>
          </div>
          <div v-else-if="x.type === 'markdown'">
            <div
              v-if="edit_field !== x.name"
              class="h-96 bg-slate-300 dark:bg-slate-500 dark:text-white"
            >
              <FabMark
                class="h-96 overflow-y-scroll dark:bg-slate-500 dark:text-white"
                v-bind:source="modelStore.instance?.[x.name] ?? ''"
                v-bind:theme="getTheme"
              />
            </div>

            <div
              v-else
              class="h-96 bg-slate-300 dark:bg-slate-500 dark:text-white"
            >
              <FabMarkEdit v-model="new_value" class="h-96" />
            </div>
          </div>

          <div v-else>
            <div
              v-if="edit_field !== x.name"
              class="m-1 flex h-8 items-center rounded border bg-slate-300 p-1 dark:bg-slate-500 dark:text-white"
            >
              <label>{{ modelStore.instance?.[x.name as keyof Model] }}</label>
            </div>
            <div
              v-else
              class="m-1 h-8 rounded border bg-slate-300 dark:bg-slate-500 dark:text-white"
            >
              <input
                v-bind:id="instance_id"
                v-model.lazy.trim="new_value"
                class="h-full w-full p-2 text-black"
                type="text"
                autocomplete="off"
              />
            </div>
          </div>
        </div>
</template>

<script setup lang="ts">


defineProps({
  source: {
    type: String,
    default: "",
  },
  theme: {
    type: String,
    default: "dark",
  },
});

defineEmits({

});
</script>
