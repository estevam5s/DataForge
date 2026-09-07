import Link from 'next/link';
import dados from '@/lib/dados-gerados.json';
import { Rotulo, Sobe } from './Primitivos';

const modulos = Object.entries(dados.exercicios as Record<string, unknown[]>);
const total = modulos.reduce((n, [, l]) => n + l.length, 0);

export function Aprender() {
  return (
    <section className="relative overflow-hidden px-4 py-28 text-center sm:px-10 sm:py-40">
      <div className="lp-bleed left-1/2 top-[62%] h-[300px] w-[min(880px,88vw)] -translate-x-1/2" aria-hidden />

      <div className="relative mx-auto max-w-[1280px]">
        <Sobe>
          <Rotulo texto="APRENDER FAZENDO" className="justify-center" />
        </Sobe>

        <h2 className="lp-h1 mx-auto mt-6 max-w-[14ch] font-medium">
          {total} exercícios que rodam
        </h2>

        <Sobe atraso={80}>
          <p className="lp-mono mx-auto mt-8 max-w-[60ch] text-[14px] leading-[26px] text-white/65">
            Divididos em {modulos.length} módulos, do primeiro <span className="text-white">out</span> até
            escrever um interpretador. Cada um termina com um{' '}
            <span className="text-white">assert</span> — e a suíte inteira roda a cada
            mudança na linguagem, então nenhum deles pode apodrecer.
          </p>
        </Sobe>

        <Sobe atraso={140}>
          <div className="mt-12 flex flex-wrap items-center justify-center gap-3">
            <Link href="/docs/exercicios" className="lp-btn">
              Ver os exercícios
            </Link>
            <Link href="/docs/receitas/interpretador" className="lp-btn-ghost">
              Receita: um interpretador
            </Link>
          </div>
        </Sobe>

        <Sobe atraso={200}>
          <div className="lp-mono mx-auto mt-16 grid max-w-[760px] grid-cols-2 gap-px overflow-hidden rounded-2xl border border-[var(--lp-line)] bg-[var(--lp-line)] sm:grid-cols-4">
            {[
              ['240', 'testes'],
              ['180', 'exercícios'],
              ['42', 'exemplos'],
              ['225', 'arquivos .df'],
            ].map(([n, r]) => (
              <div key={r} className="bg-[var(--lp-bg)] px-4 py-7">
                <p className="text-[26px] font-medium text-white sm:text-[30px]">{n}</p>
                <p className="mt-1 text-[11px] tracking-[1.2px] text-white/40">{r}</p>
              </div>
            ))}
          </div>
          <p className="lp-mono mt-4 text-[11.5px] text-white/30">
            números conferidos na última execução da suíte
          </p>
        </Sobe>
      </div>
    </section>
  );
}
