"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import { sanitizeInput } from "@/lib/utils";
import {
  clearJobs as apiClearJobs,
  getJobs,
  startScrape,
  uploadParams as apiUploadParams,
} from "@/services/scraperService";
import type { ScrapeJob, StartScrapePayload } from "@/types/job";

type ScraperState = {
  currentJob: ScrapeJob | null;
  jobStatus: ScrapeJob["status"] | "Idle";
  progress: number;
  jobs: ScrapeJob[];
  loading: boolean;
  error: string | null;
  /** Starts a single-keyword scrape */
  startScrape: (payload: StartScrapePayload) => Promise<void>;
  /** Starts a bulk file-upload scrape */
  uploadParams: (file: File, sources: string) => Promise<void>;
  /** Refresh job list from the backend */
  fetchJobs: () => Promise<void>;
  /** Clear all jobs both locally and on the backend */
  clearJobs: () => Promise<void>;
  /** Internal: update the active (Running) job from latest backend data */
  pollActiveJob: () => Promise<void>;
};

export const useScraperStore = create<ScraperState>()(
  persist(
    (set, get) => ({
      currentJob: null,
      jobStatus: "Idle",
      progress: 0,
      jobs: [],
      loading: false,
      error: null,

      startScrape: async (payload) => {
        const safePayload: StartScrapePayload = {
          ...payload,
          keyword: sanitizeInput(payload.keyword),
          industry: sanitizeInput(payload.industry),
          location: sanitizeInput(payload.location),
        };

        set({ loading: true, error: null });
        try {
          const job = await startScrape(safePayload);
          set((state) => ({
            currentJob: job,
            jobStatus: job.status,
            progress: job.progress,
            jobs: [job, ...state.jobs.filter((j) => j.id !== job.id)],
            loading: false,
          }));
        } catch (error) {
          set({
            loading: false,
            error: error instanceof Error ? error.message : "Unable to start scrape job.",
          });
        }
      },

      uploadParams: async (file, sources) => {
        set({ loading: true, error: null });
        try {
          const { job } = await apiUploadParams(file, sources);
          set((state) => ({
            currentJob: job,
            jobStatus: job.status,
            progress: job.progress,
            jobs: [job, ...state.jobs.filter((j) => j.id !== job.id)],
            loading: false,
          }));
        } catch (error) {
          set({
            loading: false,
            error: error instanceof Error ? error.message : "Unable to upload parameters.",
          });
        }
      },

      fetchJobs: async () => {
        set({ loading: true, error: null });
        try {
          const jobs = await getJobs();
          const currentJob = jobs[0] ?? null;
          set({
            jobs,
            currentJob,
            jobStatus: currentJob?.status ?? "Idle",
            progress: currentJob?.progress ?? 0,
            loading: false,
          });
        } catch (error) {
          set({
            jobs: [],
            currentJob: null,
            jobStatus: "Idle",
            progress: 0,
            loading: false,
            error: error instanceof Error ? error.message : "Unable to load jobs.",
          });
        }
      },

      clearJobs: async () => {
        try {
          await apiClearJobs();
          set({
            jobs: [],
            currentJob: null,
            jobStatus: "Idle",
            progress: 0,
            error: null,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : "Unable to clear jobs.",
          });
        }
      },

      /**
       * Polls only if there is an active Running job to avoid unnecessary requests.
       * Called on an interval by the UI layer when needed.
       */
      pollActiveJob: async () => {
        const { currentJob } = get();
        if (!currentJob || currentJob.status !== "Running") return;
        try {
          const jobs = await getJobs();
          const updated = jobs.find((j) => j.id === currentJob.id) ?? jobs[0] ?? null;
          set({
            jobs,
            currentJob: updated,
            jobStatus: updated?.status ?? "Idle",
            progress: updated?.progress ?? 0,
          });
        } catch {
          // silent – don't spam error state during polling
        }
      },
    }),
    {
      name: "dh-scraper-store-v2",
      partialize: (state) => ({
        currentJob: state.currentJob,
        jobStatus: state.jobStatus,
        progress: state.progress,
        jobs: state.jobs,
      }),
    },
  ),
);
