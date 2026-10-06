"use client";

import { useEffect, useState } from "react";
import { Activity, ArrowRight, BarChart3, Database, Layers3, Search, SlidersHorizontal, Sparkles, X } from "lucide-react";
import { AdCard } from "@/components/ad-card";
import { searchAds } from "@/lib/api";
import type { Ad, Category, Network, SearchResponse, TargetOS } from "@/lib/types";

const NETWORKS: Network[] = ["meta", "google", "tiktok", "kwai"];
const OS_OPTIONS: TargetOS[] = ["android", "ios", "desktop"];
const NETWORK_LABELS: Record<Network, string> = { meta: "Meta", google: "Google", tiktok: "TikTok", kwai: "Kwai" };
const OS_LABELS: Record<TargetOS, string> = { android: "Android", ios: "iOS", desktop: "Desktop" };
type ScoreBand = "all" | "winner" | "scaling" | "testing";

export default function HomePage() {
  const [data, setData] = useState<SearchResponse | null>(null);
  const [draftQuery, setDraftQuery] = useState("");
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<Category | "">("");
  const [selectedOS, setSelectedOS] = useState<TargetOS[]>(["android", "ios"]);
  const [selectedNetworks, setSelectedNetworks] = useState<Network[]>(NETWORKS);
  const [scoreBand, setScoreBand] = useState<ScoreBand>("all");
  const [activeOnly, setActiveOnly] = useState(true);
  const [sortBy, setSortBy] = useState<"longevity_score_desc" | "first_seen_desc" | "active_days_desc">("longevity_score_desc");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshToken, setRefreshToken] = useState(0);

  useEffect(() => {
    let alive = true;
    const timer = window.setTimeout(async () => {
      setLoading(true);
      setError("");
      const scoreArgs = scoreBand === "winner"
        ? { min_longevity_score: 80 }
        : scoreBand === "scaling"
          ? { min_longevity_score: 40, max_longevity_score: 79 }
          : scoreBand === "testing"
            ? { max_longevity_score: 39 }
            : {};
      try {
        const result = await searchAds({
          query: query || undefined,
          category: category || undefined,
          target_os: selectedOS,
          networks: selectedNetworks,
          is_active_only: activeOnly,
          sort_by: sortBy,
          page: 1,
          limit: 20,
          ...scoreArgs,
        });
        if (alive) setData(result);
      } catch {
        if (alive) setError("Não foi possível conectar à API local. Verifique se o backend FastAPI e o PostgreSQL estão ativos.");
      } finally {
        if (alive) setLoading(false);
      }
    }, 80);
    return () => { alive = false; window.clearTimeout(timer); };
  }, [query, category, selectedOS, selectedNetworks, scoreBand, activeOnly, sortBy, refreshToken]);

  const toggleOS = (os: TargetOS) => setSelectedOS((current) => current.includes(os) ? current.filter((item) => item !== os) : [...current, os]);
  const toggleNetwork = (network: Network) => setSelectedNetworks((current) => current.includes(network) ? current.filter((item) => item !== network) : [...current, network]);
  const clearFilters = () => {
    setDraftQuery(""); setQuery(""); setCategory(""); setSelectedOS(["android", "ios"]);
    setSelectedNetworks(NETWORKS); setScoreBand("all"); setActiveOnly(true); setSortBy("longevity_score_desc");
  };

  const ads: Ad[] = data?.results ?? [];
  const winners = ads.filter((ad) => ad.badge === "Winner").length;
  const scaling = ads.filter((ad) => ad.badge === "Scaling").length;

  return (
    <div className="page-wrap">
      <div className="topbar">
        <div className="breadcrumb">Inteligência <span> / </span><b>Biblioteca de anúncios</b></div>
        <div className="topbar-right"><div className="sync-indicator"><i />Apps sincronizáveis sob demanda</div><div className="user-chip">AD</div></div>
      </div>

      <header className="page-heading">
        <div><div className="eyebrow">AD INTELLIGENCE / CRIATIVOS</div><h1>Biblioteca de anúncios</h1><p>Encontre criativos persistentes, sinais de escala e ideias para testar.</p></div>
        <div className="header-actions"><button className="button-quiet" type="button"><Database size={14} />Dados simulados</button><button className="button-quiet" type="button"><SlidersHorizontal size={14} />Filtros ativos</button></div>
      </header>

      <section className="signal-strip" aria-label="Resumo do recorte atual">
        <div className="signal-item"><span className="signal-icon"><Layers2Icon /></span><span className="signal-copy"><span>Anúncios no recorte</span><strong>{loading ? "—" : data?.total ?? 0}<small>mock</small></strong></span></div>
        <div className="signal-item"><span className="signal-icon"><Sparkles size={16} /></span><span className="signal-copy"><span>Winners nesta página</span><strong>{loading ? "—" : winners}<small>score ≥ 80</small></strong></span></div>
        <div className="signal-item"><span className="signal-icon"><BarChart3 size={16} /></span><span className="signal-copy"><span>Em escala</span><strong>{loading ? "—" : scaling}<small>score 40–79</small></strong></span></div>
        <div className="signal-item"><span className="signal-icon"><Activity size={16} /></span><span className="signal-copy"><span>Redes mapeadas</span><strong>04<small>Meta · TikTok · Google · Kwai</small></strong></span></div>
      </section>

      <section className="search-panel" id="filters" aria-label="Buscar e filtrar anúncios">
        <form className="search-row" onSubmit={(event) => { event.preventDefault(); setQuery(draftQuery.trim()); }}>
          <label className="search-box"><Search size={16} /><input value={draftQuery} onChange={(event) => setDraftQuery(event.target.value)} placeholder="Nome do jogo, produto, anunciante ou palavra-chave..." aria-label="Busca textual" /><button className="text-button" type="button" onClick={() => { setDraftQuery(""); setQuery(""); }} aria-label="Limpar busca">{draftQuery && <X size={14} />}</button></label>
          <button className="button-search" type="submit"><Search size={14} />Buscar</button>
        </form>
        <div className="filter-grid">
          <div className="filter-group"><div className="filter-heading">CATEGORIA</div><select className="filter-select" value={category} onChange={(event) => setCategory(event.target.value as Category | "")} aria-label="Filtrar categoria"><option value="">Todas as categorias</option><option value="games">Jogos</option><option value="ecommerce">E-commerce</option><option value="apps">Apps / Utilitários</option><option value="finance">Finanças</option><option value="infoproducts">Infoprodutos</option></select></div>
          <div className="filter-group"><div className="filter-heading">SISTEMA OPERACIONAL</div><div className="filter-chips">{OS_OPTIONS.map((os) => <label key={os} className={`filter-chip${selectedOS.includes(os) ? " selected" : ""}`}><input type="checkbox" checked={selectedOS.includes(os)} onChange={() => toggleOS(os)} /><i className="os-dot" />{OS_LABELS[os]}</label>)}</div></div>
          <div className="filter-group"><div className="filter-heading">REDES DE ANÚNCIOS</div><div className="filter-chips">{NETWORKS.map((network) => <label key={network} className={`filter-chip${selectedNetworks.includes(network) ? " selected" : ""}`}><input type="checkbox" checked={selectedNetworks.includes(network)} onChange={() => toggleNetwork(network)} /><i className={`network-dot network-${network}`} />{NETWORK_LABELS[network]}</label>)}</div></div>
          <div className="filter-group"><div className="filter-heading">SELO / SCORE</div><div className="filter-score">{(["all", "winner", "scaling", "testing"] as ScoreBand[]).map((band) => <label key={band} className="score-option"><input type="radio" name="score" checked={scoreBand === band} onChange={() => setScoreBand(band)} /><span>{band === "all" ? "Todos" : band === "winner" ? "Winner" : band === "scaling" ? "Escala" : "Teste"}</span></label>)}</div></div>
        </div>
        <div className="filter-footer"><label className="checkbox-line"><input type="checkbox" checked={activeOnly} onChange={(event) => setActiveOnly(event.target.checked)} />Somente anúncios ativos</label><button className="text-button" type="button" onClick={clearFilters}>Limpar filtros</button></div>
      </section>

      <section id="creatives">
        <div className="results-header"><div className="results-title"><h2>Criativos encontrados</h2><span>{loading ? "Atualizando…" : `${data?.total ?? 0} resultados`}</span></div><label className="results-sort">Ordenar por<select value={sortBy} onChange={(event) => setSortBy(event.target.value as typeof sortBy)}><option value="longevity_score_desc">Maior score</option><option value="first_seen_desc">Mais recentes</option><option value="active_days_desc">Mais dias ativos</option></select></label></div>
        {error ? <div className="error-state"><Database size={23} /><h3>API indisponível</h3><p>{error}</p></div> : loading && !data ? <div className="loading-grid"><div className="skeleton" /><div className="skeleton" /></div> : ads.length ? <div className="ad-grid">{ads.map((ad) => <AdCard key={ad.id} ad={ad} onAppSynced={() => setRefreshToken((value) => value + 1)} />)}</div> : <div className="empty-state"><Search size={24} /><h3>Nenhum criativo neste recorte</h3><p>Altere os filtros ou limpe a busca para ver mais anúncios simulados.</p></div>}
        {!loading && !error && data && <div className="pagination-note"><ArrowRight size={13} />Exibindo {ads.length} de {data.total} anúncios do mock</div>}
      </section>

      <div id="about" className="pagination-note" style={{ marginTop: 32 }}><span>Fase 2 • anúncios continuam mock • dados de apps podem ser sincronizados sob demanda</span></div>
    </div>
  );
}

function Layers2Icon() {
  return <Layers3 size={16} />;
}
