# TODO — Ad Intelligence

## Fase 1 — MVP & Interface com Dados Simulados (concluída)

- [x] **PostgreSQL e seed mock** — Criar o banco PostgreSQL usando exatamente o arquivo `schema.sql` descrito na seção 6.1 da especificação técnica. Popular com 15 a 20 anúncios simulados (implementação: 18), cobrindo diferentes categorias (Jogos, E-commerce, Apps), redes (Meta, TikTok, Google, Kwai) e sistemas operacionais (Android, iOS, Desktop). Incluir dados de downloads das lojas para os jogos.
- [x] **API FastAPI e Ad Longevity Score** — Implementar `POST /api/v1/ads/search` e `GET /api/v1/advertisers/{id}`. O endpoint de busca deve permitir pesquisa/filtros e paginação de anúncios; ambos devem consultar os dados mock do PostgreSQL. Aplicar a fórmula Ad Longevity Score da seção 5.1: `min(100, (Dias_ativos * 1.5) + (Num_redes * 10) + (Num_plataformas * 5) + Bonus_impressoes)`; classificar Score >= 80 como Winner, entre 40 e 79 como Scaling/Em Escala, e abaixo de 40 como Testing/Em Teste.
- [x] **Frontend Next.js + Tailwind: busca e cards** — Criar a página inicial com painel de busca e filtros superiores por Categoria, SO, Redes e Selos/Score. Implementar o card visual conforme a seção 8.2, mostrando badge Winner/Em Escala, player de vídeo/preview, dados do app e downloads, botões de baixar vídeo e abrir na biblioteca, rede, score, OS, anunciante/perfil, legenda, tempo ativo e variações.
- [x] **Perfil do anunciante e execução local/preview** — Criar `/advertisers/[id]` com dados do anunciante e gráficos de pizza/rosca. Deixar o ambiente local/preview executável com o mock funcional e os filtros testáveis. Esta fase não inclui sincronização real com lojas de apps nem scraping.

## Fase 2 — Sincronização Real com Lojas de Apps e Serviços Externos (concluída)

- [x] **Worker Google Play Store** — Implementar um script/worker em Python (usando a biblioteca `google-play-scraper`) que receba o `app_id` de um jogo, extraia os dados atualizados (número de downloads, nota/rating, ícone, categoria) e atualize a tabela no PostgreSQL. A faixa pública de instalações da loja é preservada como faixa, não apresentada como contagem exata.
- [x] **Worker App Store (iOS)** — Implementar a integração equivalente para a loja da Apple (usando `app-store-scraper` ou API pública de consulta de pacotes iOS). A API pública escolhida preserva o limite real de dados da loja: quando downloads/instalações não são publicados para iOS, não inventar o valor nem apresentar o mock como dado sincronizado.
- [x] **Endpoint de atualização e métricas** — Criar o endpoint FastAPI `POST /api/v1/apps/sync/{app_id}` para disparar essa sincronização e atualizar automaticamente as métricas exibidas nos cards do frontend.
- [x] **Interface com status de sincronização** — No card do anúncio e na página do anunciante, exibir dinamicamente downloads e avaliação vindos da loja, atualizar a interface após sincronização bem-sucedida e mostrar um badge `Sincronizado` somente para dados confirmados pela loja.

### Evidências desta entrega

- Build de produção Next.js concluído; typecheck TypeScript aprovado.
- Dez testes Python passaram, incluindo resposta Apple fora do formato esperado e persistência do status `error` em falhas inesperadas.
- Sync real via Google Play e App Store e teste do botão no Preview. Reexecução do seed verificada: preserva três apps sincronizados e restaura estado `mock` para registro não sincronizado com erro antigo.
- PostgreSQL de desenvolvimento: 18 anúncios e 11 apps; Preview e proxy de API respondendo.


## Fase 3 — Processamento de Mídia e Inteligência de Anúncios (concluída)

- [x] **Worker de Perceptual Hashing (pHash)** — Criar um módulo em Python (backend) para gerar assinaturas visuais (pHash) das imagens e thumbnails de anúncios. Adicionar a lógica de comparação de distância Hamming para agrupar automaticamente anúncios parecidos ou variações do mesmo criativo. Para vídeos, a especificação original determina extração do frame em 2,0 s; usar a thumbnail como fallback.
- [x] **Algoritmo de Ad Longevity Score** — Criar uma função/serviço no FastAPI que calcula a nota de longevidade do anúncio (0 a 100) combinando: tempo ativo em dias, frequência de aparição nos últimos 30 dias e quantidade de variações detectadas. Aplicar a fórmula aprovada: `min(100, (dias_ativos × 1,5) + min(20, aparições_30d × 2) + min(20, variações_detectadas × 3))`.
- [x] **Endpoints de Análise** — Atualizar os endpoints de listagem e detalhes do anúncio para retornar a nota de longevidade e a lista de anúncios variantes correlacionados.
- [x] **Ajustes no Frontend (Next.js)** — Atualizar os cards de anúncios e a modal de detalhes para exibir o badge do Ad Longevity Score com barra de progresso visual. Adicionar uma aba ou seção de “Variações Encontradas” mostrando os outros anúncios visualmente idênticos ou parecidos.

> Nota operacional: o worker pode ser executado via CLI no Preview temporário; não há endpoint HTTP público para disparar o processamento pesado. A execução diária mencionada no roteiro de produção da especificação não é agendada nesta fase e requer ambiente persistente.

### Evidências da Fase 3

- Worker pHash processou 18 anúncios, gerou 18 hashes e 49 pares com distância `<= 10`, sem erros.
- 24 testes Python passaram; build de produção e typecheck TypeScript passaram.
- Busca, filtros, score/breakdown, detalhe, similars, proxy Next e abertura da modal foram exercitados; a árvore `schema.sql` permaneceu inalterada.
- No Preview, “Jogos” e o gênero da loja “Ação” aparecem separados; filtro de jogos, seleção de variante e fechamento por Escape e pelo botão X foram verificados.


## Publicação do contêiner

- [x] **Contrato de publicação WebDev** — Configurar o domínio `deploy` com Dockerfile raiz e healthPath `/health`; construir e iniciar Next.js e FastAPI no mesmo contêiner, encaminhar API e healthcheck e respeitar `PORT`.
- [ ] **PostgreSQL da instância publicada** — Configurar `DATABASE_URL` como segredo de runtime para um PostgreSQL externo e preparar schema, migrations e seed nesse banco antes de usar as rotas de dados. O banco gerenciado WebDev é MySQL e permanece desabilitado por incompatibilidade.
