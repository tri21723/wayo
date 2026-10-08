import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { isPublicSupabaseKey } from "./public-key.mjs";

let client: SupabaseClient | null = null;

export function getSupabase(): SupabaseClient | null {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  if (
    !url ||
    !key ||
    url.includes("YOUR_PROJECT") ||
    key.includes("YOUR_") ||
    !isPublicSupabaseKey(key)
  )
    return null;
  client ??= createClient(url, key);
  return client;
}
