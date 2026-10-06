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
