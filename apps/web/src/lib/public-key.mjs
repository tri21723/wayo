/** Classify configuration only; JWT signatures are verified by the API, not here.
 * @param {string | undefined} key
 */
export function isPublicSupabaseKey(key) {
  if (!key) return false;
  if (/^sb_publishable_[A-Za-z0-9_-]+$/.test(key)) return true;
  try {
    const parts = key.split(".");
    if (parts.length !== 3) return false;
    const payload = JSON.parse(
      atob(parts[1].replace(/-/g, "+").replace(/_/g, "/")),
    );
    return payload.role === "anon";
  } catch {
    return false;
  }
}

/** Fail before Next.js can inline a private key into browser assets.
 * @param {string | undefined} key
 */
export function assertPublicSupabaseKey(key) {
  if (!key || key === "sb_publishable_YOUR_KEY") return;
  if (!isPublicSupabaseKey(key))
    throw new Error(
      "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY must be a publishable key or legacy anon key. Never use a secret/service_role key.",
    );
}
