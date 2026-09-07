'use client';

import { useEffect, useState } from 'react';

/** Alterna claro/escuro e lembra a escolha. O escuro é o padrão. */
export function ThemeToggle() {
  const [tema, setTema] = useState<'dark' | 'light'>('dark');

  useEffect(() => {
    const guardado = localStorage.getItem('df-theme');
    const inicial = guardado === 'light' ? 'light' : 'dark';
    setTema(inicial);
    document.documentElement.dataset.theme = inicial;
  }, []);

  const alternar = () => {
    const proximo = tema === 'dark' ? 'light' : 'dark';
    setTema(proximo);
    document.documentElement.dataset.theme = proximo;
    try {
      localStorage.setItem('df-theme', proximo);
    } catch {
      /* modo privado: a escolha simplesmente não persiste */
    }
  };

  return (
    <button
      onClick={alternar}
      className="rounded-lg p-2 text-muted transition-colors hover:bg-raised hover:text-accent"
      aria-label={tema === 'dark' ? 'Mudar para tema claro' : 'Mudar para tema escuro'}
      title={tema === 'dark' ? 'Tema claro' : 'Tema escuro'}
    >
      {tema === 'dark' ? (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle cx="12" cy="12" r="4.2" stroke="currentColor" strokeWidth="1.8" />
          <path
            d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M18.7 5.3l-1.4 1.4M6.7 17.3l-1.4 1.4"
            stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"
          />
        </svg>
      ) : (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M20 14.2A8.2 8.2 0 0 1 9.8 4a8.4 8.4 0 1 0 10.2 10.2Z"
            stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"
          />
        </svg>
      )}
    </button>
  );
}
