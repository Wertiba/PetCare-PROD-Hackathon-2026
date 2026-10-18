import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import '../styles.css';
import { IntervalForm } from './IntervalForm';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <main className="min-h-screen bg-[var(--white)] px-5 py-6 text-[var(--ink)]">
      <IntervalForm />
    </main>
  </StrictMode>,
);
