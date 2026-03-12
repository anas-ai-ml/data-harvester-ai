"use client";

import { Activity, CheckCircle2, AlertTriangle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { useScraperStore } from "@/store/scraperStore";

export function JobStatus() {
  const { currentJob, jobStatus, progress, error } = useScraperStore();
  const icon = jobStatus === "Completed" ? CheckCircle2 : jobStatus === "Failed" ? AlertTriangle : Activity;
  const Icon = icon;
  const badgeVariant = jobStatus === "Completed" ? "success" : jobStatus === "Failed" ? "danger" : "accent";

  return (
    <Card className="overflow-hidden">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-[var(--muted-foreground)]">Job monitor</p>
          <h3 className="mt-2 text-2xl font-semibold text-white">{currentJob?.query ?? "No active scrape yet"}</h3>
        </div>
        <Badge variant={badgeVariant} className="gap-2">
          <Icon className="size-3.5" />
          {jobStatus}
        </Badge>
      </div>

      <div className="mt-6 space-y-3">
        <div className="flex items-center justify-between text-sm text-[var(--muted-foreground)]">
          <span>Progress</span>
          <span>{progress}%</span>
        </div>
        <div className="h-3 rounded-full bg-white/10">
          <div className="h-3 rounded-full bg-[linear-gradient(90deg,var(--accent),#2ad4ff)]" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {currentJob ? (
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted-foreground)]">Job ID</p>
            <p className="mt-2 text-sm text-white">{currentJob.id}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted-foreground)]">Records Found</p>
            <p className="mt-2 text-sm text-white">{currentJob.recordsFound}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted-foreground)]">Sources</p>
            <p className="mt-2 text-sm text-white">{currentJob.sources.join(", ")}</p>
          </div>
        </div>
      ) : null}

      {error ? <p className="mt-5 text-sm text-rose-300">{error}</p> : null}
    </Card>
  );
}
