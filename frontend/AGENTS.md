<!-- BEGIN:nextjs-agent-rules -->

# AGENTS.md

## Project
- Use the existing stack, architecture, dependencies, and conventions.
- Read `package.json` and relevant files before making changes.
- Make the smallest complete change that solves the task.
- Do not rewrite unrelated code or introduce unnecessary abstractions.
- Do not add dependencies or change configuration without a clear need.
- Never overwrite existing work unrelated to the task.

## Workflow
1. **Read `agents/architecture.md` first.** Use it to determine where files belong and follow the documented conventions.
2. If the actual codebase differs from `agents/architecture.md`, investigate the discrepancy and update the documentation before proceeding.
3. Inspect only the files relevant to the task.
4. Identify existing patterns and reuse them.
5. Implement the change with minimal, focused edits.
6. Run relevant lint, type-check, tests, or build commands.
7. Report what changed and any checks that failed.

## Next.js
- Use the App Router and follow the existing route structure.
- Prefer Server Components by default.
- Add `"use client"` only when client-side interactivity or browser APIs are needed.
- Keep server-only code out of client components.
- Use appropriate loading, error, and empty states.
- Avoid unnecessary `useEffect`, duplicate state, and client-side fetching when existing server or query patterns suffice.
- Follow Next.js conventions for layouts, pages, loading, errors, and route handlers.

## TypeScript & React
- Keep types strict; avoid `any` and unsafe type assertions.
- Use `interface` for object shapes and `type` for unions and other type aliases.
- Use descriptive names; avoid vague abbreviations.
- Extract components when it improves reuse or readability, not by default.
- Keep components focused and state close to where it is used.

## State & Data
- Use local React state for component-specific state.
- Use Zustand only for state genuinely shared across components.
- Use TanStack Query for client-side server-state fetching and caching when the project already uses it.
- Avoid duplicating server data in Zustand.
- Follow the project's existing API and error-handling patterns.

## Architecture
- Preserve the existing architecture; do not reorganize folders without a reason.
- The project uses FSD-style layers (`src/app`, `entities`, `features`, `widgets`, `shared`) — respect layer boundaries and public APIs; `agents/architecture.md` documents the details (structure, dependency rule, conventions, where new files go).

## UI & Styling
- Follow the existing design system, fonts, colors, and spacing conventions.
- Prioritize visual hierarchy, typography, composition, and responsive behavior.
- Avoid generic layouts and decorative effects without a clear design purpose.
- Build accessible interfaces with semantic HTML, keyboard support, and visible focus states.
- Use Tailwind CSS and existing UI components; avoid unnecessary custom CSS.
- Check mobile and desktop layouts when changing UI.

## Code Quality
- Follow the repository's formatter and lint rules.
- Reuse existing utilities and components before creating alternatives.
- Handle expected errors and edge cases.
- Do not leave debug logs, dead code, or placeholder implementations.
- Do not claim a check passed unless it was actually run.

## Git & Dependencies
- Do not commit, push, or change branches unless explicitly requested.
- Respect the existing lockfile and package manager.
- Do not install a package when existing tools can solve the problem.

## Design
Read `Design-style.md` before creating or substantially modifying UI.
Follow its visual quality rules and anti-patterns.
Review the rendered result before considering visual work complete.

## Product Context
- Read `product.md` before planning or implementing product features.
- Treat it as the source of truth for product requirements.
- Do not invent requirements or expand product scope without approval.
- Read only the relevant sections when working on isolated tasks.

<!-- END:nextjs-agent-rules -->
