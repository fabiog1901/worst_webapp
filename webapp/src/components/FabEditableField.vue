<template>
  <div class="flex">
    <div class="p-2 text-sm text-gray-700 dark:text-white">
      {{ item_name }}
    </div>
    <div class="flex-grow"></div>
    <div>
      <button
        v-if="edit_field !== item_name"
        class="m-2 rounded-xl bg-green-400 px-2 text-sm hover:cursor-pointer hover:bg-green-300"
        v-on:click="
          new_value = instance[item_name] ?? '';
          edit_field = item_name;
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
            $emit('save_new_value', [
              new_value,
              instance[item_name as keyof Model],
              edit_field,
            ]);
            edit_field = '';
          "
        >
          Save
        </div>
      </button>
    </div>
  </div>
  <div v-if="item_type === 'decimal'">
    <div
      v-if="edit_field !== item_name"
      class="m-1 flex h-8 items-center rounded border bg-slate-300 p-1 dark:bg-slate-500 dark:text-white"
    >
      <label>{{ formatDecimal(instance?.[item_name as keyof Model]) }}</label>
    </div>
    <div
      v-else
      class="m-1 h-8 rounded border bg-slate-300 dark:bg-slate-500 dark:text-white"
    >
      <input
        v-model.number="new_value"
        class="h-full w-full p-2 text-black"
        type="number"
        autocomplete="off"
      />
    </div>
  </div>

  <div v-else-if="item_type === 'date'">
    <div
      v-if="edit_field !== item_name"
      class="m-1 flex h-8 items-center rounded border bg-slate-300 p-1 dark:bg-slate-500 dark:text-white"
    >
      <label>{{ formatDate(instance?.[item_name as keyof Model]) }}</label>
    </div>

    <div
      v-else
      class="m-1 h-8 rounded border bg-slate-300 dark:bg-slate-500 dark:text-white"
    >
      <input
        v-model="new_value"
        class="h-full w-full p-2 text-black"
        type="date"
        autocomplete="off"
      />
    </div>
  </div>
  <div v-else-if="item_type === 'enum'">
    <div v-if="edit_field !== item_name" class="m-1 flex h-8 items-center">
      <div
        class="flex h-8 w-fit min-w-16 items-center justify-center rounded border p-2 text-sm font-semibold"
        v-bind:class="getLabel(instance?.[item_name as keyof Model] as string)"
      >
        {{ instance?.[item_name as keyof Model] }}
      </div>
    </div>
    <div
      v-else
      class="m-1 h-8 rounded border bg-slate-300 dark:bg-slate-500 dark:text-white"
    >
      <input
        v-model.lazy.trim="new_value"
        class="h-full w-full p-2 text-black"
        type="text"
        autocomplete="off"
      />
    </div>
  </div>
  <div v-else-if="item_type === 'markdown'">
    <div
      v-if="edit_field !== item_name"
      class="h-96 bg-slate-300 dark:bg-slate-500 dark:text-white"
    >
      <FabMark
        class="h-96 overflow-y-scroll dark:bg-slate-500 dark:text-white"
        v-bind:source="instance?.[item_name] ?? ''"
        v-bind:theme="getTheme"
      />
    </div>

    <div v-else class="h-96 bg-slate-300 dark:bg-slate-500 dark:text-white">
      <FabMarkEdit v-model="new_value" class="h-96" />
    </div>
  </div>

  <div v-else-if="item_type === 'header'">
    <div
      v-if="edit_field !== item_name"
      class="m-1 flex h-12 text-3xl items-center rounded border font-semibold bg-slate-300 p-1 dark:bg-slate-500 dark:text-white"
    >
      <label>{{ instance?.[item_name as keyof Model] }}</label>
    </div>
    <div
      v-else
      class="m-1 h-12 rounded border text-3xl font-semibold bg-slate-300 dark:bg-slate-500 dark:text-white"
    >
      <input
        v-model.lazy.trim="new_value"
        class="h-full w-full p-2 text-black"
        type="text"
        autocomplete="off"
      />
    </div>
  </div>

  <div v-else>
    <div
      v-if="edit_field !== item_name"
      class="m-1 flex h-8 items-center rounded border bg-slate-300 p-1 dark:bg-slate-500 dark:text-white"
    >
      <label>{{ instance?.[item_name as keyof Model] }}</label>
    </div>
    <div
      v-else
      class="m-1 h-8 rounded border bg-slate-300 dark:bg-slate-500 dark:text-white"
    >
      <input
        v-model.lazy.trim="new_value"
        class="h-full w-full p-2 text-black"
        type="text"
        autocomplete="off"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { formatDecimal, formatDate, getLabel } from "@/utils/utils";
import FabMark from "@/components/FabMark.vue";
import FabMarkEdit from "@/components/FabMarkEdit.vue";
import type { Model } from "@/types";

const edit_field = ref("");
const new_value = ref("");

defineProps({
  instance: {
    type: Object,
    default: {},
  },
  item_name: {
    type: String,
    default: "",
  },
  item_type: {
    type: String,
    default: "",
  },
});

defineEmits(["save_new_value"]);

const getTheme = computed(() => {
  const theme = localStorage.getItem("user-theme");
  if (!theme) {
    return "dark";
  }
  return theme;
});
</script>
