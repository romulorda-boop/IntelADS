"use client";

import Link from "next/link";
import { ArrowDownToLine, ArrowUpRight, Clock3, ExternalLink, Layers2, Play, Star } from "lucide-react";
import { useRef, useState } from "react";
import { AppSyncButton } from "@/components/app-sync-controls";
import { LongevityMeter } from "@/components/longevity-meter";
import { labelAdCategory, labelStoreCategory } from "@/lib/category-labels";
import type { Ad } from "@/lib/types";

const networkNames: Record<string, string> = { meta: "Meta", tiktok: "TikTok", google: "Google", kwai: "Kwai" };
const osNames: Record<string, string> = { android: "Android", ios: "iOS", desktop: "Desktop" };
export function AdCard({ ad, onAppSynced, onOpenDetails }: { ad: Ad; onAppSynced?: () => void; onOpenDetails?: () => void }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);
  const startDate = ad.first_seen_at
    ? new Date(ad.first_seen_at).toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" })
    : null;
  const appMetricLabel = ad.app?.platform === "android" && ad.app.sync_status === "synced" ? "INSTALAÇÕES" : "DOWNLOADS";
  const storeCategory = labelStoreCategory(ad.app?.category);

  const preview = async () => {
    const video = videoRef.current;
    if (!video) return;
    try {
      if (video.paused) { await video.play(); setPlaying(true); }
      else { video.pause(); setPlaying(false); }
    } catch { setPlaying(false); }
  };
  const pausePreview = () => {
    if (!videoRef.current) return;
    videoRef.current.pause();
    videoRef.current.currentTime = 0;
    setPlaying(false);
  };

  return (
    <article className="ad-card">
      <div className="ad-card-top">
        <div className="network-label"><span className={`network-dot network-${ad.source_network}`} /><span>{networkNames[ad.source_network] ?? ad.source_network}</span></div>
        <span className={`score-badge badge-${ad.badge.toLowerCase()}`}><span className="badge-spark">{ad.badge === "Winner" ? "✦" : ad.badge === "Scaling" ? "↗" : "·"}</span>{ad.badge === "Scaling" ? "Em escala" : ad.badge === "Testing" ? "Em teste" : "Winner"}<b>{ad.longevity_score}</b></span>
        <div className="os-label" title={ad.target_os.map((os) => osNames[os]).join(" + ")}><span className="os-glyph">▣</span>{ad.target_os.map((os) => osNames[os]).join(" + ")}</div>
      </div>
      <div className="ad-card-score"><LongevityMeter score={ad.longevity_score} compact /></div>

      <div className="ad-media" onMouseEnter={() => void preview()} onMouseLeave={pausePreview}>
        <video ref={videoRef} src={ad.media_url} poster={ad.thumbnail_url} muted loop playsInline preload="none" aria-label={`Prévia do anúncio: ${ad.title}`} />
        <div className="media-shade" />
        <button className={`media-play${playing ? " is-playing" : ""}`} onClick={() => void preview()} aria-label={playing ? "Pausar prévia" : "Reproduzir prévia"}><Play size={15} fill="currentColor" /></button>
        <div className="media-caption"><span>PRÉVIA DO CRIATIVO</span><span>00:04</span></div>
        <span className="media-category">{labelAdCategory(ad.category)}</span>
      </div>

      <div className="ad-card-content">
        <div className="ad-title-row"><div><div className="field-label">{labelAdCategory(ad.category)}</div><h3>{ad.title}</h3></div>{ad.is_active ? <span className="active-pill"><i />Ativo</span> : <span className="inactive-pill">Encerrado</span>}</div>

        {ad.app ? (
          <div className="app-insight">
            {ad.app.icon_url ? <img src={ad.app.icon_url} alt="" className="app-icon" /> : <div className="app-icon app-icon-fallback">A</div>}
            <div className="app-identity"><div className="app-name"><span>APP VINCULADO</span><strong>{ad.app.title}</strong>{storeCategory && storeCategory !== labelAdCategory(ad.category) && <span>{storeCategory}</span>}</div><AppSyncButton appId={ad.app.id} status={ad.app.sync_status} onSynced={onAppSynced} compact /></div>
            <div className="app-metric"><span>{appMetricLabel}</span><strong>{ad.app.downloads_count ?? (ad.app.platform === "ios" ? "Não divulgado" : "—")}</strong></div>
            <div className="app-rating"><Star size={13} fill="currentColor" /><strong>{ad.app.rating?.toFixed(1) ?? "—"}</strong></div>
          </div>
        ) : (
          <div className="product-insight"><span className="product-symbol">↗</span><span>Oferta de e-commerce</span><strong>Destino externo</strong></div>
        )}

        <div className="advertiser-line"><span className="advertiser-avatar">{ad.advertiser?.name.slice(0, 1) ?? "A"}</span><span className="advertiser-copy"><small>ANUNCIANTE</small><strong>{ad.advertiser?.name ?? "Anunciante não identificado"}</strong></span>{ad.advertiser && <Link href={`/advertisers/${ad.advertiser.id}`} className="profile-link">Ver perfil <ArrowUpRight size={13} /></Link>}</div>
        <p className="ad-caption"><span>“</span>{ad.caption}</p>
        <div className="ad-meta-row"><span><Clock3 size={14} />Ativo há {ad.active_days} dias{startDate ? ` · Desde ${startDate}` : ""}</span><button className="variation-action" type="button" onClick={onOpenDetails} aria-label={`Abrir detalhes e ${ad.variations_count} variações encontradas`}><Layers2 size={14} />{ad.variations_count} {ad.variations_count === 1 ? "variação" : "variações"}<span>Ver detalhes</span></button></div>
      </div>

      <div className="ad-card-actions"><a href={ad.media_url} download className="action-primary"><ArrowDownToLine size={15} />Baixar vídeo MP4</a><a href={ad.destination_url} target="_blank" rel="noreferrer" className="action-secondary">Ver na biblioteca<ExternalLink size={14} /></a></div>
    </article>
  );
}
