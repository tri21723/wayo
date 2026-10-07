"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AccountNav } from "@/components/account-nav";
import { useAuth } from "@/components/auth-provider";
import {
  getProfile,
  saveProfile,
  type SavedProfile,
  type TasteAnswers,
} from "@/lib/api";

const interests: [TasteAnswers["interests"][number], string][] = [
  ["cafe", "Cà phê"],
  ["nature", "Thiên nhiên"],
  ["photography", "Chụp ảnh"],
  ["food", "Ẩm thực"],
  ["culture", "Văn hóa"],
  ["nightlife", "Hoạt động buổi tối"],
];
const exclusions: [TasteAnswers["exclusions"][number], string][] = [
  ["trekking", "Trekking"],
  ["stairs", "Đường có cầu thang"],
  ["alcohol", "Hoạt động uống rượu bia"],
];
const defaults: TasteAnswers = {
  interests: [],
  pace: "balanced",
  crowd: "neutral",
  adventure: "easy",
  diet: "unrestricted",
  exclusions: [],
};

function ProfileForm({
  initial,
  reload,
}: {
  initial: SavedProfile;
  reload: () => void;
}) {
  const [answers, setAnswers] = useState<TasteAnswers>(
    initial.answers ?? defaults,
  );
  const [revision, setRevision] = useState(initial.revision ?? 0);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  function change<K extends keyof TasteAnswers>(
    key: K,
    value: TasteAnswers[K],
  ) {
    setAnswers((current) => ({ ...current, [key]: value }));
    setSaved(false);
  }
  return (
    <form
      className="form-card taste-form"
      onSubmit={async (event) => {
        event.preventDefault();
        setPending(true);
        setError("");
        setSaved(false);
        try {
          const result = await saveProfile(answers, revision);
          setRevision(result.revision ?? 0);
          setSaved(true);
        } catch (caught) {
          setError(
            caught instanceof Error
              ? caught.message
              : "Chưa lưu được sở thích.",
          );
        } finally {
          setPending(false);
        }
      }}
    >
      <fieldset disabled={pending}>
        <legend>1. Bạn thích trải nghiệm nào? Chọn ít nhất một.</legend>
        <div className="taste-options">
          {interests.map(([value, label]) => (
            <label key={value}>
              <input
                type="checkbox"
                checked={answers.interests.includes(value)}
                onChange={(event) =>
                  change(
                    "interests",
                    event.target.checked
                      ? [...answers.interests, value]
                      : answers.interests.filter((item) => item !== value),
                  )
                }
              />
              {label}
            </label>
          ))}
        </div>
      </fieldset>
      <label>
        2. Nhịp độ chuyến đi
        <select
          disabled={pending}
          value={answers.pace}
          onChange={(e) =>
            change("pace", e.target.value as TasteAnswers["pace"])
          }
        >
          <option value="relaxed">Thong thả</option>
          <option value="balanced">Cân bằng</option>
          <option value="active">Nhiều hoạt động</option>
        </select>
      </label>
      <label>
        3. Không khí bạn yêu thích
        <select
          disabled={pending}
          value={answers.crowd}
          onChange={(e) =>
            change("crowd", e.target.value as TasteAnswers["crowd"])
          }
        >
          <option value="quiet">Yên tĩnh</option>
          <option value="neutral">Không ưu tiên</option>
          <option value="lively">Nhộn nhịp</option>
        </select>
      </label>
      <label>
        4. Mức vận động phù hợp
        <select
          disabled={pending}
          value={answers.adventure}
          onChange={(e) =>
            change("adventure", e.target.value as TasteAnswers["adventure"])
          }
        >
          <option value="easy">Nhẹ nhàng</option>
          <option value="moderate">Vừa phải</option>
          <option value="challenging">Thử thách</option>
        </select>
      </label>
      <label>
        5. Chế độ ăn
        <select
          disabled={pending}
          value={answers.diet}
          onChange={(e) =>
            change("diet", e.target.value as TasteAnswers["diet"])
          }
        >
          <option value="unrestricted">Không giới hạn</option>
          <option value="vegetarian">Ăn chay</option>
          <option value="vegan">Thuần chay</option>
        </select>
      </label>
      <fieldset disabled={pending}>
        <legend>6. Những điều cần tránh (có thể bỏ trống)</legend>
        <div className="taste-options">
          {exclusions.map(([value, label]) => (
            <label key={value}>
              <input
                type="checkbox"
                checked={answers.exclusions.includes(value)}
                onChange={(event) =>
                  change(
                    "exclusions",
                    event.target.checked
                      ? [...answers.exclusions, value]
                      : answers.exclusions.filter((item) => item !== value),
                  )
                }
              />
              {label}
            </label>
          ))}
        </div>
      </fieldset>
      <p>
        Sở thích được lưu vào tài khoản. Các chuyến đi đã tạo giữ nguyên lựa
        chọn riêng; phần gợi ý địa điểm sẽ được bổ sung sau.
      </p>
      {error && (
        <div role="alert" className="message error">
          <p>{error}</p>
          <button type="button" disabled={pending} onClick={reload}>
            Tải lại sở thích đã lưu
          </button>
          <p>Tải lại sẽ bỏ các thay đổi chưa lưu.</p>
        </div>
      )}
      {saved && <p role="status">Đã lưu sở thích của bạn.</p>}
      <button
        className="primary"
        disabled={pending || answers.interests.length === 0}
        type="submit"
      >
        {pending ? "Đang lưu…" : "Lưu sở thích"}
      </button>
    </form>
  );
}

function ProfileLoader() {
  const [data, setData] = useState<SavedProfile | null>(null);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    getProfile()
      .then((value) => {
        if (active) setData(value);
      })
      .catch((caught) => {
        if (active)
          setError(
            caught instanceof Error
              ? caught.message
              : "Chưa tải được sở thích.",
          );
      });
    return () => {
      active = false;
    };
  }, [attempt]);
  function reload() {
    setData(null);
    setError("");
    setAttempt((value) => value + 1);
  }
  if (error)
    return (
      <div role="alert">
        <p>{error}</p>
        <button onClick={reload}>Thử lại</button>
      </div>
    );
  if (!data) return <p role="status">Đang tải sở thích…</p>;
  return <ProfileForm initial={data} reload={reload} />;
}

export default function ProfilePage() {
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
        <p className="eyebrow">GU DU LỊCH CỦA BẠN</p>
        <h1>
          Mỗi chuyến đi,
          <br />
          <span>thêm đúng gu.</span>
        </h1>
        <p>Sáu câu hỏi ngắn. Bạn có thể thay đổi bất cứ lúc nào.</p>
      </section>
      {loading ? (
        <p role="status">Đang kiểm tra phiên đăng nhập…</p>
      ) : !configured ? (
        <p>Tính năng tài khoản chưa được cấu hình.</p>
      ) : !session ? (
        <Link href="/login">Đăng nhập để lưu sở thích →</Link>
      ) : (
        <ProfileLoader key={session.user.id} />
      )}
    </main>
  );
}
