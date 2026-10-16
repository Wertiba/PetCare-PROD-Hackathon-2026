# Project Architecture

Auth template: Next.js 16 (App Router, React 19, Turbopack, React Compiler) + TypeScript strict, Tailwind CSS v4, TanStack Query 5, Zustand 5, Axios, Zod, React Hook Form. Package manager: pnpm.

## Structure

```
app/                    # Next.js App Router — route entry points only
  layout.tsx            # Root layout: Google fonts (Geist only), QueryProvider → SessionProvider
  page.tsx              # Route "/" (landing)
  login/page.tsx        # Route "/login" — AuthShell + LoginForm
  register/page.tsx     # Route "/register" — AuthShell + RegisterForm
  globals.css           # Tailwind v4 import + re-export of ../ui/globals.css
ui/                     # Centralized design styles (design tokens, body styles) — replace this folder to re-skin the app
  globals.css           # :root tokens, @theme inline, body styles; imported by app/globals.css
src/                    # FSD-style layers, path alias @src/*
  app/                  # App-wide setup (non-routing)
    providers/          # query-provider.tsx (TanStack Query client), session-provider.tsx (session restore + 401 sync with user store)
    init/               # Reserved for app initialization (currently empty)
    styles/             # Reserved (currently empty)
  entities/             # Domain entities
    user/
      api/              # fetch-user.ts (GET /users/me), user.dto.ts (UserDto, UserAndTokenDto — mirror backend schemas)
      model/            # user.store.ts (Zustand useUserStore), user.selectors.ts, types.ts (domain User type)
      ui/               # Entity UI (currently empty)
  features/             # User-facing actions; each slice: api/ + model/ + ui/
    login/              # api: login.ts + login.dto.ts; model: use-login-mutation.ts, validation.ts (Zod)
    register/           # api: register.ts + register.dto.ts; model: use-register-mutation.ts, validation.ts
    logout/             # api: logout.ts; model: use-logout-mutation.ts
  widgets/              # Large composed UI blocks; flat ui/ folder, named exports in barrel
    ui/AuthShell.tsx    # Shared auth-page layout (header + centered plain panel)
    ui/Background.tsx   # Plain white fixed layer (#app-background)
    ui/Header.tsx       # Standard top nav bar; exports linkClasses / whiteLinkClasses
    ui/LoginForm.tsx    # React Hook Form + Zod + useLoginMutation
    ui/RegisterForm.tsx
    ui/UserMenu.tsx     # Shows user from store, logout action
  shared/               # Framework-agnostic reusable code
    api/client.ts       # Axios instance for /api/v1: Bearer token injection, snake→camel case conversion, 401 → refresh-token retry, setOnUnauthorized()
    api/query-keys.ts   # Central TanStack Query key registry
    config/env.ts       # API_BASE_URL from NEXT_PUBLIC_API_BASE_URL (default '' = same-origin via rewrites)
    lib/token.ts        # Access token in localStorage (get/set/clear)
    lib/case-converter.ts
    ui/FormField.tsx    # Reusable labeled input with error display
    ui/SubmitButton.tsx
  app|entities|features|widgets|shared → index.ts barrel per slice/segment
```

Root config: `next.config.ts` (rewrites `/api/v1/*` → `BACKEND_ORIGIN` :8080, `reactCompiler`, `cacheComponents`), `tsconfig.json` (`@src/*` alias), `eslint.config.mjs` (TS type-checked + Prettier), `.prettierrc` (printWidth 60, single quotes, import sorting), `Dockerfile`, `mock-backend.cjs` (test-only auth backend mock on :8080).

## Layer dependency rule

`app/ (routes) → widgets → features → entities → shared`. Imports go downward only via `@src/<layer>` (e.g. `@src/shared/api`, `@src/entities/user`, `@src/features/login`) or relative within a slice. Never import another slice's internal files directly — go through its `index.ts` barrel. Exception seen in `features/login`: validation schemas are imported from `@src/features/login/model/validation.ts` by widgets (feature-internal path, same slice boundary).

## Conventions

- **Pages are thin**: route files in `app/` only compose widgets; all logic lives in `src/` layers.
- **API**: endpoint functions in `<layer>/api/*.ts` using the shared `api` client; request/response types as `*Dto` interfaces mirroring backend schemas. Server responses are snake_case — the Axios interceptor converts to camelCase automatically.
- **Server state**: TanStack Query mutations/queries in `<feature>/model/use-*.ts` hooks; query keys registered in `shared/api/query-keys.ts`.
- **Auth state**: Zustand `useUserStore` (entities layer) holds the current user; access token via `shared/lib/token.ts`; session lifecycle wired in `src/app/providers/session-provider.tsx`.
- **Forms**: React Hook Form + `@hookform/resolvers/zod`; Zod schemas in `<feature>/model/validation.ts`; UI via `shared/ui` FormField/SubmitButton.
- **Client components**: `"use client"` on files using hooks/browser APIs (all mutations, forms, canvas widgets). Pages/layouts stay server components.
- **Styling**: Tailwind utility classes only; design tokens defined in `ui/globals.css` `@theme inline` (imported via `app/globals.css`). Design-specific styles are centralized in `ui/` so they can be swapped as a unit.

## Where to put new files

- New route → `app/<route>/page.tsx` (thin composition).
- Page-composing block (section, form panel, nav) → `src/widgets/ui/`.
- New user action (auth flow, form submit, endpoint call with side effects) → `src/features/<name>/{api,model,ui}` + barrel.
- New domain entity consumed across features → `src/entities/<name>/{api,model,ui}` + barrel.
- Reusable primitive (input, button, hook, util) → `src/shared/{ui,lib,api,config}`.
- New query key → `src/shared/api/query-keys.ts`.
- Global provider / app init → `src/app/providers/` or `src/app/init/`.
