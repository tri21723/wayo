import assert from "node:assert/strict";
import test from "node:test";
import { assertPublicSupabaseKey, isPublicSupabaseKey } from "./public-key.mjs";

const jwt = (role) =>
  `eyJhbGciOiJIUzI1NiJ9.${Buffer.from(JSON.stringify({ role })).toString("base64url")}.test`;

test("public configuration accepts publishable and legacy anon keys", () => {
  for (const key of ["sb_publishable_fixture", jwt("anon")]) {
    assert.equal(isPublicSupabaseKey(key), true);
    assert.doesNotThrow(() => assertPublicSupabaseKey(key));
  }
});

test("private and malformed keys fail without exposing their value", () => {
  for (const key of [
    "sb_secret_fixture",
    jwt("service_role"),
    jwt("authenticated"),
    "invalid.key.fixture",
  ]) {
    assert.equal(isPublicSupabaseKey(key), false);
    assert.throws(
      () => assertPublicSupabaseKey(key),
      (error) => {
        assert.match(error.message, /Never use a secret\/service_role key/);
        assert.equal(error.message.includes(key), false);
        return true;
      },
    );
  }
});

test("missing or example configuration still permits guest builds", () => {
  for (const key of [undefined, "", "sb_publishable_YOUR_KEY"])
    assert.doesNotThrow(() => assertPublicSupabaseKey(key));
});
