"use client";

import { Download, FileJson, FileSpreadsheet, Sheet } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { CompanyRecord } from "@/types/company";

function downloadBlob(content: string, filename: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function toCsv(rows: CompanyRecord[]) {
  if (!rows.length) return "";
  const headers = Object.keys(rows[0]);
  return [
    headers.join(","),
    ...rows.map((row) => headers.map((header) => JSON.stringify((row as Record<string, string | undefined>)[header] ?? "")).join(",")),
  ].join("\n");
}

export function ExportButtons({ companies }: { companies: CompanyRecord[] }) {
  return (
    <div className="flex flex-wrap gap-3">
      <Button variant="outline" onClick={() => downloadBlob(toCsv(companies), "companies.csv", "text/csv;charset=utf-8;")}> 
        <Download className="mr-2 size-4" />Export CSV
      </Button>
      <Button variant="outline" onClick={() => downloadBlob(JSON.stringify(companies, null, 2), "companies.json", "application/json")}> 
        <FileJson className="mr-2 size-4" />Export JSON
      </Button>
      <Button variant="outline" onClick={() => downloadBlob(toCsv(companies), "companies.xls", "application/vnd.ms-excel")}> 
        <FileSpreadsheet className="mr-2 size-4" />Export Excel
      </Button>
      <Button variant="default" onClick={() => window.alert("Connect this button to your Google Sheets sync endpoint.")}> 
        <Sheet className="mr-2 size-4" />Push to Google Sheets
      </Button>
    </div>
  );
}
