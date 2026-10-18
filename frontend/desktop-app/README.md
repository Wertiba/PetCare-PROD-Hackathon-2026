# petcare desktop pet

Electron-питомец: висит поверх окон, опрашивает `/events/upcoming`
и зовёт пользователя, когда наступает время события.

```bash
pnpm install
pnpm dev          # electron-vite dev
pnpm build        # сборка в out/
pnpm start        # запуск собранного
pnpm lint
pnpm typecheck
```

Если терминал унаследовал `ELECTRON_RUN_AS_NODE=1` (бывает внутри
расширений VS Code), Electron запустится как Node — сбросьте переменную:
`env -u ELECTRON_RUN_AS_NODE pnpm dev`.

## Настройки

- `src/shared/config.ts` — `APP_URL`, куда ведёт «Открыть» (`/dashboard`).
- `src/main/config.ts` — `API_URL` (переопределяется `PETCARE_API_URL`),
  интервалы опроса, «отложить».

## Как устроено

- `src/main` — опрос бэка и таймеры на точное время события
  (`scheduler.ts`), пересинхронизация после сна (`powerMonitor`),
  очередь событий и системные уведомления (`alerts.ts`), refresh-токен
  в `safeStorage` (`session.ts`), трей (`tray.ts`).
- `src/preload` — по одному минимальному API на окно (`pet`, `login`).
- `src/renderer` — окно питомца (сейчас текстовая заглушка) и копия
  формы входа из основного приложения.
- `src/shared` — копии типов из `frontend/src` (держать в синхроне)
  и IPC-контракт `ipc.ts`.
