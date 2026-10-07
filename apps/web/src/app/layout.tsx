import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Wayo — Chuyến đi theo cách của bạn",
  description: "Bắt đầu lên kế hoạch cho chuyến đi Đà Lạt cùng Wayo.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
