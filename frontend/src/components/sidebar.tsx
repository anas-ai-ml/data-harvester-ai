"use client";

import type { ComponentType } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, BriefcaseBusiness, Cog, Database, PlayCircle, Rows3 } from "lucide-react";

import { cn } from "@/lib/utils";

const items: { href: string; label: string; icon: ComponentType<{ className?: string }> }[] = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/scraper", label: "Scraper", icon: PlayCircle },
  { href: "/jobs", label: "Jobs", icon: BriefcaseBusiness },
  { href: "/results", label: "Results", icon: Rows3 },
  { href: "/settings", label: "Settings", icon: Cog },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-full flex-col rounded-[32px] border border-white/10 bg-[radial-gradient(circle_at_top,rgba(11,94,215,0.24),transparent_38%),rgba(255,255,255,0.04)] p-5 shadow-[0_30px_90px_rgba(0,0,0,0.25)] backdrop-blur-xl">
      <div className="mb-10 flex items-center gap-3 px-2">
        <div className="grid size-11 place-items-center rounded-2xl bg-[linear-gradient(135deg,var(--accent),#2ad4ff)] text-lg font-black text-[var(--accent-foreground)]">
          DH
        </div>
        <div>
          <p className="text-sm uppercase tracking-[0.28em] text-[var(--muted-foreground)]">DataHarvester</p>
          <h1 className="text-lg font-semibold text-white">Company Intelligence</h1>
        </div>
      </div>

      <nav className="space-y-2">
        {items.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition",
                active
                  ? "bg-white text-slate-950 shadow-[0_16px_35px_rgba(255,255,255,0.16)]"
                  : "text-[var(--muted-foreground)] hover:bg-white/6 hover:text-white",
              )}
            >
              <Icon className="size-4" />
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto rounded-[24px] border border-white/10 bg-black/20 p-4">
        <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
          <Database className="size-4 text-[var(--accent-soft)]" />
          Live Throughput
        </div>
        <p className="text-3xl font-semibold text-white">50K</p>
        <p className="mt-1 text-sm text-[var(--muted-foreground)]">Records supported in virtualized results view.</p>
      </div>
    </aside>
  );
}
