'use client';

import { useState } from 'react';
import { tokenize, classePorTipo } from '@/lib/highlight';

type Props = {
  code: string;
  /** 'df' realça DataForge; 'bash'/'powershell', 'toml', 'json' e 'text' têm tratamento próprio. */
  lang?: 'df' | 'bash' | 'powershell' | 'toml' | 'json' | 'text' | 'sql' | 'javascript' | 'yaml';
  /** Rótulo exibido no topo do bloco — normalmente o nome do arquivo. */
  title?: string;
};

/** Realce leve para linguagens que não são DataForge. */
function realceSimples(code: string, lang: string) {
  if (lang === 'bash' || lang === 'powershell') {
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
  if (lang === 'sql') {
    // Só as palavras-chave e as strings. Um realce completo de SQL
    // seria um segundo destacador para manter em dia, e o que importa
    // num bloco de documentação é distinguir o comando do dado.
    const chaves = /\b(SELECT|FROM|WHERE|JOIN|LEFT|INNER|OUTER|ON|GROUP|ORDER|BY|HAVING|LIMIT|OFFSET|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|INDEX|VIRTUAL|USING|DROP|ALTER|ADD|COLUMN|PRIMARY|KEY|FOREIGN|REFERENCES|UNIQUE|NOT|NULL|DEFAULT|CHECK|AND|OR|IN|LIKE|MATCH|AS|ASC|DESC|COALESCE|SUM|COUNT|AVG|MIN|MAX|CASE|WHEN|THEN|ELSE|END|PRAGMA|BEGIN|COMMIT|ROLLBACK|SAVEPOINT|CONFLICT|DO|NOTHING|EXCLUDED|RANK)\b/g;
    return code.split('\n').map((linha, i) => {
      const comentario = linha.indexOf('--');
      const corpo = comentario >= 0 ? linha.slice(0, comentario) : linha;
      const resto = comentario >= 0 ? linha.slice(comentario) : '';
      const html = corpo
        .replace(/'([^']*)'/g, '\u0001$1\u0002')
        .replace(chaves, '\u0003$&\u0004');
      return (
        <span key={i}>
          {html.split(/([\u0001-\u0004])/).reduce<React.ReactNode[]>((acc, p, k, todos) => {
            if (p === '\u0001' || p === '\u0003') return acc;
            if (p === '\u0002' || p === '\u0004') return acc;
            const antes = todos[k - 1];
            if (antes === '\u0001') acc.push(<span key={k} className="tk-string">{`'${p}'`}</span>);
            else if (antes === '\u0003') acc.push(<span key={k} className="tk-keyword">{p}</span>);
            else acc.push(p);
            return acc;
          }, [])}
          {resto && <span className="tk-comment">{resto}</span>}
          {'\n'}
        </span>
      );
    });
  }
  if (lang === 'javascript') {
    const chaves = /\b(const|let|var|function|return|if|else|for|while|new|await|async|class|import|export|from|=>)\b/g;
    return code.split('\n').map((linha, i) => {
      const comentario = linha.indexOf('//');
      const corpo = comentario >= 0 ? linha.slice(0, comentario) : linha;
      const resto = comentario >= 0 ? linha.slice(comentario) : '';
      const partes = corpo.split(chaves);
      return (
        <span key={i}>
          {partes.map((p, k) =>
            chaves.test(p) && p.trim()
              ? <span key={k} className="tk-keyword">{p}</span>
              : <span key={k}>{p}</span>
          )}
          {resto && <span className="tk-comment">{resto}</span>}
          {'\n'}
        </span>
      );
    });
  }
  if (lang === 'yaml') {
    return code.split('\n').map((linha, i) => {
      if (linha.trim().startsWith('#')) {
        return <span key={i}><span className="tk-comment">{linha}</span>{'\n'}</span>;
      }
      const dois = linha.indexOf(':');
      if (dois < 0) return <span key={i}>{linha}{'\n'}</span>;
      return (
        <span key={i}>
          <span className="tk-property">{linha.slice(0, dois)}</span>
          <span className="tk-operator">:</span>
          <span className="tk-string">{linha.slice(dois + 1)}</span>
          {'\n'}
        </span>
      );
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
