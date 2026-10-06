import Link from "next/link";
import { Activity, BadgePercent, Building2, CircleHelp, Compass, Layers3, Search, Settings2 } from "lucide-react";

const links = [
  { href: "/", label: "Visão geral", icon: Compass, active: true },
  { href: "/#creatives", label: "Criativos", icon: Layers3 },
  { href: "/#filters", label: "Explorar anúncios", icon: Search },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-frame">
      <aside className="sidebar">
        <Link href="/" className="brand-lockup" aria-label="AdIntel — página inicial">
          <span className="brand-mark" aria-hidden="true"><i /><b /><em /></span>
          <span className="brand-type">AdIntel<span className="brand-beta">BETA</span></span>
        </Link>

        <div className="workspace-select">
          <span className="workspace-avatar">A</span>
          <span className="workspace-copy"><strong>Acquisition team</strong><small>Workspace demo</small></span>
          <span className="workspace-chevron">⌄</span>
        </div>

        <div className="nav-label">INTELIGÊNCIA</div>
        <nav className="side-nav" aria-label="Navegação principal">
          {links.map(({ href, label, icon: Icon, active }) => (
            <Link key={label} href={href} className={`side-link${active ? " active" : ""}`}>
              <Icon size={17} strokeWidth={1.8} /><span>{label}</span>
              {label === "Criativos" && <span className="nav-count">18</span>}
            </Link>
          ))}
        </nav>

        <div className="nav-label nav-label-spaced">ANÁLISE</div>
        <nav className="side-nav" aria-label="Ferramentas">
          <Link href="/#creatives" className="side-link"><BadgePercent size={17} strokeWidth={1.8} /><span>Winners</span></Link>
          <Link href="/#creatives" className="side-link"><Building2 size={17} strokeWidth={1.8} /><span>Anunciantes</span></Link>
          <Link href="/#filters" className="side-link"><Activity size={17} strokeWidth={1.8} /><span>Redes</span></Link>
        </nav>

        <div className="sidebar-bottom">
          <div className="mock-status"><span className="status-dot" /><span><strong>Ambiente mock</strong><small>PostgreSQL conectado</small></span></div>
          <Link href="/#filters" className="side-link subtle"><Settings2 size={17} /><span>Preferências</span></Link>
          <Link href="/#about" className="side-link subtle"><CircleHelp size={17} /><span>Sobre o MVP</span></Link>
          <div className="sidebar-foot"><span>AD INTELLIGENCE</span><span>FASE 02</span></div>
        </div>
      </aside>
      <main className="main-shell">{children}</main>
    </div>
  );
}
