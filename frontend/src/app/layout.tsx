import type { Metadata } from "next";
import type { ReactNode } from "react";

import { Navbar } from "@/components/navbar";
import { Sidebar } from "@/components/sidebar";

import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "DataHarvester Frontend",
  description: "Company intelligence dashboard for global scraping operations.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen p-3 md:p-5">
          <div className="grid min-h-[calc(100vh-1.5rem)] gap-3 lg:grid-cols-[290px_1fr]">
            <div className="lg:sticky lg:top-5 lg:h-[calc(100vh-2.5rem)]">
              <Sidebar />
            </div>
            <div className="rounded-[32px] border border-white/10 bg-[rgba(255,255,255,0.03)] shadow-[0_30px_120px_rgba(0,0,0,0.28)] backdrop-blur-xl">
              <Navbar />
              <main className="p-4 md:p-8">{children}</main>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
