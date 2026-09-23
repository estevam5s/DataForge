'use client';

import Link from 'next/link';
import { useState } from 'react';
import dados from '@/lib/dados-gerados.json';
import { Contagem } from './Contagem';

/* Os números saem do repositório, e não daqui.
 *
 * Estavam escritos à mão — '2332' quando eram 2377, e antes disso
 * '1246' quando eram 2304 — sob um comentário que prometia uma trava.
 * Um comentário que promete verificação que não existe é pior que
 * nenhum: quem lê confia e não confere.
 *
 * Hoje vêm de 'site/scripts/gerar_dados.py', que conta o repositório,
 * e 'test_a_home_anuncia_os_numeros_reais' cobra a sincronia. */
const contagem = (dados as unknown as {
  contagem: { testes: number; exemplos: number; arquivosDf: number };
}).contagem;

const totalExercicios = Object.values(
  dados.exercicios as Record<string, unknown[]>,
).reduce((n, l) => n + l.length, 0);

const COMANDO = 'curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh';

/** Os quatro lugares onde o release é construído e testado. */
const PLATAFORMAS = ['macOS', 'Linux', 'Windows', 'Docker'];

export function Heroi() {
  const [copiado, setCopiado] = useState(false);

  async function copiar() {
    try {
      await navigator.clipboard.writeText(COMANDO);
      setCopiado(true);
      window.setTimeout(() => setCopiado(false), 1800);
    } catch {
      /* Sem área de transferência (http, permissão negada): o comando
         continua visível e selecionável, que é o que importa. */
    }
  }

  return (
    <header>
      {/* A barra NAO mora aqui. Um 'position: sticky' so gruda dentro
          da caixa do pai: dentro deste <header> ela ia ate o fim do
          hero e sumia no resto da pagina. Ela e irma do hero, filha
          direta de '.lp' — e e por isso que o seletor
          '.lp > .lp-barra' do globals.css existe. */}
      <div className="px-4 pb-4 sm:px-10 sm:pb-10">
        <div className="lp-noise lp-hero-glow relative isolate overflow-hidden rounded-[28px] px-6 pb-14 pt-16 sm:rounded-[40px] sm:px-10 sm:pb-16 sm:pt-24 lg:pb-20 lg:pt-28">
        <div className="relative z-10 mx-auto max-w-[1280px]">
          {/* O selo: o que mudou por último, com para onde ir. Ele é um
              link de verdade — um selo decorativo é ruído. */}
          <div className="flex justify-center">
            <Link
              href="/docs/versoes"
              className="lp-mono group inline-flex items-center gap-2.5 rounded-full border border-white/15 bg-white/[0.06] py-1.5 pl-2 pr-4 text-[12px] text-white/75 backdrop-blur-sm transition-colors hover:border-white/30 hover:text-white"
            >
              <span className="rounded-full bg-white px-2.5 py-0.5 text-[11px] font-bold text-black">
                v{dados.versaoDaLinguagem}
              </span>
              109 rotas novas de documentação
              <span aria-hidden className="transition-transform group-hover:translate-x-0.5">→</span>
            </Link>
          </div>

          <h1 className="lp-h1 mx-auto mt-7 max-w-[15ch] text-center text-white">
            Mais que uma sintaxe diferente
          </h1>

          <p className="lp-mono mx-auto mt-8 max-w-[62ch] text-center text-[14px] leading-[24px] text-white/75 sm:text-[15px] sm:leading-[26px]">
            DataForge é uma linguagem interpretada de propósito geral, com lexer,
            parser, analisador estático e interpretador próprios — escritos em
            Python, sem uma única dependência externa em tempo de execução.
          </p>

          <div className="mt-10 flex flex-col items-center gap-4">
            <div className="flex items-center gap-2 sm:gap-4">
              <Link href="/docs/primeiros-passos" className="lp-btn">
                Começar
              </Link>
              <Link href="/download" className="lp-btn-ghost">
                Instalar
              </Link>
            </div>

            {/* O comando embaixo do botão: quem já decidiu instalar não
                deveria precisar abrir outra página para copiar uma linha. */}
            <div className="flex w-full max-w-[min(100%,560px)] items-center gap-2 rounded-full border border-white/12 bg-black/35 py-1.5 pl-4 pr-1.5 backdrop-blur-sm">
              <code className="lp-mono flex-1 truncate text-left text-[12px] text-white/70 sm:text-[13px]">
                <span className="text-[var(--lp-warm)]">$</span> {COMANDO}
              </code>
              <button
                type="button"
                onClick={copiar}
                className="lp-mono shrink-0 rounded-full bg-white/10 px-3 py-1.5 text-[11px] font-bold uppercase tracking-wide text-white transition-colors hover:bg-white/20"
              >
                {copiado ? 'copiado' : 'copiar'}
              </button>
            </div>
          </div>

          {/* A prova social de um site de produto são rostos de clientes.
              Aqui não há clientes para mostrar, e inventá-los seria
              mentira: o que existe é onde o release é construído e
              testado, em cada tag, nas quatro plataformas. */}
          <div className="mt-10 flex flex-col items-center gap-3">
            <div className="flex -space-x-2" aria-hidden>
              {PLATAFORMAS.map((p) => (
                <span
                  key={p}
                  title={p}
                  className="lp-mono grid h-9 w-9 place-items-center rounded-full border-2 border-black/60 bg-[var(--lp-raised)] text-[11px] font-bold text-white/80"
                >
                  {p.slice(0, 2)}
                </span>
              ))}
            </div>
            <p className="lp-mono text-center text-[12.5px] text-white/55">
              Construída e testada em {PLATAFORMAS.join(', ')} a cada versão —{' '}
              <Link href="/download" className="text-white/80 underline-offset-4 hover:underline">
                binário para os quatro
              </Link>
            </p>
          </div>

          <dl className="lp-mono mx-auto mt-12 grid max-w-[720px] grid-cols-1 gap-px overflow-hidden rounded-2xl border border-white/10 bg-white/[0.06] text-[13px] sm:grid-cols-3">
            {/* 'Funções de teste', e nao 'Testes passando'. O gerador
                conta os 'def test_' do repositorio; o pytest reporta
                mais CASOS, porque 'parametrize' expande uma funcao em
                varios. Os dois numeros sao verdadeiros e diferentes —
                e o rotulo tem de dizer qual deles esta ali. */}
            <div className="bg-black/30 px-5 py-4 text-center">
              <dt className="text-white/55">Funções de teste</dt>
              <dd className="mt-1 text-[20px] font-medium text-white">
                <Contagem valor={contagem.testes} />
              </dd>
            </div>
            <div className="bg-black/30 px-5 py-4 text-center">
              <dt className="text-white/55">Exercícios verificados</dt>
              <dd className="mt-1 text-[20px] font-medium text-white">
                <Contagem valor={totalExercicios} duracao={900} />
              </dd>
            </div>
            <div className="bg-black/30 px-5 py-4 text-center">
              <dt className="text-white/55">Dependências no runtime</dt>
              <dd className="mt-1 text-[20px] font-medium text-white">nenhuma</dd>
            </div>
          </dl>
        </div>
        </div>
      </div>
    </header>
  );
}
