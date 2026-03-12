import { BriefcaseBusiness, Database, Radar, Workflow } from "lucide-react";

import { Card } from "@/components/ui/card";
import { formatNumber } from "@/lib/utils";

type StatsCardProps = {
  title: string;
  value: number;
  note: string;
  icon: "companies" | "jobs" | "active" | "erp";
};

const icons = {
  companies: Database,
  jobs: BriefcaseBusiness,
  active: Radar,
  erp: Workflow,
};

export function StatsCards({ items }: { items: StatsCardProps[] }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => {
        const Icon = icons[item.icon];
        return (
          <Card key={item.title} className="relative overflow-hidden">
            <div className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,var(--accent),#2ad4ff)]" />
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm text-[var(--muted-foreground)]">{item.title}</p>
                <p className="mt-3 text-4xl font-semibold tracking-tight text-white">{formatNumber(item.value)}</p>
                <p className="mt-2 text-sm text-[var(--muted-foreground)]">{item.note}</p>
              </div>
              <div className="grid size-12 place-items-center rounded-2xl bg-white/8">
                <Icon className="size-5 text-[var(--accent-soft)]" />
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
