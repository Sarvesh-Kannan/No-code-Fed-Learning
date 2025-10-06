import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NoCode Federated Learning Platform",
  description: "Build and train ML models without code using federated learning",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">{children}</body>
    </html>
  );
}

