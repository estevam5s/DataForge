'use client';

import { useState } from 'react';
import { tokenize, classePorTipo } from '@/lib/highlight';

type Props = {
  code: string;
  /** 'df' realça DataForge; 'bash', 'toml', 'json' e 'text' têm tratamento próprio. */
  lang?: 'df' | 'bash' | 'toml' | 'json' | 'text';
  /** Rótulo exibido no topo do bloco — normalmente o nome do arquivo. */
  title?: string;
};

/** Realce leve para linguagens que não são DataForge. */
function realceSimples(code: string, lang: string) {
  if (lang === 'bash') {
    return code.split('\n').map((linha, i) => {
      const comentario = linha.match(/(^|\s)(#.*)$/);
      const corpo = comentario ? linha.slice(0, comentario.index! + comentario[1].length) : linha;
      const [cmd, ...resto] = corpo.split(' ');
      return (
        <span key={i}>
          {cmd && <span className="tk-function">{cmd}</span>}
          {resto.length > 0 && (
            <span>
              {' '}
              {resto.map((p, k) => (
                <span key={k} className={p.startsWith('-') ? 'tk-operator' : ''}>
                  {p}{k < resto.length - 1 ? ' ' : ''}
                </span>
              ))}
            </span>
          )}
          {comentario && <span className="tk-comment">{comentario[2]}</span>}
          {i < code.split('\n').length - 1 && '\n'}
        </span>
      );
    });
  }
  if (lang === 'toml') {
    return code.split('\n').map((linha, i) => {
      let el: React.ReactNode = linha;
      if (linha.trim().startsWith('[')) el = <span className="tk-declaration">{linha}</span>;
      else if (linha.includes('=')) {
        const [k, ...v] = linha.split('=');
        el = (
          <>
            <span className="tk-property">{k}</span>
            <span className="tk-operator">=</span>
            <span className="tk-string">{v.join('=')}</span>
          </>
        );
      } else if (linha.trim().startsWith('#')) el = <span className="tk-comment">{linha}</span>;
      return <span key={i}>{el}{'\n'}</span>;
    });
  }
  return code;
}

export function CodeBlock({ code, lang = 'df', title }: Props) {
  const [copiado, setCopiado] = useState(false);
  const fonte = code.replace(/\n$/, '');

  const copiar = async () => {
    try {
      await navigator.clipboard.writeText(fonte);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 1800);
    } catch {
      /* clipboard indisponível (http, permissão) — silencioso */
    }
  };

  const conteudo =
    lang === 'df'
      ? tokenize(fonte).map((t, i) => {
          const cls = classePorTipo[t.kind];
          return cls ? (
            <span key={i} className={cls}>{t.text}</span>
          ) : (
            <span key={i}>{t.text}</span>
          );
        })
      : realceSimples(fonte, lang);

  return (
    <figure className="group my-6 overflow-hidden rounded-xl border border-line bg-surface">
      <div className="flex items-center justify-between border-b border-line/70 bg-raised/50 px-4 py-2">
        <span className="font-mono text-[11.5px] uppercase tracking-[0.9px] text-muted">
          {title ?? (lang === 'df' ? 'dataforge' : lang)}
        </span>
        <button
          onClick={copiar}
          className="rounded-md px-2 py-1 text-[11.5px] font-medium text-muted transition-colors hover:bg-line/60 hover:text-strong"
          aria-label="Copiar código"
        >
          {copiado ? 'copiado' : 'copiar'}
        </button>
      </div>
      <pre className="overflow-x-auto px-4 py-4 text-[13.5px] leading-[22px]">
        <code className="font-mono">{conteudo}</code>
      </pre>
    </figure>
  );
}
