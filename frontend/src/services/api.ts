import axios, { AxiosError } from "axios";

/**
 * In development the Next.js config rewrites /api/* → backend, so we call
 * relative paths and avoid CORS entirely.
 *
 * In production set NEXT_PUBLIC_API_BASE_URL to the actual backend host
 * (e.g. https://api.example.com) and calls will go there directly.
 */
const RAW_BASE = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || "";

/**
 * If the env var looks like the same host as the frontend (localhost:3000)
 * or is empty, use relative URLs so the Next.js proxy handles rewrites.
 * Otherwise use the explicit URL (production).
 */
const isRelative =
  !RAW_BASE ||
  RAW_BASE === "http://localhost:3000" ||
  RAW_BASE === "http://127.0.0.1:3000";

export const api = axios.create({
  baseURL: isRelative ? "" : RAW_BASE,
  /**
   * 30 s default. Scraping jobs start async so the POST returns immediately;
   * only file uploads need the extended 60 s timeout set per-call.
   */
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
});

/** Normalise FastAPI detail messages and network errors for the UI stores */
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const detail = error.response?.data?.detail;
    if (detail) {
      return Promise.reject(new Error(detail));
    }
    if (error.code === "ECONNABORTED") {
      return Promise.reject(
        new Error("Request timed out – is the backend running?"),
      );
    }
    if (!error.response) {
      return Promise.reject(
        new Error(
          `Cannot reach the backend at ${RAW_BASE || "localhost:8000"}. Make sure it is running.`,
        ),
      );
    }
    return Promise.reject(error);
  },
);
