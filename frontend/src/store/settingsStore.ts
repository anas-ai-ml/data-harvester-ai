"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { DashboardSettings } from "@/types/settings";

type SettingsState = {
  settings: DashboardSettings;
  updateSettings: (patch: Partial<DashboardSettings>) => void;
};

const defaultSettings: DashboardSettings = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
  googleSheetName: "DataHarvester Results",
  googleWorksheetName: "Companies",
  apiKey: "",
  requestsPerMinute: "120",
  proxyUrl: "",
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      settings: defaultSettings,
      updateSettings: (patch) => set((state) => ({ settings: { ...state.settings, ...patch } })),
    }),
    { name: "dh-settings-store" },
  ),
);
