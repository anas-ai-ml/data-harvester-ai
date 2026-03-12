export type CompanyRecord = {
  "SL No.": string;
  "Company Name": string;
  Website: string;
  "Owner/ IT Head/ CEO/Finance Head Name": string;
  "Phone Number": string;
  "EMail Address": string;
  Address: string;
  Industry_Type: string;
  "Employee _No": string;
  "Branch/ Warehouse _No": string;
  Annual_Turnover: string;
  "Current_Use_ERP Software_Name": string;
  Additional_Information: string;
  id?: string;
  country?: string;
  source?: string;
};

export type CompanyFilters = {
  search: string;
  industry: string;
  erp: string;
};
