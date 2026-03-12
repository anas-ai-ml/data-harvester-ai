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
