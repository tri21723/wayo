import { TripForm } from "@/components/trip-form";
import Link from "next/link";
import { AccountNav } from "@/components/account-nav";

export default function Home() {
  return (
    <main>
      <header className="topbar">
        <Link className="wordmark" href="/" aria-label="Wayo — Trang chủ">
          wayo<span>↗</span>
        </Link>
        <AccountNav />
      </header>
      <section className="intro">
        <p className="eyebrow">TRAVEL YOUR WAY</p>
        <h1>
          Chuyến đi của bạn.
          <br />
          <span>Theo cách của bạn.</span>
        </h1>
        <p>
          Một cuối tuần nhiều trải nghiệm, hay vài ngày thật thảnh thơi? Bắt đầu
          với những điều bạn muốn cho chuyến đi Đà Lạt.
        </p>
      </section>
      <div className="workspace">
        <TripForm />
        <aside className="guide">
          <span className="guide-icon" aria-hidden="true">
            ↗
          </span>
          <p className="eyebrow">BẮT ĐẦU TỪ BẠN</p>
          <h2>
            Ít vội vã hơn.
            <br />
            Đúng gu hơn.
          </h2>
          <p>
            Cho Wayo biết thời gian, người đồng hành và ngân sách. Đây sẽ là nền
            tảng để chọn trải nghiệm phù hợp.
          </p>
          <ol>
            <li>
              <strong>Điều kiện chuyến đi</strong>
              <span>Ngày đến, ngày về, ngân sách.</span>
            </li>
            <li>
              <strong>Gu du lịch của bạn</strong>
              <span>Những điều bạn thích và muốn tránh.</span>
            </li>
            <li>
              <strong>Lịch trình phù hợp</strong>
              <span>Timeline, bản đồ và điều chỉnh — đang phát triển.</span>
            </li>
          </ol>
          <p className="development-note">
            Kiểm tra thông tin và lưu bản nháp vào tài khoản của bạn. Lịch trình
            AI đang được phát triển.
          </p>
        </aside>
      </div>
      <footer>Wayo · Khởi đầu từ Đà Lạt, dành cho cách đi của bạn.</footer>
    </main>
  );
}
