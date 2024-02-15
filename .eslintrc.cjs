/* eslint-env node */
require("@rushstack/eslint-patch/modern-module-resolution");

module.exports = {
  root: true,
  extends: [
    "plugin:vue/vue3-recommended",
    "eslint:recommended",
    "@vue/eslint-config-typescript",
    "@vue/eslint-config-prettier",
    // "plugin:tailwindcss/recommended",
    "plugin:vitest-globals/recommended",
  ],
  parserOptions: {
    ecmaVersion: "latest",
  },
  env: {
    "vitest-globals/env": true,
  },
  rules: {
    "vue/v-bind-style": ["error", "longform"],
    "vue/v-on-style": ["error", "longform"],
    "vue/v-slot-style": [
      "error",
      {
        atComponent: "longform",
        default: "longform",
        named: "longform",
      },
    ],
  },
};
