"use client";

import { useEffect } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useScraperStore } from "@/store/scraperStore";
import { Trash2, RefreshCw, Inbox } from "lucide-react";

export default function JobsPage() {
  const { jobs, fetchJobs, clearJobs, loading } = useScraperStore();

  useEffect(() => {
    void fetchJobs();
  }, [fetchJobs]);

  return (
    <div className="space-y-8">
      <section className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-[var(--muted-foreground)]">Operations</p>
          <h2 className="mt-2 text-4xl font-semibold text-white">Scraping job monitor</h2>
          <p className="mt-3 max-w-3xl text-base text-[var(--muted-foreground)]">
            Watch every job move from discovery through extraction and schema formatting, with status,
            record count, and progress visibility.
          </p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={() => void fetchJobs()}
            disabled={loading}
            className="gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => void clearJobs()}
            disabled={loading || jobs.length === 0}
            className="gap-2 border-rose-500/30 text-rose-400 hover:bg-rose-500/10 hover:text-rose-300"
          >
            <Trash2 className="h-4 w-4" />
            Clear All
          </Button>
        </div>
      </section>

      <Card className="overflow-hidden p-0">
        <div className="grid grid-cols-6 border-b border-white/10 bg-white/5 px-6 py-4 text-xs uppercase tracking-[0.18em] text-[var(--muted-foreground)]">
          <div>Job ID</div>
          <div>Query</div>
          <div>Status</div>
          <div>Records Found</div>
          <div>Start Time</div>
          <div>Progress %</div>
        </div>
        <div className="divide-y divide-white/8">
          {jobs.length === 0 ? (
            <div className="grid place-items-center gap-3 py-20 text-center">
              <div className="grid size-16 place-items-center rounded-full bg-white/5">
                <Inbox className="size-7 text-[var(--muted-foreground)]" />
              </div>
              <p className="text-sm text-[var(--muted-foreground)]">No jobs yet. Start a scrape from the Scraper page.</p>
            </div>
          ) : (
            jobs.map((job) => (
              <div
                key={job.id}
                className="grid grid-cols-6 items-center px-6 py-4 text-sm text-[var(--muted-foreground)]"
              >
                <div className="font-medium text-white font-mono text-xs">{job.id}</div>
                <div className="truncate pr-4">{job.query}</div>
                <div>
                  <Badge
                    variant={
                      job.status === "Completed"
                        ? "success"
                        : job.status === "Failed"
                          ? "danger"
                          : "accent"
                    }
                  >
                    {job.status}
                  </Badge>
                </div>
                <div>{job.recordsFound}</div>
                <div>{new Date(job.startTime).toLocaleString()}</div>
                <div className="flex items-center gap-2">
                  <div className="h-1.5 flex-1 rounded-full bg-white/10 overflow-hidden">
                    <div
                      className="h-1.5 rounded-full bg-[linear-gradient(90deg,var(--accent),#2ad4ff)] transition-all"
                      style={{ width: `${job.progress}%` }}
                    />
                  </div>
                  <span className="text-xs tabular-nums">{job.progress}%</span>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
}
