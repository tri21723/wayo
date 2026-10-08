import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import ts from "typescript";

// Compile the actual BFF module without adding a second test framework.
const source = await readFile(
  new URL("./api-proxy.ts", import.meta.url),
  "utf8",
);
const compiled = ts.transpileModule(
  source.replace(
    '"next/server"',
    JSON.stringify(import.meta.resolve("next/server.js")),
  ),
  {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ES2022,
    },
  },
).outputText;
const { proxyApi } = await import(
  `data:text/javascript;base64,${Buffer.from(compiled).toString("base64")}`
);

test("DELETE preserves upstream request ID and no-store on an empty 204 response", async (t) => {
  const requestId = "11111111-1111-4111-8111-111111111111";
  t.mock.method(globalThis, "fetch", async (_url, options) => {
    assert.equal(options.method, "DELETE");
    assert.equal(options.headers.get("Authorization"), "Bearer fixture");
    return new Response(null, {
      status: 204,
      headers: { "X-Request-ID": requestId },
    });
  });
  const result = await proxyApi(
    new Request("http://localhost/api/trips/fixture", {
      method: "DELETE",
      headers: { Authorization: "Bearer fixture" },
    }),
    "/v1/trips/fixture",
  );
  assert.equal(result.status, 204);
  assert.equal(result.headers.get("X-Request-ID"), requestId);
  assert.equal(result.headers.get("Cache-Control"), "no-store");
  assert.equal(await result.text(), "");
});
