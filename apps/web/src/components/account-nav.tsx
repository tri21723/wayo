"use client";

import Link from "next/link";
import { useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { getSupabase } from "@/lib/supabase";

export function AccountNav() {
  const { session, loading, configured } = useAuth();
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);
  async function signOut() {
    setPending(true);
    setError("");
    try {
      const result = await getSupabase()?.auth.signOut({ scope: "local" });
      if (result?.error) setError("Chưa đăng xuất được. Vui lòng thử lại.");
    } catch {
      setError("Chưa đăng xuất được. Vui lòng thử lại.");
    } finally {
      setPending(false);
    }
  }
  return (
    <nav className="account-nav" aria-label="Tài khoản">
      <Link href="/profile">Sở thích của tôi</Link>
      <Link href="/trips">Chuyến đi của tôi</Link>
      {!loading &&
        configured &&
        (session ? (
          <button type="button" onClick={signOut} disabled={pending}>
            Đăng xuất
          </button>
        ) : (
          <Link href="/login">Đăng nhập</Link>
        ))}
      {error && <span role="alert">{error}</span>}
    </nav>
  );
}
