import type { AdvertiserProfile, SearchPayload, SearchResponse } from "@/lib/types";

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(detail || `A API respondeu com status ${response.status}.`);
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
