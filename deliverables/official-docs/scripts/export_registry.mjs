/**
 * Write src/official-docs.json from the JS registry.
 * Run: node scripts/export_registry.mjs
 *
 * The JSON is the contract the Python twin and CI read. Keeping JS as the
 * source of truth and generating the mirror means the two languages can never
 * drift silently — tests/test_official_docs.py asserts parity.
 */
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { toRegistry } from "../src/official-docs.js";

const here = dirname(fileURLToPath(import.meta.url));
const target = join(here, "..", "src", "official-docs.json");

const payload = JSON.stringify(toRegistry(), null, 2) + "\n";
writeFileSync(target, payload, "utf8");

const docCount = Object.keys(toRegistry().docs).length;
console.log(`wrote ${target} (${docCount} doc groups, ${payload.length} bytes)`);
