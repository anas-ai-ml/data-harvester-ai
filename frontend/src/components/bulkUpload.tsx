"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { SourceSelector } from "@/components/sourceSelector";
import { useScraperStore } from "@/store/scraperStore";
import type { ScrapeSource } from "@/types/job";
import { Upload, FileJson, CheckCircle2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

const defaultSources: ScrapeSource[] = ["google", "linkedin", "website"];

export function BulkUpload() {
  const { uploadParams, loading } = useScraperStore();
  const [file, setFile] = useState<File | null>(null);
  const [sources, setSources] = useState<ScrapeSource[]>(defaultSources);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
      setSuccess(false);
    }
  };

  const handleUpload = async () => {
    if (!file || sources.length === 0) return;
    try {
      await uploadParams(file, sources.join(","));
      setSuccess(true);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div
        onClick={() => fileInputRef.current?.click()}
        className={cn(
          "relative group cursor-pointer border-2 border-dashed rounded-2xl p-8 transition-all duration-300 text-center",
          file
            ? "border-primary/50 bg-primary/5"
            : "border-white/10 hover:border-white/20 hover:bg-white/[0.02]",
        )}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".json,.csv"
          className="hidden"
        />

        <div className="flex flex-col items-center gap-3">
          {file ? (
            <div className="p-4 rounded-full bg-primary/20 text-primary animate-in zoom-in">
              <FileJson className="h-8 w-8" />
            </div>
          ) : (
            <div className="p-4 rounded-full bg-white/5 text-white/40 group-hover:text-white/60 transition-colors">
              <Upload className="h-8 w-8" />
            </div>
          )}

          <div>
            <p className="font-semibold text-white">
              {file ? file.name : "Upload Parameters File"}
            </p>
            <p className="text-sm text-white/50 mt-1">Supports .json or .csv files</p>
          </div>
        </div>
      </div>

      {/* Source selector for bulk uploads */}
      <div>
        <label className="mb-3 block text-sm font-medium text-white/80">
          Data Sources
        </label>
        <SourceSelector value={sources} onChange={setSources} />
        {sources.length === 0 && (
          <p className="mt-2 text-xs text-rose-400">Select at least one source.</p>
        )}
      </div>

      <div className="flex flex-col gap-3">
        <Button
          onClick={handleUpload}
          disabled={!file || loading || sources.length === 0}
          className="w-full bg-white text-black hover:bg-white/90 font-bold h-12 rounded-xl transition-all disabled:opacity-50"
        >
          {loading ? "Processing File..." : "Start Bulk Extraction"}
        </Button>

        {success && (
          <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium animate-in fade-in slide-in-from-top-2">
            <CheckCircle2 className="h-4 w-4" />
            Bulk job started successfully!
          </div>
        )}
      </div>

      <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
        <div className="flex gap-3">
          <AlertCircle className="h-5 w-5 text-blue-400 shrink-0" />
          <div className="text-xs text-blue-200/70 leading-relaxed">
            <p className="font-semibold text-blue-200 mb-1">Upload format guide:</p>
            <ul className="list-disc pl-4 space-y-1">
              <li>JSON: Array of objects with &quot;Company Name&quot; or &quot;Website&quot;</li>
              <li>CSV: Columns for &quot;Company Name&quot;, &quot;Industry&quot;, &quot;Location&quot;</li>
              <li>The system will automatically generate search queries for each row.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
