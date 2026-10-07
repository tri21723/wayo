"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AccountNav } from "@/components/account-nav";
import { useAuth } from "@/components/auth-provider";
import { listTrips, type TripList } from "@/lib/api";

function TripCollection() {
  const [data, setData] = useState<TripList | null>(null);
  const [error, setError] = useState("");
  const [page, setPage] = useState(0);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    listTrips(page * 20)
      .then((value) => {
        if (active) setData(value);
      })
      .catch((caught) => {
        if (active)
          setError(
            caught instanceof Error
              ? caught.message
              : "Không tải được chuyến đi.",
          );
      });
    return () => {
      active = false;
    };
  }, [page, attempt]);
  function load(next: number) {
    setData(null);
    setError("");
    setPage(next);
    setAttempt((value) => value + 1);
  }
  if (error)
    return (
      <div className="message error" role="alert">
        <p>{error}</p>
        <button type="button" onClick={() => load(page)}>
          Thử lại
        </button>
      </div>
    );
  if (!data) return <p role="status">Đang tải chuyến đi…</p>;
  return (
    <>
      {data.total === 0 ? (
        <div className="form-card">
          <h2>Chuyến đi đầu tiên đang chờ bạn</h2>
          <p>
            Tạo bản nháp, lưu vào tài khoản và quay lại chỉnh sửa bất cứ lúc
            nào.
          </p>
          <Link href="/">Phác thảo chuyến đi →</Link>
        </div>
      ) : (
        <div className="trip-grid">
          {data.items.map((item) => (
            <article className="form-card" key={item.id}>
              <p className="eyebrow">ĐÀ LẠT · BẢN NHÁP</p>
              <h2>
                <Link href={`/trips/${item.id}`}>{item.title}</Link>
              </h2>
              <p>
                {new Date(item.trip.arrival_at).toLocaleDateString("vi-VN", {
                  timeZone: "Asia/Ho_Chi_Minh",
                })}{" "}
                –{" "}
                {new Date(item.trip.departure_at).toLocaleDateString("vi-VN", {
                  timeZone: "Asia/Ho_Chi_Minh",
                })}
              </p>
              <p>
                {item.trip.people_count} người ·{" "}
                {item.trip.budget.amount_vnd.toLocaleString("vi-VN")} đ{" "}
                {item.trip.budget.scope === "group" ? "/ cả nhóm" : "/ người"}
              </p>
              <Link href={`/trips/${item.id}`}>Xem và chỉnh sửa →</Link>
            </article>
          ))}
        </div>
      )}
      {data.total > 20 && (
        <div className="pagination">
          <button disabled={page === 0} onClick={() => load(page - 1)}>
            Trước
          </button>
          <span>Trang {page + 1}</span>
          <button
            disabled={(page + 1) * 20 >= data.total}
            onClick={() => load(page + 1)}
          >
            Tiếp
          </button>
        </div>
      )}
    </>
  );
}

export default function TripsPage() {
  const { session, loading, configured } = useAuth();
  return (
    <main>
      <header className="topbar">
        <Link href="/" className="wordmark">
          wayo↗
        </Link>
        <AccountNav />
      </header>
      <section className="intro">
        <p className="eyebrow">CHUYẾN ĐI CỦA BẠN</p>
        <h1>
          Lên kế hoạch,
          <br />
          <span>tiếp tục khi bạn muốn.</span>
        </h1>
        <Link href="/">+ Tạo chuyến đi mới</Link>
      </section>
      {loading ? (
        <p role="status">Đang kiểm tra phiên đăng nhập…</p>
      ) : !configured ? (
        <div className="form-card">
          <p>Tính năng tài khoản chưa được mở ở bản này.</p>
          <Link href="/">Tiếp tục kiểm tra chuyến đi →</Link>
        </div>
      ) : !session ? (
        <div className="form-card">
          <p>Đăng nhập để xem các chuyến đi đã lưu của bạn.</p>
          <Link href="/login">Đăng nhập →</Link>
        </div>
      ) : (
        <TripCollection key={session.user.id} />
      )}
    </main>
  );
}
