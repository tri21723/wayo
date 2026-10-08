import path from "node:path";
import type { NextConfig } from "next";

const config: NextConfig = {
  output: "standalone",
  outputFileTracingRoot: path.join(import.meta.dirname, "../.."),
  poweredByHeader: false,
  // Let browser tests run without stopping a developer's server on port 3000.
  distDir: process.env.WAYO_E2E === "1" ? ".next-e2e" : ".next",
};

export default config;
