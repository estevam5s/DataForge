'use client';

import { useEffect, useRef, useState } from 'react';
import { classePorTipo, tokenize } from '@/lib/highlight';

/**
 * Editor de DataForge com realce de sintaxe.
 *
 * A técnica é um `<textarea>` transparente sobre um `<pre>` colorido,
 * alinhados ao pixel. Um editor de verdade (CodeMirror, Monaco) traria
 * 300 KB e uma segunda gramática para manter em dia — aqui o realce sai
 * do mesmo `lib/highlight.ts` que colore a documentação, então o código
 * na prática fica igual ao código nos exemplos.
 *
 * O que ele faz além do básico: Tab insere quatro espaços (a linguagem
 * recusa tab), Enter mantém a indentação e aprofunda depois de `:`, e a
 * numeração das linhas acompanha a rolagem.
 */
export function Editor({
  valor,
  aoMudar,
  aoExecutar,
  altura = 320,
  somenteLeitura = false,
}: {
  valor: string;
  aoMudar: (v: string) => void;
  aoExecutar?: () => void;
  altura?: number;
  somenteLeitura?: boolean;
}) {
  const area = useRef<HTMLTextAreaElement>(null);
  const pintado = useRef<HTMLPreElement>(null);
  const numeros = useRef<HTMLDivElement>(null);
  const [linhaAtual, setLinhaAtual] = useState(1);

  const linhas = valor.split('\n');

  // O <pre> e a numeração seguem a rolagem do textarea.
  const sincronizar = () => {
    if (!area.current) return;
    const { scrollTop, scrollLeft } = area.current;
    if (pintado.current) {
      pintado.current.scrollTop = scrollTop;
      pintado.current.scrollLeft = scrollLeft;
    }
    if (numeros.current) numeros.current.scrollTop = scrollTop;
  };

  useEffect(sincronizar, [valor]);

  const aoDigitar = (evento: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const alvo = evento.currentTarget;

    // Ctrl/Cmd + Enter executa — o atalho que todo mundo tenta primeiro.
    if (evento.key === 'Enter' && (evento.metaKey || evento.ctrlKey)) {
      evento.preventDefault();
      aoExecutar?.();
      return;
    }

    if (evento.key === 'Tab') {
      evento.preventDefault();
      const { selectionStart: inicio, selectionEnd: fim } = alvo;

      if (evento.shiftKey) {
        // Shift+Tab remove um nível da linha atual.
        const comecoLinha = valor.lastIndexOf('\n', inicio - 1) + 1;
        if (valor.slice(comecoLinha, comecoLinha + 4) === '    ') {
          const novo = valor.slice(0, comecoLinha) + valor.slice(comecoLinha + 4);
          aoMudar(novo);
          requestAnimationFrame(() => {
            alvo.selectionStart = alvo.selectionEnd = Math.max(comecoLinha, inicio - 4);
          });
        }
        return;
      }

      // Quatro espaços, nunca um tab: a linguagem recusa tab com SyncError.
      const novo = valor.slice(0, inicio) + '    ' + valor.slice(fim);
      aoMudar(novo);
      requestAnimationFrame(() => {
        alvo.selectionStart = alvo.selectionEnd = inicio + 4;
      });
      return;
    }

    if (evento.key === 'Enter') {
      const inicio = alvo.selectionStart;
      const comecoLinha = valor.lastIndexOf('\n', inicio - 1) + 1;
      const linha = valor.slice(comecoLinha, inicio);
      const recuo = linha.match(/^[ ]*/)?.[0] ?? '';
      // Uma linha terminada em ':' abre um bloco: a próxima entra um nível.
      const aprofunda = linha.trimEnd().endsWith(':') ? '    ' : '';

      if (recuo || aprofunda) {
        evento.preventDefault();
        const novo =
          valor.slice(0, inicio) + '\n' + recuo + aprofunda + valor.slice(alvo.selectionEnd);
        aoMudar(novo);
        const posicao = inicio + 1 + recuo.length + aprofunda.length;
        requestAnimationFrame(() => {
          alvo.selectionStart = alvo.selectionEnd = posicao;
        });
      }
    }
  };

  const aoMoverCursor = () => {
    if (!area.current) return;
    const antes = valor.slice(0, area.current.selectionStart);
    setLinhaAtual(antes.split('\n').length);
  };

  return (
    <div
      className="relative overflow-hidden rounded-xl border border-line bg-[#0d0d10] font-mono text-[13.5px] leading-[22px]"
      style={{ height: altura }}
    >
      <div className="flex h-full">
        {/* Numeração */}
        <div
          ref={numeros}
          className="w-[46px] shrink-0 overflow-hidden border-r border-line/60 bg-black/25 py-3 text-right"
          aria-hidden="true"
        >
          {linhas.map((_, i) => (
            <div
              key={i}
              className={`pr-2.5 tabular-nums transition-colors ${
                i + 1 === linhaAtual ? 'text-accent' : 'text-muted/45'
              }`}
            >
              {i + 1}
            </div>
          ))}
        </div>

        <div className="relative min-w-0 flex-1">
          {/* Camada colorida */}
          <pre
            ref={pintado}
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 overflow-auto whitespace-pre px-3 py-3 [scrollbar-width:none] [&::-webkit-scrollbar]{display:none}"
          >
            {tokenize(valor).map((t, i) => (
              <span key={i} className={classePorTipo[t.kind]}>
                {t.text}
              </span>
            ))}
            {'\n'}
          </pre>

          {/* Camada de digitação, transparente por cima */}
          <textarea
            ref={area}
            value={valor}
            onChange={(e) => aoMudar(e.target.value)}
            onKeyDown={aoDigitar}
            onKeyUp={aoMoverCursor}
            onClick={aoMoverCursor}
            onScroll={sincronizar}
            readOnly={somenteLeitura}
            spellCheck={false}
            autoCapitalize="off"
            autoCorrect="off"
            className="absolute inset-0 resize-none overflow-auto whitespace-pre bg-transparent px-3 py-3 text-transparent caret-accent outline-none [scrollbar-width:thin]"
            aria-label="Editor de código DataForge"
          />
        </div>
      </div>
    </div>
  );
}
