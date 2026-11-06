import { defineConfig } from "vitest/config";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

export default defineConfig({
  test: {
    include: ["test/**/*.test.ts"],
    env: { DATA_DIR: mkdtempSync(join(tmpdir(), "pitch-in-test-")), DB_PATH: ":memory:", PAYPAL_SANDBOX_CLIENT_ID: "", PAYPAL_SANDBOX_CLIENT_SECRET: "", PAYPAL_HACK_GEMINI_API_KEY: "", DEMO_MODE: "1" },
    fileParallelism: false,
  },
});
