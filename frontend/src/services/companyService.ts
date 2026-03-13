import { api } from "@/services/api";
import type { CompanyRecord } from "@/types/company";

export async function getCompanies() {
  const { data } = await api.get<CompanyRecord[]>("/api/companies");
  return data;
}

export async function getCompany(id: string) {
  const { data } = await api.get<CompanyRecord>(`/api/company/${id}`);
  return data;
}

export async function pushCompaniesToSheets() {
  const { data } = await api.post<{ success: boolean; rows_synced: number }>("/api/push-to-sheets");
  return data;
}

/**
 * Checks whether the backend has a downloadable results CSV ready.
 * Returns metadata; the actual download is triggered client-side
 * using the in-memory company data to avoid binary streaming complexity.
 */
export async function checkDownloadReady() {
  const { data } = await api.get<{ path: string; size_bytes: number; records: number }>(
    "/api/download/csv",
  );
  return data;
}
