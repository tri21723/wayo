"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AccountNav } from "@/components/account-nav";
import { useAuth } from "@/components/auth-provider";
import { TripRecommendations } from "@/components/trip-recommendations";
import { TripForm } from "@/components/trip-form";
import { deleteTrip, getTrip, type SavedTrip } from "@/lib/api";

function Editor({ id }: { id: string }) {
  const [trip, setTrip] = useState<SavedTrip | null>(null);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [pending, setPending] = useState(false);
  const [savedNotice, setSavedNotice] = useState(false);
  const router = useRouter();
  useEffect(() => {
    let active = true;
    getTrip(id)
      .then((value) => {
        if (active) setTrip(value);
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
  }, [id, attempt]);
  function reload() {
    setSavedNotice(false);
    setTrip(null);
    setError("");
    setConfirmDelete(false);
    setAttempt((value) => value + 1);
  }
  async function remove() {
    if (!trip || pending) return;
    setPending(true);
    setError("");
    try {
      await deleteTrip(trip.id, trip.revision);
      router.replace("/trips");
    } catch (caught) {
      setError(
        caught instanceof Error ? caught.message : "Chưa xóa được chuyến đi.",
      );
      setPending(false);
    }
  }
  return (
    <>
      {savedNotice && (
        <p className="message success" role="status">
          Đã lưu thay đổi chuyến đi.
        </p>
      )}
      {error && (
        <div className="message error" role="alert">
          <p>{error}</p>
        </div>
      )}
      <button
        type="button"
        className="text-button"
        disabled={pending}
        onClick={reload}
      >
        Tải lại bản đã lưu (bỏ thay đổi chưa lưu)
      </button>
      {!trip && !error && <p role="status">Đang tải chuyến đi…</p>}
      {trip && (
        <>
          <TripForm
            key={`${trip.id}:${trip.revision}`}
            initial={trip}
            onSaved={(value) => {
              setTrip(value);
              setSavedNotice(true);
              setError("");
            }}
          />
          <TripRecommendations
            key={`recommendations:${trip.id}:${trip.revision}`}
            tripId={trip.id}
            revision={trip.revision}
          />
          <section className="delete-panel">
            <p>Chỉ xóa khi bạn không cần bản nháp này nữa.</p>
            {!confirmDelete ? (
              <button
                className="danger-button"
                type="button"
                onClick={() => setConfirmDelete(true)}
              >
                Xóa chuyến đi
              </button>
            ) : (
              <div role="group" aria-label="Xác nhận xóa">
                <p>Xóa vĩnh viễn “{trip.title}”?</p>
                <button
                  className="danger-button"
                  disabled={pending}
                  onClick={remove}
                >
                  {pending ? "Đang xóa…" : "Xác nhận xóa"}
                </button>
                <button
                  type="button"
                  disabled={pending}
                  onClick={() => setConfirmDelete(false)}
                >
                  Giữ lại
                </button>
              </div>
            )}
          </section>
        </>
      )}
    </>
  );
}

export default function TripPage() {
  const { id } = useParams<{ id: string }>();
  const { session, loading, configured } = useAuth();
  return (
    <main className="narrow-page">
      <header className="topbar">
        <Link href="/" className="wordmark">
          wayo↗
        </Link>
        <AccountNav />
      </header>
      <p className="back-link">
        <Link href="/trips">← Chuyến đi của tôi</Link>
      </p>
      {loading ? (
        <p role="status">Đang kiểm tra phiên đăng nhập…</p>
      ) : !configured ? (
        <p>Tính năng tài khoản chưa được mở ở bản này.</p>
      ) : !session ? (
        <p>
          <Link href="/login">Đăng nhập</Link> để xem chuyến đi.
        </p>
      ) : (
        <Editor key={`${session.user.id}:${id}`} id={id} />
      )}
    </main>
  );
}
