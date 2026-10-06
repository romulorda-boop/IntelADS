# AdIntel — Fases 1, 2 e 3

MVP em **Next.js + Tailwind** (porta `3000`), **FastAPI** (porta `8000`) e **PostgreSQL 16** local. `backend/db/schema.sql` permanece o DDL literal da seção 6.1 da especificação da Fase 1. A migração aditiva `backend/db/migrations/001_app_sync_status.sql` registra o estado de atualização de apps sem alterar aquele schema. Os anúncios e anunciantes continuam simulados; metadados de apps podem ser sincronizados sob demanda.

## Executar localmente

Requisitos: Node.js 22+, pnpm 11, Python 3.11+ e PostgreSQL 16.

1. Na raiz, crie o ambiente Python e instale as dependências:

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r backend/requirements.txt
   ```

2. Crie o banco `adintel` e dê ao usuário local acesso de proprietário. Em uma instalação Ubuntu com PostgreSQL:

   ```bash
   sudo -u postgres createuser --login --createdb "$(id -un)" 2>/dev/null || true
   sudo -u postgres createdb --owner="$(id -un)" adintel 2>/dev/null || true
   ```

   A conexão por socket peer é o padrão. Se usar outro usuário, defina `DATABASE_URL` no ambiente antes de iniciar o backend.

3. Aplique bootstrap, schema literal, migrations aditivas das Fases 2 e 3 e fixtures, nesta ordem:

   ```bash
   psql -d adintel -v ON_ERROR_STOP=1 -f backend/db/bootstrap.sql
   psql -d adintel -v ON_ERROR_STOP=1 -f backend/db/schema.sql
   psql -d adintel -v ON_ERROR_STOP=1 -f backend/db/migrations/001_app_sync_status.sql
   psql -d adintel -v ON_ERROR_STOP=1 -f backend/db/migrations/002_ad_analysis.sql
   (cd backend && ../.venv/bin/python -m seed.seed)
   ```

   O seed é idempotente e contém 18 anúncios, sete anunciantes e 11 apps. Preserva metadados e estado de apps já confirmados pelas lojas; apps não sincronizados voltam ao estado `mock`. Inclui Brawl Stars em Android (`com.supercell.brawlstars`) e iOS (`1229016807`) para testar as duas lojas.

4. Em um terminal, inicie o backend a partir da raiz:

   ```bash
   .venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
   ```

5. Em outro terminal, instale as dependências JavaScript uma vez e rode o frontend:

   ```bash
   pnpm install
   pnpm dev
   ```

O Next encaminha `/api/v1/*` para a API FastAPI em `http://127.0.0.1:8000`. A lista de páginas do Preview está em `apps/web/public/manus-routes.json`.

## Sincronizar um app

A API aceita o UUID do app no PostgreSQL ou seu `store_app_id` registrado:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/apps/sync/com.supercell.brawlstars
curl -X POST http://127.0.0.1:8000/api/v1/apps/sync/1229016807
```

O botão **Atualizar** também aparece no card e na lista de apps do perfil. Para executar o mesmo serviço como worker CLI:

```bash
cd backend
../.venv/bin/python -m app.workers.sync_app com.supercell.brawlstars
```

Google Play usa `google-play-scraper==1.2.7`, locale `pt_BR`/`br` e devolve faixa pública de instalações, rating, ícone e gênero. O adaptador iOS usa o endpoint público Apple iTunes Lookup; não é necessária chave. A categoria ampla do anúncio (por exemplo, **“Jogos”**) e o gênero retornado pela loja (por exemplo, **“Ação”**) são apresentados separadamente quando o dado existe. A consulta pública Apple não expõe downloads: após sincronizar iOS, downloads ficam indisponíveis e a interface mostra **“Não divulgado”**. Apps mock permanecem marcados **“Dados mock”**; só uma resposta real bem-sucedida gera o badge **“Sincronizado”**. As lojas podem limitar chamadas ou mudar os dados/endpoints; falhas aparecem no controle e preservam os valores previamente salvos, salvo downloads iOS que não são publicados pela loja.

## Verificações

- `pnpm typecheck`
- `pnpm build`
- `(cd backend && ../.venv/bin/python -m unittest discover -s tests -v)`
- `curl -X POST http://127.0.0.1:8000/api/v1/apps/sync/com.supercell.brawlstars`
- `curl -X POST http://127.0.0.1:8000/api/v1/apps/sync/1229016807`

Fontes externas, campos retornados e resultados de consulta estão em [`backend/INTEGRATIONS.md`](backend/INTEGRATIONS.md). As imagens e os vídeos dos anúncios mock estão documentados em `ASSET_SOURCES.md`.


## Fase 3 — pHash, variantes e longevidade

Na instalação limpa, o passo 3 já aplica a migration incremental e gera os eventos de aparição mock. Depois de subir PostgreSQL e concluir o seed, execute a análise:

```bash
(cd backend && ../.venv/bin/python -m app.workers.analyze_ads)
```

Se quiser regenerar os eventos de aparição simulados, reexecute o seed antes do worker; ele substitui somente eventos `is_mock=true` e preserva observações futuras reais. `schema.sql` permanece intacto.

O worker usa ImageHash/Pillow para thumbnails e imagens. Para vídeo, tenta extrair com FFmpeg o frame em 2,0 segundos e usa a thumbnail se a extração falhar. Os pHashes de 64 bits são comparados par a par; distância de Hamming `<= 10` cria uma relação em `ad_variations`. Eventos em `ad_appearances` permitem computar aparições em uma janela móvel de 30 dias; os eventos `is_mock=true` são substituídos pelo seed, preservando observações futuras reais.

Fórmula aprovada da Fase 3: `min(100, (dias_ativos × 1,5) + min(20, aparições_30d × 2) + min(20, variações_detectadas × 3))`, arredondada ao inteiro mais próximo. O worker materializa o valor em `ads.longevity_score`; os endpoints de leitura calculam score/breakdown dinamicamente para manter a janela de frequência atual.

### Endpoints de análise

- `POST /api/v1/ads/search` — retorna score, fatores, contagem e resumo das variantes junto aos filtros existentes.
- `GET /api/v1/ads/{ad_id}` — retorna detalhe, score breakdown e variantes relacionadas.
- `GET /api/v1/ads/{ad_id}/similars` — retorna score, badge, breakdown e anúncios correspondentes a até 10 bits de Hamming.

A execução do worker ocorre pela CLI acima; uma rota HTTP pública não expõe a execução pesada do processamento. A execução recorrente diária descrita como comportamento de produção na especificação não fica agendada no Preview temporário; pode ser conectada a um ambiente persistente/automação na próxima etapa.


## Publicação WebDev

O contrato de publicação usa o `Dockerfile` da raiz. A imagem instala os toolchains fixados pelo projeto, compila o frontend e inicia Next.js e FastAPI no mesmo contêiner; o `PORT` define a porta pública (padrão `3000`). O Next encaminha `/api/v1/*` e `/health` ao FastAPI interno, e `/health` é o healthcheck público do contêiner.

O banco gerenciado do WebDev não foi ativado: ele oferece MySQL, enquanto o sistema exige PostgreSQL. **Antes de publicar uma instância funcional**, configure `DATABASE_URL` como segredo de runtime com uma conexão a um PostgreSQL externamente acessível. Aplicar bootstrap, `schema.sql`, migrations e seed nesse banco continua sendo uma ação separada; a publicação não executa migrations nem seed automaticamente. Sem essa variável, o healthcheck pode responder, mas as rotas que leem dados falharão ao conectar ao banco.


## Deploy do frontend na Vercel

Configure o **Root Directory** do projeto Vercel como `apps/web` e mantenha habilitado **Include source files outside of the Root Directory in the Build Step**: `pnpm-lock.yaml`, `pnpm-workspace.yaml` e o `package.json` que fixa o pnpm vivem na raiz do monorepo. A Vercel lê o `vercel.json` do Root Directory, portanto a configuração efetiva está em `apps/web/vercel.json`; o [`vercel.json` da raiz](./vercel.json) também foi incluído para o contexto do monorepo. A instalação usa `npx` para chamar explicitamente `pnpm@11.25.0`, instala o filtro `@adintel/web...` com lockfile congelado e executa `vercel-build` (`next build`); o output de Next.js é detectado pelo framework, sem `outputDirectory` customizado.

O frontend é implantado separadamente do FastAPI. Antes de usar a API em produção, configure `ADINTEL_API_ORIGIN` nas variáveis da Vercel com a origem pública do backend FastAPI; o padrão `http://127.0.0.1:8000` serve apenas para desenvolvimento local/contêiner combinado. Consulte a [documentação de monorepos](https://vercel.com/docs/monorepos), [builds](https://vercel.com/docs/builds/configure-a-build) e [vercel.json](https://vercel.com/docs/project-configuration/vercel-json).
