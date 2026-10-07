"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { useAuth } from "@/components/auth-provider";
import { getSupabase } from "@/lib/supabase";

export default function LoginPage() {
  const { configured, loading, session } = useAuth();
  const [signup, setSignup] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const router = useRouter();
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const supabase = getSupabase();
    if (!supabase || pending) return;
    const form = new FormData(event.currentTarget);
    const credentials = {
      email: String(form.get("email")).trim(),
      password: String(form.get("password")),
    };
    setPending(true);
    setError("");
    setMessage("");
    try {
      const { data, error: authError } = signup
        ? await supabase.auth.signUp(credentials)
        : await supabase.auth.signInWithPassword(credentials);
      if (authError) {
        setError(
          signup
            ? "Chưa tạo được tài khoản. Kiểm tra thông tin và thử lại sau."
            : "Đăng nhập chưa thành công. Kiểm tra email, mật khẩu và xác nhận email nếu cần.",
        );
      } else if (data.session) {
        router.replace("/trips");
      } else {
        setMessage(
          "Hãy kiểm tra email để xác nhận tài khoản, sau đó quay lại đăng nhập.",
        );
      }
    } catch {
      setError("Không kết nối được dịch vụ đăng nhập. Vui lòng thử lại.");
    } finally {
      setPending(false);
    }
  }
  return (
    <main className="narrow-page">
      <Link href="/" className="wordmark">
        wayo↗
      </Link>
      <section className="form-card">
        <h1 className="page-title">
          {signup ? "Tạo tài khoản" : "Chào bạn trở lại"}
        </h1>
        <p>Lưu chuyến đi và tiếp tục chỉnh sửa khi bạn sẵn sàng.</p>
        {loading ? (
          <p role="status">Đang kiểm tra phiên đăng nhập…</p>
        ) : !configured ? (
          <p role="status">
            Tính năng tài khoản chưa được mở ở bản này. Bạn vẫn có thể{" "}
            <Link href="/">kiểm tra thông tin chuyến đi</Link>.
          </p>
        ) : session ? (
          <Link href="/trips">Đến chuyến đi của tôi →</Link>
        ) : (
          <form onSubmit={submit}>
            <fieldset disabled={pending} className="auth-fields">
              <legend className="sr-only">Đăng nhập bằng email</legend>
              <label>
                Email
                <input
                  type="email"
                  name="email"
                  autoComplete="email"
                  required
                  maxLength={254}
                />
              </label>
              <label>
                Mật khẩu
                <input
                  type="password"
                  name="password"
                  autoComplete={signup ? "new-password" : "current-password"}
                  minLength={signup ? 8 : 1}
                  maxLength={128}
                  required
                />
              </label>
              <button className="primary" type="submit">
                {pending
                  ? "Đang xử lý…"
                  : signup
                    ? "Tạo tài khoản"
                    : "Đăng nhập"}
              </button>
              <button
                className="text-button"
                type="button"
                onClick={() => {
                  setSignup(!signup);
                  setError("");
                  setMessage("");
                }}
              >
                {signup
                  ? "Đã có tài khoản? Đăng nhập"
                  : "Chưa có tài khoản? Đăng ký"}
              </button>
            </fieldset>
          </form>
        )}
        {error && (
          <p className="message error" role="alert">
            {error}
          </p>
        )}
        {message && (
          <p className="message success" role="status">
            {message}
          </p>
        )}
      </section>
    </main>
  );
}
