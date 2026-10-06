# Plano de implementação — Ad Intelligence, Fase 1

## Escopo e arquitetura

Construir um monorepo dentro de `/home/ubuntu/adintel` com Next.js App Router + TypeScript + Tailwind na origem de preview (porta 3000), API FastAPI em Python na porta local 8000 e PostgreSQL local para os dados mock. O Next fará proxy relativo de `/api/v1/*` para FastAPI; os componentes do browser só chamam caminhos relativos. Como o banco gerenciado WebDev disponível é MySQL, não o habilitar: a exigência explícita é PostgreSQL e o preview desta fase é no sandbox com PostgreSQL nativo. Não implementar scraping, sincronização real, workers, Elasticsearch, autenticação nem coleta de lojas.

Criar `backend/db/schema.sql` com o DDL exatamente como na seção 6.1, sem acrescentar colunas/tabelas/índices. A extensão exigida por `gen_random_uuid()` ficará em bootstrap separado. O seed terá 18 anúncios determinísticos, cobrindo Jogos/E-commerce/Apps, Meta/TikTok/Google/Kwai e Android/iOS/Desktop; downloads e ratings de lojas serão valores ilustrativos para apps/jogos. Executar a fórmula de longevity em função isolada e persistir `longevity_score` ao semear. Dados de input de fórmula inexistentes no schema (redes detectadas, placements Meta, bônus estimado de impressões) serão metadados mock do seed, não novas colunas.

A API expõe `POST /api/v1/ads/search` com busca, categoria, SO, redes, faixa de score/selo, ativo, ordenação e paginação, e `GET /api/v1/advertisers/{id}` com apps, contagens e distribuições. O frontend consome a API real local. A home apresenta filtros no topo e cards com rede, badge/score, OS, vídeo/poster, app e downloads, nota, anunciante/link, legenda, dias ativos, data de início, variações e ações de download/biblioteca. `/advertisers/[id]` exibe perfil e gráficos de pizza/rosca via Recharts.

## Estrutura de projeto

```text
apps/web/                     Next.js, páginas, componentes, estilos, API client e mídia mock
backend/app/api/v1/            rotas de busca e perfil
backend/app/db/                conexão e consultas PostgreSQL
backend/app/schemas/           modelos de request/response
backend/app/services/          longevity e agregações
backend/db/schema.sql          DDL literal da seção 6.1
backend/db/bootstrap.sql       pré-requisito pgcrypto separado do DDL
backend/seed/                  fixtures e seed determinístico/idempotente
apps/web/public/manus-routes.json manifest das páginas Preview
package.json, pnpm-workspace.yaml, pnpm-lock.yaml
.env.example                   configuração local documentada, sem credenciais reais
```

## Direção visual

- **Movimento:** painel editorial de inteligência, entre Swiss International Style e terminal analítico contemporâneo.
- **Princípios:** hierarquia por sinal/performance; densidade alta sem sacrificar leitura; filtros visíveis e combináveis; dados simulados identificáveis como mock.
- **Filosofia de cor:** base carvão-azulada para reduzir ruído; superfícies em ardósia; verde-lima ácido como cor própria de score/ação e violeta/coral para redes e alertas.
- **Layout:** faixa lateral de navegação, cabeçalho utilitário, busca e filtros compactos no topo, tira horizontal com quatro sinais e feed de criativos em duas colunas; perfil com gráficos em duas colunas no desktop e coluna única no mobile.
- **Elementos de assinatura:** monograma de varredura/linha de sinal no wordmark; pílulas de score com trilho luminoso; cartões de criativo com moldura de player.
- **Interação:** feedback em busca e filtros, estados de carregamento/sem resultados, seleção combinada e links contextuais para perfis.
- **Animação:** transições curtas (120–180 ms) para hover/foco; poster com leve zoom no hover; evitar movimento contínuo/redundante.
- **Tipografia:** Space Grotesk para títulos e Inter para interface/dados, com hierarquia tipográfica curta.
- **Essência da marca:** inteligência de anúncios para equipes de aquisição que precisam separar testes de criativos escaláveis; personalidade: precisa, incisiva, confiável.
- **Voz:** curta e orientada a evidência. Exemplos: “Criativos que continuam rodando merecem atenção.” e “Filtre o ruído. Encontre o próximo winner.”
- **Wordmark:** “AdIntel” acompanhado por um A geométrico atravessado por duas linhas de leitura/scan.
- **Cor assinatura:** verde-lima elétrica, reservada para score, estados positivos e foco principal.

## Restrições conhecidas

O schema tem apenas uma rede por anúncio e não registra placements Meta ou impressões. Portanto a fórmula é calculada fielmente com parâmetros mock no seed; o score resultante fica em `ads.longevity_score`. A duração será derivada de `first_seen_at`/`last_seen_at`. A tabela `apps` aceita apenas Android/iOS; Desktop aparece em `ads.target_os`. O gráfico temporal de 12 meses não está no recorte da Fase 1, que pediu especificamente gráficos pizza/rosca. Downloads reais, scraping e sincronização de lojas ficam para a Fase 2.
