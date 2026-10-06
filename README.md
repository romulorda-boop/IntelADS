

## Deploy do frontend na Vercel

Configure o **Root Directory** do projeto Vercel como `apps/web` e mantenha habilitado **Include source files outside of the Root Directory in the Build Step**: `pnpm-lock.yaml`, `pnpm-workspace.yaml` e o `package.json` que fixa o pnpm vivem na raiz do monorepo. A Vercel lê o `vercel.json` do Root Directory, portanto a configuração efetiva está em `apps/web/vercel.json`; o [`vercel.json` da raiz](./vercel.json) também foi incluído para o contexto do monorepo. A instalação usa `npx` para chamar explicitamente `pnpm@11.25.0`, instala o filtro `@adintel/web...` com lockfile congelado e executa `vercel-build` (`next build`); o output de Next.js é detectado pelo framework, sem `outputDirectory` customizado.

O frontend é implantado separadamente do FastAPI. Antes de usar a API em produção, configure `ADINTEL_API_ORIGIN` nas variáveis da Vercel com a origem pública do backend FastAPI; o padrão `http://127.0.0.1:8000` serve apenas para desenvolvimento local/contêiner combinado. Consulte a [documentação de monorepos](https://vercel.com/docs/monorepos), [builds](https://vercel.com/docs/builds/configure-a-build) e [vercel.json](https://vercel.com/docs/project-configuration/vercel-json).
