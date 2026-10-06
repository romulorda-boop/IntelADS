export type Network = "meta" | "google" | "tiktok" | "kwai";
export type TargetOS = "android" | "ios" | "desktop";
export type Category = "games" | "ecommerce" | "apps" | "finance" | "infoproducts";
export type Badge = "Winner" | "Scaling" | "Testing";

export type SyncStatus = "mock" | "syncing" | "synced" | "error";

export interface SyncedApp {
  id: string;
  advertiser_id: string | null;
  platform: "android" | "ios";
  store_app_id: string;
  title: string;
  downloads_count: string | null;
  rating: number | null;
  icon_url: string | null;
  category: string | null;
  sync_status: SyncStatus;
  last_synced_at: string;
}

export interface Ad {
  id: string;
  title: string;
  caption: string;
  media_type: "video" | "image" | "carrousel";
  media_url: string;
  thumbnail_url: string;
  source_network: Network;
  category: string;
  target_os: TargetOS[];
  longevity_score: number;
  badge: Badge;
  active_days: number;
  first_seen_at?: string;
  is_active: boolean;
  variations_count: number;
  destination_url: string;
  advertiser: { id: string; name: string } | null;
  app: {
    title: string;
    platform: "android" | "ios";
    downloads_count: string | null;
    rating: number | null;
    icon_url: string | null;
    id: string;
    store_app_id: string;
    sync_status: SyncStatus;
    last_synced_at: string | null;
  } | null;
}

export interface SearchPayload {
  query?: string;
  category?: string;
  target_os?: TargetOS[];
  networks?: Network[];
  min_longevity_score?: number;
  max_longevity_score?: number;
  is_active_only?: boolean;
  sort_by?: "longevity_score_desc" | "first_seen_desc" | "active_days_desc";
  page?: number;
  limit?: number;
  advertiser_id?: string;
}

export interface SearchResponse {
  total: number;
  page: number;
  total_pages: number;
  results: Ad[];
}

export interface AdvertiserProfile {
  advertiser_id: string;
  name: string;
  domain: string | null;
  total_ads_captured: number;
  active_ads: number;
  inactive_ads: number;
  os_distribution: Record<TargetOS, number>;
  network_distribution: Record<Network, number>;
  apps_linked: Array<{
    id: string;
    title: string;
    store_id: string;
    downloads: string | null;
    rating: number | null;
    icon_url: string | null;
    category: string | null;
    platform: "android" | "ios";
    sync_status: SyncStatus;
    last_synced_at: string | null;
  }>;
}
