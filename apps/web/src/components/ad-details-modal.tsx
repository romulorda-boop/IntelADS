"use client";

import Link from "next/link";
import { ArrowDownToLine, ArrowUpRight, ExternalLink, Layers2, LoaderCircle, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { LongevityMeter } from "@/components/longevity-meter";
import { getAdDetails } from "@/lib/api";
import { labelAdCategory, labelStoreCategory } from "@/lib/category-labels";
import type { AdDetails } from "@/lib/types";

const networkNames: Record<string, string> = { meta: "Meta", tiktok: "TikTok", google: "Google", kwai: "Kwai" };
const osNames: Record<string, string> = { android: "Android", ios: "iOS", desktop: "Desktop" };

export function AdDetailsModal({ adId, onClose }: { adId: string; onClose: () => void }) {
  const [selectedAdId, setSelectedAdId] = useState(adId);
  const [ad, setAd] = useState<AdDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryToken, setRetryToken] = useState(0);
  const dialogRef = useRef<HTMLElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const openerRef = useRef<HTMLElement | null>(null);
  const onCloseRef = useRef(onClose);
  const appCategory = labelStoreCategory(ad?.app?.category);
  onCloseRef.current = onClose;

  useEffect(() => setSelectedAdId(adId), [adId]);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getAdDetails(selectedAdId)
      .then((result) => { if (!cancelled) setAd(result); })
      .catch((cause: unknown) => { if (!cancelled) setError(cause instanceof Error ? cause.message : "Falha ao carregar detalhes."); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [selectedAdId, retryToken]);

  useEffect(() => {
    openerRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const oldOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const focusFrame = window.requestAnimationFrame(() => closeButtonRef.current?.focus());
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); onCloseRef.current(); return; }
      if (event.key !== "Tab") return;
      const dialog = dialogRef.current;
      if (!dialog) return;
      const focusable = Array.from(dialog.querySelectorAll<HTMLElement>(
        'button:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])',
      ));
      if (!focusable.length) { event.preventDefault(); dialog.focus(); return; }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && (document.activeElement === first || !dialog.contains(document.activeElement))) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && (document.activeElement === last || !dialog.contains(document.activeElement))) {
        event.preventDefault(); first.focus();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      window.cancelAnimationFrame(focusFrame);
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = oldOverflow;
      window.requestAnimationFrame(() => openerRef.current?.focus());
    };
  }, []);

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <section ref={dialogRef} className="ad-detail-modal" role="dialog" aria-modal="true" aria-labelledby="ad-detail-title" tabIndex={-1}>
        <header className="ad-detail-header">
          <div><span className="field-label">AD INTELLIGENCE / ANÁLISE</span><h2 id="ad-detail-title">Detalhes do anúncio</h2></div>
          <button ref={closeButtonRef} type="button" className="modal-close" onClick={onClose} aria-label="Fechar detalhes"><X size={18} /></button>
        </header>
        {loading ? (
          <div className="modal-state"><LoaderCircle size={22} className="spin" /><span>Carregando análise…</span></div>
        ) : error ? (
          <div className="modal-state modal-error" role="alert"><p>{error}</p><button type="button" className="action-secondary" onClick={() => setRetryToken((value) => value + 1)}>Tentar novamente</button></div>
        ) : ad ? (
          <div className="ad-detail-body">
            <div className="detail-hero">
              <div className="detail-thumbnail"><img src={ad.thumbnail_url} alt="" /><span>{networkNames[ad.source_network] ?? ad.source_network}</span></div>
              <div className="detail-summary">
                <div className="detail-tags"><span className={`score-badge badge-${ad.badge.toLowerCase()}`}>{ad.badge === "Scaling" ? "Em escala" : ad.badge === "Testing" ? "Em teste" : "Winner"}<b>{ad.longevity_score}</b></span><span className="media-category static-category">{labelAdCategory(ad.category)}</span>{appCategory && appCategory !== labelAdCategory(ad.category) && <span className="media-category static-category">{appCategory}</span>}</div>
                <h3>{ad.title}</h3><p>{ad.caption}</p>
                {ad.advertiser && <Link href={`/advertisers/${ad.advertiser.id}`} onClick={onClose} className="profile-link">{ad.advertiser.name}<ArrowUpRight size={13} /></Link>}
              </div>
            </div>
            <section className="detail-score-section" aria-label="Pontuação de longevidade">
              <LongevityMeter score={ad.longevity_score} />
              <div className="score-breakdown">
                <div><span>Tempo ativo</span><strong>{ad.score_breakdown.active_days} dias</strong><small>+{ad.score_breakdown.active_points} pts</small></div>
                <div><span>Aparições · 30 dias</span><strong>{ad.score_breakdown.appearances_last_30_days}</strong><small>+{ad.score_breakdown.appearance_points} pts</small></div>
                <div><span>Variações detectadas</span><strong>{ad.score_breakdown.variations_count}</strong><small>+{ad.score_breakdown.variation_points} pts</small></div>
              </div>
            </section>
            {ad.app && <section className="detail-app-panel"><div className="field-label">DADOS DA LOJA</div><div className="detail-app-row"><strong>{ad.app.title}</strong><span>{ad.app.downloads_count ?? (ad.app.platform === "ios" ? "Downloads não divulgados" : "—")}</span><span>{ad.app.rating?.toFixed(1) ?? "—"} ★</span></div></section>}
            <section className="variants-section" aria-labelledby="variants-title">
              <div className="variants-heading"><div><span className="field-label">MATCH VISUAL / HAMMING ≤ 10</span><h3 id="variants-title"><Layers2 size={17} />Variações Encontradas</h3></div><span className="variant-count">{ad.variants.length} {ad.variants.length === 1 ? "anúncio" : "anúncios"}</span></div>
              {ad.variants.length ? (
                <div className="variant-list">{ad.variants.map((variant) => (
                  <button type="button" className="variant-row" key={variant.id} onClick={() => setSelectedAdId(variant.id)} aria-label={`Abrir variação ${variant.title}`}>
                    <img src={variant.thumbnail_url} alt="" /><span className="variant-copy"><strong>{variant.title}</strong><small>{networkNames[variant.source_network] ?? variant.source_network}</small></span><span className="hamming-chip">H {variant.hamming_distance}/64</span><ArrowUpRight size={15} />
                  </button>
                ))}</div>
              ) : <p className="empty-variants">Nenhuma variação visual foi encontrada dentro do limiar atual.</p>}
            </section>
            <div className="detail-footer"><span>{ad.target_os.map((os) => osNames[os] ?? os).join(" · ")} · {ad.active_days} dias ativo</span><div><a href={ad.media_url} download className="action-primary"><ArrowDownToLine size={14} />Baixar</a><a href={ad.destination_url} target="_blank" rel="noreferrer" className="action-secondary">Abrir anúncio<ExternalLink size={13} /></a></div></div>
          </div>
        ) : null}
      </section>
    </div>
  );
}
