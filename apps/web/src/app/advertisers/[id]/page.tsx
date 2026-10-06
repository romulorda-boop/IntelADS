"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowLeft, ArrowUpRight, Building2, Globe2, Layers3 } from "lucide-react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { AdCard } from "@/components/ad-card";
import { AppSyncButton } from "@/components/app-sync-controls";
import { getAdvertiserProfile, searchAds } from "@/lib/api";
import type { Ad, AdvertiserProfile } from "@/lib/types";

type ChartDatum = { name: string; value: number; color: string };
const OS_COLORS: Record<string, string> = { android: "#c8f169", ios: "#8ab6e9", desktop: "#9d8af2" };
const NETWORK_COLORS: Record<string, string> = { meta: "#6ebbf2", google: "#c8f169", tiktok: "#f18b77", kwai: "#9d8af2" };
const NETWORK_LABELS: Record<string, string> = { meta: "Meta", google: "Google", tiktok: "TikTok", kwai: "Kwai" };
const OS_LABELS: Record<string, string> = { android: "Android", ios: "iOS", desktop: "Desktop / PC" };

export default function AdvertiserPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [profile, setProfile] = useState<AdvertiserProfile | null>(null);
  const [ads, setAds] = useState<Ad[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshToken, setRefreshToken] = useState(0);

  useEffect(() => {
    if (!id) return;
    let alive = true;
    setLoading(true);
    Promise.all([
      getAdvertiserProfile(id),
      searchAds({ advertiser_id: id, is_active_only: false, page: 1, limit: 20, sort_by: "longevity_score_desc" }),
    ]).then(([advertiser, result]) => {
      if (!alive) return;
      setProfile(advertiser);
      setAds(result.results);
      setError("");
    }).catch(() => {
      if (alive) setError("Não foi possível carregar o perfil deste anunciante.");
    }).finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [id, refreshToken]);

  if (loading) return <div className="page-wrap"><div className="topbar"><div className="breadcrumb">Inteligência / <b>Perfil do anunciante</b></div></div><div className="profile-loading">Carregando dados do anunciante…</div></div>;
  if (error || !profile) return <div className="page-wrap"><div className="topbar"><div className="breadcrumb">Inteligência / <b>Perfil do anunciante</b></div></div><div className="not-found"><h2>Perfil indisponível</h2><p>{error || "Anunciante não encontrado."}</p><Link href="/" className="back-link"><ArrowLeft size={14} />Voltar à biblioteca</Link></div></div>;

  const osData: ChartDatum[] = Object.entries(profile.os_distribution).map(([key, value]) => ({ name: OS_LABELS[key] ?? key, value, color: OS_COLORS[key] ?? "#8996a4" }));
  const networkData: ChartDatum[] = Object.entries(profile.network_distribution).map(([key, value]) => ({ name: NETWORK_LABELS[key] ?? key, value, color: NETWORK_COLORS[key] ?? "#8492a1" }));
  const activeRate = profile.total_ads_captured ? Math.round((profile.active_ads / profile.total_ads_captured) * 100) : 0;

  return (
    <div className="page-wrap page-profile">
      <div className="topbar"><div className="breadcrumb">Inteligência <span> / </span><b>Perfil do anunciante</b></div><div className="topbar-right"><div className="sync-indicator"><i />Apps sincronizáveis sob demanda</div><div className="user-chip">AD</div></div></div>
      <Link href="/" className="back-link"><ArrowLeft size={14} />Voltar para a biblioteca</Link>
      <header className="page-heading"><div><div className="eyebrow">ECOSSISTEMA DE MÍDIA</div><h1>Perfil do anunciante</h1><p>Distribuição de criativos e presença por canal.</p></div></header>

      <section className="profile-hero">
        <div className="profile-avatar">{profile.name.slice(0, 1).toUpperCase()}</div>
        <div className="profile-identity"><h1>{profile.name}</h1><p>Análise de anúncios capturados no ambiente demonstrativo</p></div>
        {profile.domain && <div className="profile-domain"><Globe2 size={14} />{profile.domain}<ArrowUpRight size={12} /></div>}
      </section>

      <section className="profile-kpis" aria-label="Resumo do anunciante">
        <div className="profile-kpi"><span>Anúncios capturados</span><strong>{profile.total_ads_captured}</strong><small>ativos e inativos no mock</small></div>
        <div className="profile-kpi"><span>Anúncios ativos</span><strong>{profile.active_ads}</strong><small>{activeRate}% do inventário</small></div>
        <div className="profile-kpi"><span>Apps vinculados</span><strong>{profile.apps_linked.length}</strong><small>mock e dados de loja</small></div>
      </section>

      <section className="profile-charts">
        <ChartCard title="Distribuição por sistema operacional" subtitle="Participação dos anúncios por plataforma" type="Pizza" data={osData}>
          <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={osData} dataKey="value" nameKey="name" outerRadius={65} stroke="#11171f" strokeWidth={3}>{osData.map((entry, index) => <Cell key={`os-${index}`} fill={entry.color} />)}</Pie><Tooltip contentStyle={{ background: "#18212b", border: "1px solid #34414e", borderRadius: 7, color: "#e8edf0", fontSize: 10 }} formatter={(value) => [`${value}%`, "Participação"]} /></PieChart></ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Distribuição por rede" subtitle="Mix de presença entre redes de anúncios" type="Rosca" data={networkData}>
          <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={networkData} dataKey="value" nameKey="name" innerRadius={43} outerRadius={66} paddingAngle={3} stroke="#11171f" strokeWidth={2}>{networkData.map((entry, index) => <Cell key={`net-${index}`} fill={entry.color} />)}</Pie><Tooltip contentStyle={{ background: "#18212b", border: "1px solid #34414e", borderRadius: 7, color: "#e8edf0", fontSize: 10 }} formatter={(value) => [`${value}%`, "Participação"]} /></PieChart></ResponsiveContainer>
        </ChartCard>
      </section>

      <section className="apps-card">
        <div className="section-title"><h2>Aplicativos vinculados</h2><span>{profile.apps_linked.length} aplicativos</span></div>
        {profile.apps_linked.length ? <div className="apps-list">{profile.apps_linked.map((app) => <div className="linked-app" key={app.id}><div className="linked-app-icon">{app.icon_url ? <img src={app.icon_url} alt="" /> : <Building2 size={15} />}</div><div className="linked-app-info"><strong>{app.title}</strong><small>{app.platform === "android" ? "Google Play" : "App Store"} · {app.store_id}</small></div><div className="linked-app-metrics"><div className="linked-app-downloads"><small>{app.platform === "android" && app.sync_status === "synced" ? "INSTALAÇÕES" : "DOWNLOADS"}</small>{app.downloads ?? (app.platform === "ios" ? "Não divulgado" : "—")}</div><div className="linked-app-rating"><small>RATING</small>{app.rating?.toFixed(1) ?? "—"}</div></div><AppSyncButton appId={app.id} status={app.sync_status} onSynced={() => setRefreshToken((value) => value + 1)} compact /></div>)}</div> : <div className="empty-state"><p>Nenhum aplicativo vinculado.</p></div>}
      </section>

      <section className="profile-feed">
        <div className="section-title"><h2>Criativos do anunciante</h2><span><Layers3 size={12} style={{ verticalAlign: -2, marginRight: 4 }} />{ads.length} anúncios</span></div>
        {ads.length ? <div className="feed-grid">{ads.map((ad) => <AdCard key={ad.id} ad={ad} onAppSynced={() => setRefreshToken((value) => value + 1)} />)}</div> : <div className="empty-state"><p>Nenhum criativo relacionado neste mock.</p></div>}
      </section>
    </div>
  );
}

function ChartCard({ title, subtitle, type, data, children }: { title: string; subtitle: string; type: string; data: ChartDatum[]; children: React.ReactNode }) {
  return (
    <div className="chart-card">
      <div className="chart-heading"><div><h2>{title}</h2><p>{subtitle}</p></div><span className="chart-type">{type}</span></div>
      <div className="chart-body">
        <div className="chart-wrap">{children}</div>
        <div className="chart-legend">{data.map((item) => <div className="legend-row" key={item.name}><i className="legend-dot" style={{ background: item.color }} /><span>{item.name}</span><strong>{item.value.toFixed(1)}%</strong></div>)}</div>
      </div>
    </div>
  );
}
