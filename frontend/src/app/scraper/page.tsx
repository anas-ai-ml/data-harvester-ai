import { JobStatus } from "@/components/jobStatus";
import { QueryForm } from "@/components/queryForm";
import { Card } from "@/components/ui/card";

export default function ScraperPage() {
  return (
    <div className="space-y-8">
      <section>
        <p className="text-sm uppercase tracking-[0.24em] text-[var(--muted-foreground)]">Scraper control</p>
        <h2 className="mt-2 text-4xl font-semibold text-white">Launch a new global company harvest</h2>
        <p className="mt-3 max-w-3xl text-base text-[var(--muted-foreground)]">
          Define keywords, optional geography, and the business directories or web sources you want the engine to search.
        </p>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.25fr_0.9fr]">
        <Card>
          <QueryForm />
        </Card>
        <JobStatus />
      </div>
    </div>
  );
}
