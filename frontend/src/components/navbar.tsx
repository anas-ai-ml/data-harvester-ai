"use client";

import { Search, Bell, UserCircle2 } from "lucide-react";

import { Input } from "@/components/ui/input";

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-[rgba(7,10,18,0.72)] backdrop-blur-xl">
      <div className="flex h-20 items-center justify-between gap-4 px-4 md:px-8">
        <div className="relative max-w-xl flex-1">
          <Search className="pointer-events-none absolute left-4 top-1/2 size-4 -translate-y-1/2 text-[var(--muted-foreground)]" />
          <Input className="pl-10" placeholder="Search companies, jobs, ERP signals..." />
        </div>
        <div className="flex items-center gap-3">
          <button className="rounded-full border border-white/10 bg-white/5 p-3 text-[var(--muted-foreground)] transition hover:text-white">
            <Bell className="size-4" />
          </button>
          <div className="flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2">
            <UserCircle2 className="size-7 text-[var(--accent-soft)]" />
            <div className="hidden text-left sm:block">
              <p className="text-sm font-semibold text-white">Analyst Console</p>
              <p className="text-xs text-[var(--muted-foreground)]">Global Intelligence Team</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
