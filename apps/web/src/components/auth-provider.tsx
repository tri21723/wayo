"use client";

import { createContext, useContext, useEffect, useState } from "react";
import type { Session } from "@supabase/supabase-js";
import { getSupabase } from "@/lib/supabase";

const AuthContext = createContext<{
  session: Session | null;
  loading: boolean;
  configured: boolean;
}>({ session: null, loading: true, configured: false });

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState({
    session: null as Session | null,
    loading: true,
    configured: false,
  });
  useEffect(() => {
    const supabase = getSupabase();
    if (!supabase) {
      // Resolve initialization asynchronously to avoid updates during effect setup.
      queueMicrotask(() =>
        setState({ session: null, loading: false, configured: false }),
      );
      return;
    }
    let active = true;
    const { data } = supabase.auth.onAuthStateChange((_event, session) => {
      if (active) setState({ session, loading: false, configured: true });
    });
    return () => {
      active = false;
      data.subscription.unsubscribe();
    };
  }, []);
  return <AuthContext.Provider value={state}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
