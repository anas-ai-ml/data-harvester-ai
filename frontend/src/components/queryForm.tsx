"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SourceSelector } from "@/components/sourceSelector";
import { useScraperStore } from "@/store/scraperStore";
import type { ScrapeSource } from "@/types/job";
import { MapPin, Briefcase, Search, Sparkles } from "lucide-react";

const defaultSources: ScrapeSource[] = ["google", "linkedin", "website"];

export function QueryForm() {
  const { startScrape, loading, currentJob } = useScraperStore();
  const [keyword, setKeyword] = useState("");
  const [industry, setIndustry] = useState("");
  const [location, setLocation] = useState("");
  const [sources, setSources] = useState<ScrapeSource[]>(defaultSources);

  return (
    <form
      className="space-y-8 animate-in fade-in duration-700 relative"
      onSubmit={async (event) => {
        event.preventDefault();
        if (!sources.length) return;
        await startScrape({ keyword, industry, location, sources });
      }}
    >
      <div className="space-y-5">
        <div className="group relative">
          <label className="mb-2 flex items-center gap-2 text-sm font-medium text-white/80 transition-colors group-hover:text-white">
            <Search className="h-4 w-4 text-primary/60" />
            Target Keyword
          </label>
          <div className="relative">
            <div className="absolute -inset-0.5 rounded-lg bg-gradient-to-r from-primary/30 to-purple-500/30 opacity-0 blur transition duration-500 group-hover:opacity-100" />
            <Input
              className="relative bg-zinc-900/50 backdrop-blur-sm border-white/10 text-lg transition-all focus:bg-zinc-900"
              value={keyword}
              onChange={(event) => setKeyword(event.target.value)}
              placeholder="e.g. wholesale furniture manufacturers"
              required
            />
          </div>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          <div className="group relative">
            <label className="mb-2 flex items-center gap-2 text-sm font-medium text-white/80 transition-colors group-hover:text-white">
              <Briefcase className="h-4 w-4 text-primary/60" />
              Industry
            </label>
            <Input
              className="bg-zinc-900/50 backdrop-blur-sm border-white/10 transition-all focus:bg-zinc-900 focus:border-primary/50"
              value={industry}
              onChange={(event) => setIndustry(event.target.value)}
              placeholder="e.g. retail, mining"
            />
          </div>

          <div className="group relative">
            <label className="mb-2 flex items-center gap-2 text-sm font-medium text-white/80 transition-colors group-hover:text-white">
              <MapPin className="h-4 w-4 text-primary/60" />
              Location
            </label>
            <Input
              className="bg-zinc-900/50 backdrop-blur-sm border-white/10 transition-all focus:bg-zinc-900 focus:border-primary/50"
              value={location}
              onChange={(event) => setLocation(event.target.value)}
              placeholder="City, region, or country"
            />
          </div>
        </div>

        {/* Source selector — now wired up and functional */}
        <div>
          <label className="mb-3 block text-sm font-medium text-white/80">
            Data Sources
          </label>
          <SourceSelector value={sources} onChange={setSources} />
          {sources.length === 0 && (
            <p className="mt-2 text-xs text-rose-400">Select at least one source.</p>
          )}
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-white/5">
        <Button
          disabled={loading || sources.length === 0}
          type="submit"
          className="w-full sm:w-auto px-8 bg-gradient-to-r from-primary to-purple-600 hover:from-primary/80 hover:to-purple-500/80 text-white shadow-[0_0_20px_rgba(var(--primary),0.3)] transition-all duration-300 hover:shadow-[0_0_30px_rgba(var(--primary),0.5)] hover:scale-105"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/20 border-t-white" />
              Initializing Harvest...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Start Extraction
            </span>
          )}
        </Button>

        {currentJob ? (
          <div className="flex items-center gap-3 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 animate-in slide-in-from-right-4">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary"></span>
            </span>
            <p className="text-sm font-medium text-primary/90">
              Active Job <span className="font-bold text-primary">#{currentJob.id.split("-")[1]}</span>
            </p>
          </div>
        ) : null}
      </div>
    </form>
  );
}
