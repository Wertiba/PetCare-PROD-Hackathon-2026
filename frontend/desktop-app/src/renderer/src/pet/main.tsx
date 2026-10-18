import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import '../styles.css';
import { Pet } from './Pet';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Pet />
  </StrictMode>,
);
