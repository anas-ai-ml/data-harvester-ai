"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SourceSelector } from "@/components/sourceSelector";
import { useScraperStore } from "@/store/scraperStore";
import type { ScrapeSource } from "@/types/job";

const defaultSources: ScrapeSource[] = ["google", "linkedin", "website"];

export function QueryForm() {
  const { startScrape, loading, currentJob } = useScraperStore();
  const [keyword, setKeyword] = useState("");
  const [industry, setIndustry] = useState("");
  const [location, setLocation] = useState("");
  const [sources, setSources] = useState<ScrapeSource[]>(defaultSources);

  return (
    <form
      className="space-y-6"
      onSubmit={async (event) => {
        event.preventDefault();
        await startScrape({ keyword, industry, location, sources });
      }}
    >
      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <label className="mb-2 block text-sm text-[var(--muted-foreground)]">Keyword</label>
          <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="e.g. furniture manufacturers" required />
        </div>
        <div>
          <label className="mb-2 block text-sm text-[var(--muted-foreground)]">Industry</label>
          <Input value={industry} onChange={(event) => setIndustry(event.target.value)} placeholder="e.g. retail, mining, logistics" />
        </div>
        <div>
          <label className="mb-2 block text-sm text-[var(--muted-foreground)]">Location</label>
          <Input value={location} onChange={(event) => setLocation(event.target.value)} placeholder="Optional city, country, or region" />
        </div>
      </div>

      <div>
        <label className="mb-3 block text-sm text-[var(--muted-foreground)]">Sources to scrape</label>
        <SourceSelector value={sources} onChange={setSources} />
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <Button disabled={loading || sources.length === 0} type="submit">
          {loading ? "Starting..." : "Start Scraping"}
        </Button>
        {currentJob ? (
          <p className="text-sm text-[var(--muted-foreground)]">
            Active job <span className="font-semibold text-white">{currentJob.id}</span> for query <span className="font-semibold text-white">{currentJob.query}</span>
          </p>
        ) : null}
      </div>
    </form>
  );
}
