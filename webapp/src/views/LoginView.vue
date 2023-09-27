<template>
  <section class="align-center flex h-screen justify-center bg-slate-700">
    <Form
      v-slot:default="{ errors, isSubmitting }"
      class="h-96 w-96 p-2"
      v-bind:validation-schema="schema"
      v-on:submit="onSubmit"
    >
      <div class="mb-6 md:flex md:items-center">
        <div class="md:w-1/3">
          <label
            class="mb-1 block pr-4 font-bold text-gray-500 md:mb-0 md:text-right"
            for="inline-full-name"
          >
            Username
          </label>
        </div>
        <div class="form-group md:w-2/3">
          <Field
            name="username"
            type="text"
            class="form-control w-full appearance-none rounded border-2 border-gray-200 bg-gray-200 px-4 py-2 leading-tight text-gray-700 focus:border-purple-500 focus:bg-white focus:outline-none"
            v-bind:class="{ 'is-invalid': errors.username }"
          />
          <div class="invalid-feedback">{{ errors.username }}</div>
        </div>
      </div>
      <div class="mb-6 md:flex md:items-center">
        <div class="md:w-1/3">
          <label
            class="mb-1 block pr-4 font-bold text-gray-500 md:mb-0 md:text-right"
            for="inline-password"
          >
            Password
          </label>
        </div>
        <div class="form-group md:w-2/3">
          <Field
            name="password"
            type="password"
            class="form-control w-full appearance-none rounded border-2 border-gray-200 bg-gray-200 px-4 py-2 leading-tight text-gray-700 focus:border-purple-500 focus:bg-white focus:outline-none"
            v-bind:class="{ 'is-invalid': errors.password }"
          />
          <div class="invalid-feedback">{{ errors.password }}</div>
        </div>
      </div>
      <div class="mb-6 md:flex md:items-center">
        <div class="md:w-1/3"></div>
        <label class="block font-bold text-gray-500 md:w-2/3">
          <input class="mr-2 leading-tight" type="checkbox" />
          <span class="text-sm"> Remember me </span>
        </label>
      </div>
      <div class="md:flex md:items-center">
        <div class="md:w-1/3"></div>
        <div class="form-group md:w-2/3">
          <button
            v-bind:disabled="isSubmitting"
            class="focus:shadow-outline rounded bg-blue-500 px-4 py-2 font-bold text-white shadow hover:bg-purple-400 focus:outline-none w-full"
          >
            Login
          </button>
        </div>
      </div>
    </Form>
  </section>
</template>

<script setup lang="ts">
import { Form, Field } from "vee-validate";
import * as Yup from "yup";

import { useAuthStore } from "@/stores/authStore";

const schema = Yup.object().shape({
  username: Yup.string().required("Username is required"),
  password: Yup.string().required("Password is required"),
});

function onSubmit(values, { setErrors }) {
  const authStore = useAuthStore();
  const { username, password } = values;

  return authStore
    .login(username, password)
    .catch((error) => setErrors({ apiError: error }));
}
</script>
