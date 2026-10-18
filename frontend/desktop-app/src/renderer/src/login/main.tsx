import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import '../styles.css';
import { LoginPage } from './LoginPage';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <LoginPage />
  </StrictMode>,
);
