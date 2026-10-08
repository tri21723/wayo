import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import ts from "typescript";

// Replace only the SDK session source; exercise the real client request/mutation code.
const sessionModule = `data:text/javascript;base64,${Buffer.from(
  `
  export function getSupabase() {
    return { auth: { getSession: async () => ({ data: { session: {
      user: { id: "owner-b" }, access_token: "fixture-token"
    } }, error: null }) } };
  }
`,
).toString("base64")}`;
const source = await readFile(new URL("./api.ts", import.meta.url), "utf8");
const compiled = ts.transpileModule(
  source.replace('"./supabase"', JSON.stringify(sessionModule)),
  {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ES2022,
    },
  },
).outputText;
const { createTrip, updateTrip } = await import(
  `data:text/javascript;base64,${Buffer.from(compiled).toString("base64")}`
);

test("create/update do not send a payload under a different account returned by getSession", async (t) => {
  const fetch = t.mock.method(globalThis, "fetch", async () => {
    throw new Error("must not send");
  });
  await assert.rejects(createTrip({}, "owner-a"), {
    code: "SESSION_CHANGED",
    status: 401,
  });
  await assert.rejects(updateTrip("trip", {}, "owner-a"), {
    code: "SESSION_CHANGED",
    status: 401,
  });
  assert.equal(fetch.mock.callCount(), 0);
});

test("matching account can send a mutation using its session token", async (t) => {
  t.mock.method(globalThis, "fetch", async (_url, options) => {
    assert.equal(options.headers.get("Authorization"), "Bearer fixture-token");
    assert.equal(options.method, "POST");
    return Response.json({ id: "saved-trip" }, { status: 201 });
  });
  assert.deepEqual(await createTrip({}, "owner-b"), { id: "saved-trip" });
});
