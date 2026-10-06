# AdIntel — MVP Fase 1

MVP em **Next.js + Tailwind** (porta `3000`), **FastAPI** (porta `8000`) e **PostgreSQL 16** local. `backend/db/schema.sql` contém o DDL da seção 6.1 da especificação; `bootstrap.sql` habilita `pgcrypto` separadamente. Os anunciantes, criativos, scores, downloads e ratings são simulados. Não há scraping nem sincronização real com lojas nesta fase.

## Executar localmente

Requisitos: Node.js 22+, pnpm 11, Python 3.11+ e PostgreSQL 16.

1. Na raiz do projeto, crie o ambiente Python e instale as dependências:

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r backend/requirements.txt
   ```

2. Crie o banco `adintel` e dê ao usuário local acesso de proprietário. Em uma instalação Ubuntu com PostgreSQL:

   ```bash
   sudo -u postgres createuser --login --createdb "$(id -un)" 2>/dev/null || true
   sudo -u postgres createdb --owner="$(id -un)" adintel 2>/dev/null || true
   ```

   A URL de socket peer está em `.env.example`. Se usar outro usuário, defina `DATABASE_URL` no ambiente; o backend lê essa variável ao iniciar.

3. Aplique o bootstrap, o schema literal e os fixtures. Execute a partir da raiz:

   ```bash
   psql -d adintel -v ON_ERROR_STOP=1 -f backend/db/bootstrap.sql
   psql -d adintel -v ON_ERROR_STOP=1 -f backend/db/schema.sql
   (cd backend && ../.venv/bin/python -m seed.seed)
   ```

   O seed é idempotente e carrega 18 anúncios, sete anunciantes e dez apps simulados.

4. Em um terminal, inicie o backend a partir da raiz:

   ```bash
   .venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
   ```

5. Em outro terminal, instale as dependências JS uma vez e rode o frontend:

   ```bash
   pnpm install
   pnpm dev
   ```

O Next encaminha `/api/v1/*` para a API FastAPI configurada por `ADINTEL_API_ORIGIN` (padrão `http://127.0.0.1:8000`). A lista de páginas do Preview está em `apps/web/public/manus-routes.json`.

## Verificações rápidas

- `pnpm typecheck`
- `pnpm build`
- `(cd backend && ../.venv/bin/python -m unittest discover -s tests -v)`

As imagens selecionadas para os anúncios mock estão listadas em `ASSET_SOURCES.md`; os vídeos MP4 são gerados localmente a partir delas para demonstrar o player e o download.
