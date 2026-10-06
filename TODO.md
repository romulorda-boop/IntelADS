

## Deploy do frontend na Vercel

- [x] **Build do workspace pnpm** — Criar `vercel.json` na raiz e no Root Directory `apps/web`; fixar `pnpm@11.25.0`, instalar `@adintel/web...` com `--frozen-lockfile` e usar o script `vercel-build` para executar `next build`.
- [ ] **Configuração do projeto Vercel** — Manter Root Directory `apps/web`, habilitar inclusão de fontes fora do Root Directory e definir `ADINTEL_API_ORIGIN` para o FastAPI publicamente acessível antes de usar os endpoints de dados.
