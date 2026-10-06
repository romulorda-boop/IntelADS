import type { AdvertiserProfile, SearchPayload, SearchResponse, SyncedApp } from "@/lib/types";

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = `A API respondeu com status ${response.status}.`;
    try {
      const body = await response.json();
      const detail = body?.detail;
      message = typeof detail === "string" ? detail : detail?.message ?? message;
    } catch {
      // Keep the concise HTTP fallback when the response is not JSON.
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export async function searchAds(payload: SearchPayload): Promise<SearchResponse> {
  const response = await fetch("/api/v1/ads/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    cache: "no-store",
  });
  return readJson<SearchResponse>(response);
}

export async function getAdvertiserProfile(id: string): Promise<AdvertiserProfile> {
  const response = await fetch(`/api/v1/advertisers/${encodeURIComponent(id)}`, {
    cache: "no-store",
  });
  return readJson<AdvertiserProfile>(response);
}

export async function syncApp(appId: string): Promise<SyncedApp> {
  const response = await fetch(`/api/v1/apps/sync/${encodeURIComponent(appId)}`, {
    method: "POST",
    cache: "no-store",
  });
  return readJson<SyncedApp>(response);
}
