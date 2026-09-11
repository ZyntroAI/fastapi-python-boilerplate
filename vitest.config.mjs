import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    // The root project has no JS test suite of its own — Python tests live under
    // pytest/ and each deliverable owns its own vitest config and dependencies.
    // Scoping this explicitly is what keeps `vitest run` from walking into
    // deliverables/ and tripping over files that use a different runner
    // (e.g. cwe1321's tests use node:test, not vitest).
    include: ["**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts}"],
    exclude: [
      "**/node_modules/**",
      "**/dist/**",
      "**/.git/**",
      // Each deliverable is its own package with its own test setup.
      "deliverables/**",
      // Separate packages with their own toolchains.
      "frontend/**",
      "Package/**",
      ".vscode/**",
    ],
    // There are currently no root-level JS tests, so a bare `vitest run` would
    // otherwise exit 1 with "No test files found" and fail CI.
    passWithNoTests: true,
  },
});
