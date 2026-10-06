

## Deploy do frontend Vercel

A aplicação Next.js permanece em `apps/web`, com `apps/web` como Root Directory Vercel. A configuração efetiva fica em `apps/web/vercel.json` (e há configuração equivalente na raiz do monorepo); o projeto deve permitir acesso a fontes fora do Root Directory, pois lockfile e workspace são compartilhados na raiz. O install command fixa `pnpm@11.25.0` via `npx`, usa `--filter @adintel/web... --frozen-lockfile`, e `vercel-build` executa `next build` no pacote web sem sobrepor o diretório de output do framework. A API FastAPI é separada do frontend Vercel; `ADINTEL_API_ORIGIN` precisa apontar para uma origem pública da API em runtime/build.
