import js from "@eslint/js";
import globals from "globals";
import pluginVue from "eslint-plugin-vue";
import json from "@eslint/json";
import ts from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import { defineConfig } from "eslint/config";

export default defineConfig([
  js.configs.recommended,

  // Vue
  ...pluginVue.configs["flat/recommended"],

  // TypeScript
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        project: "./tsconfig.json",
        extraFileExtensions: [".vue"],
      },
      globals: { ...globals.browser, ...globals.node },
    },
    plugins: { "@typescript-eslint": ts },
    rules: {
      ...ts.configs.recommended.rules,
      // ...ts.configs["recommended-requiring-type-checking"].rules,
    },
  },

  // Vue + TS в <script>
  {
    files: ["**/*.vue"],
    languageOptions: {
      parserOptions: {
        parser: tsParser,
        project: "./tsconfig.json",
        extraFileExtensions: [".vue"],
      },
    },
    plugins: { "@typescript-eslint": ts },
    rules: {
      ...ts.configs.recommended.rules,
      "vue/no-undef-properties": "error",
    },
  },

  // JSON
  {
    files: ["**/*.json"],
    plugins: { json: json },
    rules: {
      ...json.configs.recommended.rules,
    },
  },

  { ignores: ["node_modules/**", "dist/**", ".vscode/**"] },
]);
