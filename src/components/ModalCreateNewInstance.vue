<template>
  <div
    class="fixed left-0 top-0 z-10 flex h-full w-full items-center justify-center"
  >
    <div
      class="absolute h-full w-full bg-gray-900 opacity-50"
      v-on:click="$emit('cancel-clicked')"
    ></div>

    <div id="create_new_modal" class="absolute h-4/5 w-2/3">
      <div
        class="container h-full w-full overflow-y-scroll bg-white md:rounded dark:bg-slate-600"
      >
        <div
          class="flex select-none items-center justify-between border-b bg-gray-100 px-4 py-4 text-sm font-medium leading-none dark:bg-gray-700 dark:text-white"
        >
          <h3>New {{ props.modelName }}</h3>
          <div
            class="cursor-pointer text-2xl hover:text-gray-600"
            v-on:click="$emit('cancel-clicked')"
          >
            &#215;
          </div>
        </div>

        <div class="max-h-full px-4 py-4">
          <div class="w-96 flex-1 bg-gray-300 dark:bg-gray-700">
            <div v-for="x in props.modelBaseFields" v-bind:key="x">
              <div class="p-2 text-sm text-gray-700 dark:text-white">
                {{ x.name }} <i>[{{ x.type }}]</i>
              </div>
              <div
                v-if="x.type === 'decimal'"
                class="h-12 bg-slate-300 p-2 text-black dark:bg-slate-500"
              >
                <input v-model="m_json[x.name]" type="text" />
              </div>
              <div
                v-else-if="x.type === 'date'"
                class="h-12 bg-slate-300 p-2 dark:bg-slate-500"
              >
                <input v-model="m_json[x.name]" type="text" />
              </div>
              <div
                v-else-if="x.type === 'enum'"
                class="h-12 bg-slate-300 p-2 dark:bg-slate-500"
              >
                <input v-model="m_json[x.name]" type="text" />
              </div>
              <div
                v-else-if="x.type === 'markdown'"
                class="max-h-80 w-full overflow-y-scroll p-2 dark:bg-slate-500"
              >
                <input v-model="m_json[x.name]" type="text" />
              </div>

              <div v-else class="h-12 bg-slate-300 p-2 dark:bg-slate-500">
                <input v-model="m_json[x.name]" type="text" />
              </div>
            </div>
          </div>

          <div class="mt-4 p-2 text-right">
            <button
              class="px-4 py-2 text-sm text-gray-600 hover:underline focus:outline-none dark:text-white"
              v-on:click="$emit('cancel-clicked')"
            >
              Cancel
            </button>
            <button
              class="mr-2 rounded bg-green-500 px-4 py-2 text-sm text-white hover:bg-green-400 focus:outline-none"
              v-on:click="$emit('create-clicked', m_json)"
            >
              Create
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

defineEmits(["create-clicked", "cancel-clicked"]);

const props = defineProps({
  modelName: {
    type: String,
    required: true,
  },
  modelBaseFields: {
    type: Array<any>,
    required: true,
  },
});

const m_json = ref<{ [key: string]: any }>({});

m_json.value["name"] = ref();
for (const x of props.modelBaseFields) {
  m_json.value[x.name] = ref(null);
}
</script>

<style scoped>
/* .my-tag {
  @apply m-2 w-auto min-w-max origin-left scale-0 rounded-md
    bg-gray-900 p-2 
    text-xs font-bold 
    text-white shadow-md transition-all duration-100;
} */
</style>
