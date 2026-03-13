"use client";

import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useSettingsStore } from "@/store/settingsStore";
import { api } from "@/services/api";
import { CheckCircle2, AlertTriangle, Loader2 } from "lucide-react";

type ConnectionStatus = "idle" | "checking" | "ok" | "error";

export default function SettingsPage() {
  const { settings, updateSettings } = useSettingsStore();
  const connectionLabel = useMemo(() => settings.apiBaseUrl || "http://localhost:8000", [settings.apiBaseUrl]);

  const [connStatus, setConnStatus] = useState<ConnectionStatus>("idle");
  const [connMessage, setConnMessage] = useState("");

  const testConnection = async () => {
    setConnStatus("checking");
    setConnMessage("");
    try {
      const { data } = await api.get<{ status: string; jobs: number; companies: number }>("/api/health");
      setConnStatus("ok");
      setConnMessage(`Backend online · ${data.jobs} jobs · ${data.companies} companies`);
    } catch (err) {
      setConnStatus("error");
      setConnMessage(err instanceof Error ? err.message : "Connection failed");
    }
  };

  return (
    <div className="space-y-8">
      <section>
        <p className="text-sm uppercase tracking-[0.24em] text-[var(--muted-foreground)]">Configuration</p>
        <h2 className="mt-2 text-4xl font-semibold text-white">Platform and integration settings</h2>
        <p className="mt-3 max-w-3xl text-base text-[var(--muted-foreground)]">
          Configure Sheets sync, API connectivity, rate limits, and proxy routing for your scraping environment.
        </p>
      </section>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card className="space-y-5">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-[var(--muted-foreground)]">Google Sheets</p>
            <h3 className="mt-2 text-2xl font-semibold text-white">Connection</h3>
          </div>
          <Input
            placeholder="Spreadsheet name"
            value={settings.googleSheetName}
            onChange={(event) => updateSettings({ googleSheetName: event.target.value })}
          />
          <Input
            placeholder="Worksheet name"
            value={settings.googleWorksheetName}
            onChange={(event) => updateSettings({ googleWorksheetName: event.target.value })}
          />
          <p className="text-sm text-[var(--muted-foreground)]">
            These values are persisted locally and can be mapped to the backend configuration layer later.
          </p>
          <Button type="button">Saved Locally</Button>
        </Card>

        <Card className="space-y-5">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-[var(--muted-foreground)]">API and controls</p>
            <h3 className="mt-2 text-2xl font-semibold text-white">Runtime parameters</h3>
          </div>

          {/* Connection status badge */}
          <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-[var(--muted-foreground)]">
            <div className="flex items-center justify-between gap-3">
              <span>
                Active backend API: <span className="font-semibold text-white">{connectionLabel}</span>
              </span>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => void testConnection()}
                disabled={connStatus === "checking"}
                className="shrink-0 gap-1.5 text-xs"
              >
                {connStatus === "checking" ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : connStatus === "ok" ? (
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                ) : connStatus === "error" ? (
                  <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />
                ) : null}
                Test Connection
              </Button>
            </div>
            {connMessage && (
              <p
                className={`mt-2 text-xs ${connStatus === "ok" ? "text-emerald-400" : "text-rose-400"}`}
              >
                {connMessage}
              </p>
            )}
          </div>

          <Input
            placeholder="Backend API URL"
            value={settings.apiBaseUrl}
            onChange={(event) => updateSettings({ apiBaseUrl: event.target.value })}
          />
          <Input
            placeholder="Requests per minute"
            value={settings.requestsPerMinute}
            onChange={(event) => updateSettings({ requestsPerMinute: event.target.value })}
          />
          <Input
            placeholder="Proxy endpoint"
            value={settings.proxyUrl}
            onChange={(event) => updateSettings({ proxyUrl: event.target.value })}
          />
          <Input
            placeholder="API key"
            type="password"
            value={settings.apiKey}
            onChange={(event) => updateSettings({ apiKey: event.target.value })}
          />
          <p className="text-sm text-[var(--muted-foreground)]">
            Set the backend URL to your FastAPI instance. The default local stack uses port 8000.
          </p>
          <Button type="button">Saved Locally</Button>
        </Card>
      </div>
    </div>
  );
}
