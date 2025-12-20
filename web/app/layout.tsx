import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Video Generator Pro - Create Stunning Videos in Minutes",
  description: "Transform your ideas into professional videos with AI. Powered by cutting-edge technology for TikTok, YouTube, and Instagram creators.",
  keywords: "AI video generator, video creation, TikTok videos, YouTube shorts, content creation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen gradient-mesh`}>
        {children}
      </body>
    </html>
  );
}
