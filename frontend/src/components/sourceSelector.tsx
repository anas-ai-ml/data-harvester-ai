"use client";

import * as Checkbox from "@radix-ui/react-checkbox";
import { Check } from "lucide-react";

import type { ScrapeSource } from "@/types/job";
import { cn } from "@/lib/utils";

const sourceOptions: { value: ScrapeSource; label: string }[] = [
  { value: "google", label: "Google" },
  { value: "maps", label: "Google Maps" },
  { value: "indiamart", label: "IndiaMART" },
  { value: "tradeindia", label: "TradeIndia" },
  { value: "justdial", label: "JustDial" },
  { value: "linkedin", label: "LinkedIn" },
  { value: "website", label: "Company Websites" },
];

export function SourceSelector({ value, onChange }: { value: ScrapeSource[]; onChange: (sources: ScrapeSource[]) => void }) {
  const toggle = (source: ScrapeSource) => {
    onChange(value.includes(source) ? value.filter((item) => item !== source) : [...value, source]);
  };

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {sourceOptions.map((source) => {
        const checked = value.includes(source.value);
        return (
          <label
            key={source.value}
            className={cn(
              "flex cursor-pointer items-center justify-between rounded-2xl border px-4 py-3 text-sm transition",
              checked ? "border-[var(--accent)] bg-[var(--accent)]/10 text-white" : "border-white/10 bg-white/5 text-[var(--muted-foreground)]",
            )}
          >
            <span>{source.label}</span>
            <Checkbox.Root
              checked={checked}
              onCheckedChange={() => toggle(source.value)}
              className="grid size-5 place-items-center rounded-md border border-white/20 bg-black/20"
            >
              <Checkbox.Indicator>
                <Check className="size-4 text-[var(--accent-soft)]" />
              </Checkbox.Indicator>
            </Checkbox.Root>
          </label>
        );
      })}
    </div>
  );
}
