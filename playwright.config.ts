import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  workers: 1,
  timeout: 90_000,
  // Cold route compilation on WSL/OneDrive can exceed Playwright's 5s default.
  expect: { timeout: 30_000 },
  use: { baseURL: "http://127.0.0.1:3100", trace: "retain-on-failure" },
  webServer: {
    command:
      process.env.WAYO_E2E_PRODUCTION === "1"
        ? "npm run start --workspace @wayo/web -- --hostname 127.0.0.1 --port 3100"
        : "npm run dev --workspace @wayo/web -- --webpack --hostname 127.0.0.1 --port 3100",
    url: "http://127.0.0.1:3100",
    timeout: 180_000,
    reuseExistingServer: false,
    env: {
      WAYO_E2E: "1",
      WAYO_API_URL: "http://127.0.0.1:9",
      NEXT_PUBLIC_SUPABASE_URL: "http://127.0.0.1:54321",
      NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: "e2e-public-test-key",
    },
  },
});
