"use client";

import { useEffect } from "react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { useScraperStore } from "@/store/scraperStore";

export default function JobsPage() {
  const { jobs, fetchJobs } = useScraperStore();

  useEffect(() => {
    void fetchJobs();
  }, [fetchJobs]);

  return (
    <div className="space-y-8">
      <section>
        <p className="text-sm uppercase tracking-[0.24em] text-[var(--muted-foreground)]">Operations</p>
        <h2 className="mt-2 text-4xl font-semibold text-white">Scraping job monitor</h2>
        <p className="mt-3 max-w-3xl text-base text-[var(--muted-foreground)]">
          Watch every job move from discovery through extraction and schema formatting, with status, record count, and progress visibility.
        </p>
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
          {jobs.map((job) => (
            <div key={job.id} className="grid grid-cols-6 items-center px-6 py-4 text-sm text-[var(--muted-foreground)]">
              <div className="font-medium text-white">{job.id}</div>
              <div>{job.query}</div>
              <div>
                <Badge variant={job.status === "Completed" ? "success" : job.status === "Failed" ? "danger" : "accent"}>{job.status}</Badge>
              </div>
              <div>{job.recordsFound}</div>
              <div>{new Date(job.startTime).toLocaleString()}</div>
              <div>{job.progress}%</div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
