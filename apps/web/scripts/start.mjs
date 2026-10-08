import { cp, mkdir } from "node:fs/promises";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const webRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
);
const dist = process.env.WAYO_E2E === "1" ? ".next-e2e" : ".next";
const packagedWeb = path.join(webRoot, dist, "standalone", "apps", "web");
const args = process.argv.slice(2);
let port = process.env.PORT ?? "3000";
let hostname = "127.0.0.1";
for (let index = 0; index < args.length; index += 2) {
  if (args[index] === "--port") port = args[index + 1];
  else if (args[index] === "--hostname") hostname = args[index + 1];
  else throw new Error("Supported options: --port, --hostname");
}
if (
  !/^\d+$/.test(port ?? "") ||
  Number(port) < 1 ||
  Number(port) > 65535 ||
  !hostname
)
  throw new Error("Invalid port or hostname.");
await mkdir(path.join(packagedWeb, dist), { recursive: true });
await cp(
  path.join(webRoot, dist, "static"),
  path.join(packagedWeb, dist, "static"),
  { recursive: true },
);
const child = spawn(process.execPath, [path.join(packagedWeb, "server.js")], {
  stdio: "inherit",
  env: { ...process.env, PORT: port, HOSTNAME: hostname },
});
process.on("SIGINT", () => child.kill("SIGINT"));
process.on("SIGTERM", () => child.kill("SIGTERM"));
child.on("error", () => process.exit(1));
child.on("exit", (code) => process.exit(code ?? 1));
