"use client";

import { useEffect } from "react";

import { CompanyTable } from "@/components/companyTable";
import { ExportButtons } from "@/components/exportButtons";
import { Card } from "@/components/ui/card";
import { useCompanyStore } from "@/store/companyStore";

export default function ResultsPage() {
  const { companies, fetchCompanies } = useCompanyStore();

  useEffect(() => {
    void fetchCompanies();
  }, [fetchCompanies]);

  return (
    <div className="space-y-8">
      <section className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-[var(--muted-foreground)]">Results explorer</p>
          <h2 className="mt-2 text-4xl font-semibold text-white">Structured company intelligence records</h2>
          <p className="mt-3 max-w-3xl text-base text-[var(--muted-foreground)]">
            Search, sort, filter, and inspect every company in the mandatory schema before exporting or syncing to Sheets.
          </p>
        </div>
        <ExportButtons companies={companies} />
      </section>

      <CompanyTable />

      <Card>
        <p className="text-sm text-[var(--muted-foreground)]">
          The results table uses TanStack Table for column behavior and TanStack Virtual for high-volume rendering.
        </p>
      </Card>
    </div>
  );
}
