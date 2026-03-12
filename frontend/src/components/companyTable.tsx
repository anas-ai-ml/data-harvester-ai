"use client";

import { useMemo, useRef, useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { useVirtualizer } from "@tanstack/react-virtual";
import { ColumnDef, SortingState, flexRender, getCoreRowModel, getSortedRowModel, useReactTable } from "@tanstack/react-table";
import { ArrowUpDown, ExternalLink, Inbox, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useCompanyStore } from "@/store/companyStore";
import type { CompanyRecord } from "@/types/company";

const columns: ColumnDef<CompanyRecord>[] = [
  { accessorKey: "SL No.", header: "SL No." },
  {
    accessorKey: "Company Name",
    header: ({ column }) => (
      <button className="inline-flex items-center gap-2" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
        Company Name <ArrowUpDown className="size-3.5" />
      </button>
    ),
    cell: ({ row }) => <span className="font-medium text-white">{row.original["Company Name"]}</span>,
  },
  {
    accessorKey: "Website",
    header: "Website",
    cell: ({ row }) => {
      const website = row.original.Website;
      return website ? (
        <a className="inline-flex items-center gap-1 text-[var(--accent-soft)] hover:underline" href={website} rel="noreferrer" target="_blank">
          Visit <ExternalLink className="size-3.5" />
        </a>
      ) : (
        <span className="text-[var(--muted-foreground)]">-</span>
      );
    },
  },
  { accessorKey: "Owner/ IT Head/ CEO/Finance Head Name", header: "Owner / CEO" },
  { accessorKey: "Phone Number", header: "Phone" },
  { accessorKey: "EMail Address", header: "Email" },
  { accessorKey: "Address", header: "Address" },
  { accessorKey: "Industry_Type", header: "Industry" },
  { accessorKey: "Employee _No", header: "Employees" },
  { accessorKey: "Branch/ Warehouse _No", header: "Branches" },
  { accessorKey: "Annual_Turnover", header: "Turnover" },
  { accessorKey: "Current_Use_ERP Software_Name", header: "ERP" },
  { accessorKey: "Additional_Information", header: "Additional Information" },
];

export function CompanyTable() {
  const { companies, filters, setFilters, selectedCompany, setSelectedCompany, error } = useCompanyStore();
  const [sorting, setSorting] = useState<SortingState>([]);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const gridTemplateColumns = "120px repeat(12, minmax(180px, 1fr))";

  const filteredCompanies = useMemo(() => {
    return companies.filter((company) => {
      const haystack = Object.values(company).join(" ").toLowerCase();
      const matchesSearch = filters.search ? haystack.includes(filters.search.toLowerCase()) : true;
      const matchesIndustry = filters.industry === "all" ? true : company.Industry_Type === filters.industry;
      const matchesErp = filters.erp === "all" ? true : company["Current_Use_ERP Software_Name"] === filters.erp;
      return matchesSearch && matchesIndustry && matchesErp;
    });
  }, [companies, filters]);

  const table = useReactTable({
    data: filteredCompanies,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  const rows = table.getRowModel().rows;
  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => containerRef.current,
    estimateSize: () => 58,
    overscan: 10,
  });

  const industries = Array.from(new Set(companies.map((company) => company.Industry_Type).filter(Boolean)));
  const erpOptions = Array.from(new Set(companies.map((company) => company["Current_Use_ERP Software_Name"]).filter(Boolean)));

  return (
    <Card className="space-y-5 p-0">
      <div className="flex flex-col gap-4 border-b border-white/10 p-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h3 className="text-2xl font-semibold text-white">Scraped companies</h3>
          <p className="mt-1 text-sm text-[var(--muted-foreground)]">Virtualized browsing for high-volume intelligence datasets.</p>
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          <Input placeholder="Search companies..." value={filters.search} onChange={(event) => setFilters({ search: event.target.value })} />
          <select className="h-11 rounded-2xl border border-white/10 bg-[var(--panel)] px-4 text-sm text-white" value={filters.industry} onChange={(event) => setFilters({ industry: event.target.value })}>
            <option value="all">All industries</option>
            {industries.map((industry) => (
              <option key={industry} value={industry}>{industry}</option>
            ))}
          </select>
          <select className="h-11 rounded-2xl border border-white/10 bg-[var(--panel)] px-4 text-sm text-white" value={filters.erp} onChange={(event) => setFilters({ erp: event.target.value })}>
            <option value="all">All ERP usage</option>
            {erpOptions.map((erp) => (
              <option key={erp} value={erp}>{erp}</option>
            ))}
          </select>
        </div>
      </div>

      {error ? <div className="px-6 text-sm text-rose-300">{error}</div> : null}
      {!companies.length ? (
        <div className="grid place-items-center gap-3 px-6 py-20 text-center">
          <div className="grid size-16 place-items-center rounded-full bg-white/5">
            <Inbox className="size-7 text-[var(--muted-foreground)]" />
          </div>
          <h4 className="text-xl font-semibold text-white">No company records yet</h4>
          <p className="max-w-xl text-sm text-[var(--muted-foreground)]">Start a scrape from the Scraper page and the backend API will populate this table with real results.</p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto px-6">
            <div className="grid gap-px border-b border-white/10 bg-white/5 py-3 text-xs uppercase tracking-[0.18em] text-[var(--muted-foreground)]" style={{ gridTemplateColumns }}>
              {table.getHeaderGroups()[0]?.headers.map((header) => (
                <div key={header.id}>{flexRender(header.column.columnDef.header, header.getContext())}</div>
              ))}
            </div>
          </div>

          <div className="overflow-x-auto px-6 pb-6">
            <div className="h-[620px] min-w-[2600px] overflow-auto" ref={containerRef}>
              <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, position: "relative" }}>
                {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                  const row = rows[virtualRow.index];
                  return (
                    <button
                      key={row.id}
                      className="grid w-full gap-px rounded-2xl border border-transparent px-0 text-left transition hover:border-white/10 hover:bg-white/5"
                      onClick={() => setSelectedCompany(row.original)}
                      style={{ position: "absolute", top: 0, left: 0, transform: `translateY(${virtualRow.start}px)`, gridTemplateColumns }}
                    >
                      {row.getVisibleCells().map((cell) => (
                        <div key={cell.id} className="truncate px-3 py-4 text-sm text-[var(--muted-foreground)]">
                          {cell.column.columnDef.cell ? flexRender(cell.column.columnDef.cell, cell.getContext()) : String(cell.getValue() ?? "-")}
                        </div>
                      ))}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </>
      )}

      <Dialog.Root open={Boolean(selectedCompany)} onOpenChange={(open) => !open && setSelectedCompany(null)}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm" />
          <Dialog.Content className="fixed left-1/2 top-1/2 z-50 max-h-[90vh] w-[min(860px,92vw)] -translate-x-1/2 -translate-y-1/2 overflow-auto rounded-[32px] border border-white/10 bg-[var(--panel)] p-8 shadow-[0_30px_120px_rgba(0,0,0,0.4)]">
            <div className="flex items-start justify-between gap-4">
              <div>
                <Dialog.Title className="text-3xl font-semibold text-white">{selectedCompany?.["Company Name"]}</Dialog.Title>
                <Dialog.Description className="mt-2 text-sm text-[var(--muted-foreground)]">Complete company intelligence profile.</Dialog.Description>
              </div>
              <Dialog.Close asChild>
                <Button variant="ghost" size="sm"><X className="size-4" /></Button>
              </Dialog.Close>
            </div>

            {selectedCompany ? (
              <div className="mt-8 grid gap-4 md:grid-cols-2">
                {Object.entries(selectedCompany).map(([key, value]) => (
                  <div key={key} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-[var(--muted-foreground)]">{key}</p>
                    <div className="mt-3 flex items-start gap-2">
                      {key === "Current_Use_ERP Software_Name" && value ? <Badge variant="accent">{String(value)}</Badge> : null}
                      <p className="text-sm text-white">{String(value || "-")}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : null}
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </Card>
  );
}
