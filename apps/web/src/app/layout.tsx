import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "./components/layout/Sidebar";

export const metadata: Metadata = {
  title: "Agentic IAM Platform",
  description: "Identity and Access Management Intelligence Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans">
        <div className="flex h-screen">
          <Sidebar />
          <main className="flex-1 overflow-auto">
            <div className="p-6">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}
