const DEMO_PASSWORD = 'qwerty12345';

export const demoUsers = [
  { login: 'жюри1', password: DEMO_PASSWORD },
  { login: 'жюри2', password: DEMO_PASSWORD },
  { login: 'жюри3', password: DEMO_PASSWORD },
  { login: 'жюри4', password: DEMO_PASSWORD },
  { login: 'жюри5', password: DEMO_PASSWORD },
  { login: 'жюри6', password: DEMO_PASSWORD },
  { login: 'жюри7', password: DEMO_PASSWORD },
  { login: 'жюри8', password: DEMO_PASSWORD },
  { login: 'жюри9', password: DEMO_PASSWORD },
  { login: 'жюри10', password: DEMO_PASSWORD },
] as const;

// Must match ADMIN_LOGIN / ADMIN_PASSWORD in .env (backend migration 0011_seed_admin).
export const demoAdmin = {
  login: 'admin',
  password: 'admin12345',
} as const;
