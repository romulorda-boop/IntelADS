"use client";

import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { syncApp } from "@/lib/api";
import type { SyncStatus } from "@/lib/types";

const STATUS_LABELS: Record<SyncStatus, string> = {
  mock: "Dados mock",
  syncing: "Sincronizando",
  synced: "Sincronizado",
  error: "Falha na sync",
};

export function SyncStatusBadge({ status }: { status: SyncStatus }) {
  return <span className={`sync-status-badge sync-status-${status}`} role="status">{STATUS_LABELS[status]}</span>;
}

export function AppSyncButton({
  appId,
  status,
  onSynced,
  compact = false,
}: {
  appId: string;
  status: SyncStatus;
  onSynced?: () => void;
  compact?: boolean;
}) {
  const [busy, setBusy] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [failed, setFailed] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setConfirmed(status === "synced");
    setFailed(status === "error");
  }, [status]);

  const handleSync = async () => {
    setBusy(true);
    setFailed(false);
    setError("");
    try {
      await syncApp(appId);
      setConfirmed(true);
      onSynced?.();
    } catch (reason) {
      setFailed(true);
      setError(reason instanceof Error ? reason.message : "Não foi possível sincronizar este app.");
    } finally {
      setBusy(false);
    }
  };

  const visibleStatus: SyncStatus = busy ? "syncing" : failed ? "error" : confirmed ? "synced" : status;
  return (
    <div className={`app-sync-control${compact ? " compact" : ""}`}>
      <SyncStatusBadge status={visibleStatus} />
      <button
        type="button"
        className="app-sync-button"
        onClick={() => void handleSync()}
        disabled={busy}
        aria-label={busy ? "Sincronizando dados da loja" : "Sincronizar dados da loja"}
        title="Atualizar metadados da loja pública"
      >
        <RefreshCw size={12} className={busy ? "sync-rotate" : ""} />
        <span>{busy ? "Sincronizando…" : compact ? "Atualizar" : "Sincronizar"}</span>
      </button>
      {error && <small className="app-sync-error" role="alert">{error}</small>}
    </div>
  );
}
