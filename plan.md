# Plano de implementação — Ad Intelligence, Fases 1, 2 e 3

## Fase 1 — MVP com dados simulados (concluída)

O monorepo em `/home/ubuntu/adintel` usa Next.js App Router + TypeScript + Tailwind no Preview (porta 3000), FastAPI local (porta 8000) e PostgreSQL local. O Next encaminha URLs relativas `/api/v1/*` ao FastAPI. O banco gerenciado do WebDev não foi habilitado, pois é MySQL e o projeto exige PostgreSQL. A Fase 1 entrega busca, filtros, card, perfil, schema literal da seção 6.1 e seed mock; os dados foram validados contra a especificação.

## Fase 2 — sincronização com lojas

- **Google Play:** adicionar `google-play-scraper==1.2.7` e um cliente isolado em `backend/app/services/stores/google_play.py`, consultando por pacote com locale `pt_BR`/`br`. Normalizar installs, nota, ícone e categoria antes de persistir.
- **App Store:** usar a API pública oficial iTunes Lookup por `trackId`, sem credencial. O client em `backend/app/services/stores/apple_app_store.py` mapeia título, nota, ícone e gênero. A consulta pública não fornece downloads/instalações; depois de sincronizar iOS, gravar `downloads_count = NULL` e exibir “Não divulgado pela loja”, sem manter o valor mock como se fosse real.
- **Persistência evolutiva:** manter `backend/db/schema.sql` da Fase 1 intacto; aplicar `backend/db/migrations/001_app_sync_status.sql` para adicionar `sync_status` (`mock`, `syncing`, `synced`, `error`) e `last_sync_error`. `last_synced_at` já existe no schema base. Erros externos não sobrescrevem metadados válidos; respostas e logs não expõem credenciais (não são necessárias) nem corpos crus de terceiros.
- **Worker e API:** criar serviço orquestrador compartilhado por `backend/app/workers/sync_app.py` (CLI) e `POST /api/v1/apps/sync/{app_id}`. A rota aceita o UUID local ou `store_app_id` existente, consulta somente apps registrados, faz uma requisição síncrona com timeout e persiste o resultado; não introduzir Redis/Celery nesta etapa. O endpoint retorna o estado e os metadados atualizados.
- **Demonstração iOS real:** incluir um cadastro de Brawl Stars para iOS (track ID `1229016807`, obtido no catálogo público Apple) associado ao anunciante Supercell para que o teste iOS possa ser acionado pela própria interface. Reexecutar seed é idempotente por UUID: preserva metadados/status sincronizados; registros sem sync confirmado recebem de novo os valores mock e limpam erro antigo.
- **Frontend:** estender as respostas de busca e perfil com UUID do app, categoria da loja, origem/estado e `last_synced_at`; adicionar botão “Sincronizar loja”, estado de carregamento/erro e badge “Sincronizado” apenas depois de resposta real bem-sucedida. Após sucesso, atualizar busca, card e perfil para refletir os valores gravados no PostgreSQL. Exibir a categoria ampla do anúncio (por exemplo, “Jogos”) separada do gênero da loja (por exemplo, “Ação”) quando disponível; estado `mock` permanece explicitamente marcado como mock.
- **Operação:** configurar `.env.example`/README para a migração, dependência e execução de API, CLI e Preview. Google Play scraper pode sofrer bloqueios ou mudanças nos endpoints não oficiais; Apple Lookup é público e pode omitir métricas. Não se promete download de iOS nem persistência fora deste sandbox/instância.

## Estrutura

```text
apps/web/src/components/app-sync-controls.tsx    badge e ação reutilizável de sync
apps/web/src/lib/api.ts, types.ts                 contratos para sync e metadados reais
backend/app/api/v1/routes/apps.py                 POST de sincronização
backend/app/services/app_sync.py                  resolução, orquestração e persistência
backend/app/services/stores/google_play.py        cliente de enriquecimento Google Play
backend/app/services/stores/apple_app_store.py    cliente da API pública iTunes Lookup
backend/app/workers/sync_app.py                   entrada de worker via CLI
backend/db/migrations/001_app_sync_status.sql     alteração aditiva do schema já entregue
backend/tests/                                   testes de mapeamento, sucesso e erro
```

## Direção visual existente

- **Movimento:** painel editorial de inteligência, entre Swiss International Style e terminal analítico contemporâneo.
- **Princípios:** hierarquia por sinal/performance; densidade alta sem sacrificar leitura; filtros visíveis e combináveis; dados mock identificáveis.
- **Cor:** base carvão-azulada e superfícies em ardósia; verde-lima para score, sucesso real e ação; violeta/coral para redes e alertas.
- **Layout:** faixa lateral, cabeçalho utilitário, busca/filtros no topo, tira de métricas e feed em duas colunas; perfil e apps adaptáveis a coluna única no mobile.
- **Assinaturas:** monograma de varredura, score em pílula, cards com moldura de player; badge distinto entre “Mock” e “Sincronizado”.
- **Interação/animação:** feedback claro para carregando, sucesso e falha; transições curtas (120–180 ms), preview de mídia no hover, sem movimento contínuo.
- **Tipografia:** Space Grotesk para títulos e Inter para interface/dados.
- **Essência:** inteligência de anúncios para equipes de aquisição; precisa, incisiva, confiável. Voz direta: “Filtre o ruído. Encontre o próximo winner.”
- **Wordmark:** “AdIntel” com A geométrico e linha de scan; cor própria: verde-lima elétrica.

## Limites conhecidos

Os campos de downloads do Google Play são faixas públicas de instalações, não downloads exatos. A API pública Apple não expõe downloads; UI deve dizer isso claramente. Dados mock existentes não são fonte de verdade após sync de loja. A taxa de chamadas e disponibilidade dependem das lojas: não haverá scraping de anúncios, workers agendados, autenticação ou fila Redis nesta fase.


## Fase 3 — Processamento de mídia e inteligência (concluída)

- **pHash:** usar Pillow e ImageHash (`phash`, 64 bits). Para vídeo, tentar extrair o frame em 2,0 s com FFmpeg; se falhar ou não houver vídeo local, calcular a assinatura da thumbnail. Comparar pares por distância de Hamming e relacionar automaticamente pares `<= 10` na tabela `ad_variations`, apagando/recriando somente essas relações derivadas quando o worker rodar.
- **Frequência:** preservar o `schema.sql` literal da Fase 1 e adicionar `backend/db/migrations/002_ad_analysis.sql`, com eventos de aparição em `ad_appearances` e marcador `is_mock`. A frequência do score conta eventos cujo `observed_at` esteja entre agora e os 30 dias anteriores; timestamps futuros ficam fora.
- **Fórmula aprovada:** `score = min(100, dias_ativos × 1,5 + min(20, aparições_30d × 2) + min(20, variações_detectadas × 3))`, arredondado para inteiro. Os badges Winner/Scaling/Testing mantêm os limiares já usados. O worker recalcula pHash, relações e score; busca e detalhe calculam métricas atuais usando a mesma regra.
- **API:** ampliar `POST /api/v1/ads/search` com score/breakdown e resumo de variantes; incluir `GET /api/v1/ads/{id}` e `GET /api/v1/ads/{id}/similars`. Modelos Pydantic explícitos descrevem no OpenAPI score, breakdown, badges e listas correlacionadas. O processamento pesado permanece no CLI `python -m app.workers.analyze_ads`, evitando expor uma rota pública sem autenticação que reexecuta todo o worker.
- **Frontend:** mostrar barra de progresso no card e na modal de detalhe, com fatores de score e a seção “Variações Encontradas”. A modal mantém Escape, foco inicial, confinamento de Tab e restauração do foco ao fechar.
- **Estrutura:** `backend/app/services/phash.py` (hash e Hamming), `backend/app/services/ad_analysis.py` (pipeline e score), `backend/app/workers/analyze_ads.py` (CLI), `backend/db/migrations/002_ad_analysis.sql` (eventos), `backend/tests/test_phash.py` (lógica), e componentes `longevity-meter.tsx`/`ad-details-modal.tsx` em `apps/web/src/components`.
- **Limite operacional:** esta entrega habilita execução sob demanda pela CLI. O recálculo diário mencionado no roteiro de produção da especificação não é agendado no Preview temporário; requer ambiente persistente e será tratado como automação/deployment separado.
- **Rastreabilidade da fórmula:** a fórmula original da seção 5.1 permanece como histórico da Fase 1; a fórmula acima, aprovada para a Fase 3, passa a ser a fórmula runtime vigente.


## Contrato de publicação WebDev

- Uma imagem `Dockerfile` da raiz instala a versão de Node e pnpm fixada pelo monorepo, as dependências Python do backend e FFmpeg para os workers. O build de produção do Next.js é realizado no próprio contêiner, sem um contrato de build estático separado.
- `docker-entrypoint.sh` supervisiona Next.js e FastAPI no mesmo contêiner. O Next atende a porta pública `PORT` (3000 por padrão); FastAPI fica em `127.0.0.1:8000`. Rewrites encaminham `/api/v1/*` e `/health` ao FastAPI; `/health` não depende da conexão ao banco.
- `DATABASE_URL` precisa ser um segredo de runtime apontando para um PostgreSQL externo. O banco gerenciado WebDev é MySQL e não é compatível com o schema; migrations e seed são operados separadamente, sem inicialização destrutiva no boot.
