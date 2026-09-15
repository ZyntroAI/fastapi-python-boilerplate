// ESLint flat config (ESLint v9+/v10). The repo pins `eslint ^10.10.0`, where
// the legacy `.eslintrc.*` format is no longer read at all — a flat config is
// the only thing `npm run lint` and `lint-staged` will load.
//
// Rules are scoped per file type so each plugin is registered in the same
// config object that uses it (a flat-config requirement).
import js from "@eslint/js";
import prettier from "eslint-config-prettier";
import tseslint from "typescript-eslint";
import globals from "globals";

// Files that are NOT source code despite their extension:
//  - scripts/pr-manager.js and middleware/errorHandler.ts hold pasted chat
//    prose / note text, not code, so parsing them is meaningless. They are
//    candidates for removal or relocation under FIG-TASK-008 (repo-root
//    cleanup); until then they are excluded here rather than silently.
//  - .vscode/** is editor workspace tooling whose disable directives reference
//    plugins (unicorn, n) that this repo does not depend on.
const NON_LINTED = [
  "scripts/pr-manager.js",
  "middleware/errorHandler.ts",
  ".vscode/**",
];

const baseGlobals = {
  ...globals.browser,
  ...globals.node,
  ...globals.es2025,
};

export default tseslint.config(
  {
    // Build output, dependencies, fixtures, generated bundles and Python.
    ignores: [
      "node_modules/",
      "**/node_modules/",
      "dist/",
      "build/",
      "coverage/",
      ".next/",
      ".cache/",
      "archive/**",
      "deliverables/**",
      "**/*.py",
      ...NON_LINTED,
    ],
  },

  // JavaScript / ESM / CommonJS / JSX.
  {
    files: ["**/*.{js,mjs,cjs,jsx}"],
    ...js.configs.recommended,
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: baseGlobals,
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    rules: {
      ...js.configs.recommended.rules,
      // Allow a leading underscore to mark intentionally unused bindings
      // (common in framework callbacks such as Express error handlers).
      "no-unused-vars": ["warn", { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }],
      // `console` is used deliberately for server-side logging.
      "no-console": "off",
    },
  },

  // TypeScript / TSX — recommended (non type-checked) rules, so linting does
  // not depend on a resolvable tsconfig for every file.
  ...tseslint.configs.recommended.map((config) => ({
    ...config,
    files: ["**/*.{ts,tsx}"],
  })),
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: baseGlobals,
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    rules: {
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      // CommonJS interop is legitimate in this repo's backend/middleware code.
      "@typescript-eslint/no-require-imports": "off",
      "no-console": "off",
    },
  },

  // Prettier must be last — it disables every rule that would fight `npm run format`.
  prettier,
);
