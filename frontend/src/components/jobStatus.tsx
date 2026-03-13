"use client";

import { useEffect, useRef } from "react";
import { Activity, CheckCircle2, AlertTriangle, RefreshCw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { useScraperStore } from "@/store/scraperStore";
import { useCompanyStore } from "@/store/companyStore";

const POLL_INTERVAL_MS = 1_500; // poll every 1.5 s while a job is Running

export function JobStatus() {
  const { currentJob, jobStatus, progress, error, pollActiveJob } = useScraperStore();
  const { fetchCompanies } = useCompanyStore();

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  /**
   * While a job is in Running state, poll the backend every POLL_INTERVAL_MS
   * to get updated progress / status. When the job finishes, also refresh
   * the companies list so the Results page reflects new data without reload.
   */
  useEffect(() => {
    if (jobStatus === "Running") {
      intervalRef.current = setInterval(async () => {
        await pollActiveJob();
        // After polling, if the job just completed, fetch companies
        const latestStatus = useScraperStore.getState().jobStatus;
        if (latestStatus !== "Running") {
          void fetchCompanies();
          if (intervalRef.current) clearInterval(intervalRef.current);
        }
      }, POLL_INTERVAL_MS);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [jobStatus, pollActiveJob, fetchCompanies]);

  const Icon =
    jobStatus === "Completed"
      ? CheckCircle2
      : jobStatus === "Failed"
        ? AlertTriangle
        : Activity;

  const badgeVariant =
    jobStatus === "Completed"
      ? "success"
      : jobStatus === "Failed"
        ? "danger"
        : "accent";

  return (
    <Card className="overflow-hidden">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.22em] text-[var(--muted-foreground)]">Job monitor</p>
          <h3 className="mt-2 text-2xl font-semibold text-white">
            {currentJob?.query ?? "No active scrape yet"}
          </h3>
        </div>
        <Badge variant={badgeVariant} className="gap-2">
          <Icon className="size-3.5" />
          {jobStatus}
          {jobStatus === "Running" && (
            <RefreshCw className="size-3 animate-spin" />
          )}
        </Badge>
      </div>

      <div className="mt-6 space-y-3">
        <div className="flex items-center justify-between text-sm text-[var(--muted-foreground)]">
          <span>Progress</span>
          <span>{progress}%</span>
        </div>
        <div className="h-3 rounded-full bg-white/10 overflow-hidden">
          <div
            className="h-3 rounded-full bg-[linear-gradient(90deg,var(--accent),#2ad4ff)] transition-all duration-700"
            style={{ width: `${progress}%` }}
          />
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
