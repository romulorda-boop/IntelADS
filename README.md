# AdIntel — Fase 1 + Fase 2

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

3. Aplique bootstrap, schema literal, migração da Fase 2 e fixtures, nesta ordem:

   ```bash
   psql -d adintel -v ON_ERROR_STOP=1 -f backend/db/bootstrap.sql
   psql -d adintel -v ON_ERROR_STOP=1 -f backend/db/schema.sql
   psql -d adintel -v ON_ERROR_STOP=1 -f backend/db/migrations/001_app_sync_status.sql
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

Google Play usa `google-play-scraper==1.2.7`, locale `pt_BR`/`br` e devolve faixa pública de instalações, rating, ícone e gênero. O adaptador iOS usa o endpoint público Apple iTunes Lookup; não é necessária chave. A consulta pública Apple não expõe downloads: após sincronizar iOS, downloads ficam indisponíveis e a interface mostra **“Não divulgado”**. Apps mock permanecem marcados **“Dados mock”**; só uma resposta real bem-sucedida gera o badge **“Sincronizado”**. As lojas podem limitar chamadas ou mudar os dados/endpoints; falhas aparecem no controle e preservam os valores previamente salvos, salvo downloads iOS que não são publicados pela loja.

## Verificações

- `pnpm typecheck`
- `pnpm build`
- `(cd backend && ../.venv/bin/python -m unittest discover -s tests -v)`
- `curl -X POST http://127.0.0.1:8000/api/v1/apps/sync/com.supercell.brawlstars`
- `curl -X POST http://127.0.0.1:8000/api/v1/apps/sync/1229016807`

Fontes externas, campos retornados e resultados de consulta estão em [`backend/INTEGRATIONS.md`](backend/INTEGRATIONS.md). As imagens e os vídeos dos anúncios mock estão documentados em `ASSET_SOURCES.md`.
