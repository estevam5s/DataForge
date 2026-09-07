import Link from 'next/link';
import dados from '@/lib/dados-gerados.json';
import { Rotulo, TextoRevelado, Sobe } from './Primitivos';

type Modulo = { nome: string; desc: string; funcoes: { nome: string }[] };
const modulos = Object.entries(dados.modulos as Record<string, Modulo>);
const total = modulos.reduce((n, [, m]) => n + m.funcoes.length, 0);

/* Agrupada pelo que cada módulo serve, na ordem em que costuma ser usada. */
const grupos: { rotulo: string; chaves: string[] }[] = [
  { rotulo: 'Núcleo', chaves: ['math', 'text', 'io', 'regex', 'collections', 'functional'] },
  { rotulo: 'Dados', chaves: ['data', 'analytics', 'database', 'serialization', 'cortex'] },
  { rotulo: 'Sistema e rede', chaves: ['os', 'process', 'time', 'http', 'web', 'async'] },
  { rotulo: 'Qualidade', chaves: ['test', 'logging', 'crypto'] },
];

export function Arcane() {
  return (
    <section className="relative px-4 py-24 sm:px-10 sm:py-32">
      <div className="mx-auto max-w-[1280px]">
        <TextoRevelado
          texto="A biblioteca Arcane vem junto, e é feita só com a biblioteca padrão do Python."
          className="lp-h2 max-w-[24ch]"
        />
        <Sobe>
          <p className="lp-mono mt-7 max-w-[56ch] text-[13px] leading-[24px] text-white/60">
            {modulos.length} módulos, {total} símbolos, nenhum pacote a instalar.
            Cada nome abaixo tem página própria na documentação, com a assinatura
            extraída do código-fonte.
          </p>
        </Sobe>

        <div className="mt-16 space-y-14">
          {grupos.map((g) => {
            const doGrupo = g.chaves
              .map((c) => modulos.find(([k]) => k === c))
              .filter(Boolean) as [string, Modulo][];

            return (
              <div key={g.rotulo} className="grid gap-6 lg:grid-cols-[200px_minmax(0,1fr)]">
                <div className="lg:pt-6">
                  <Rotulo texto={String(doGrupo.length)} fecha />
                  <h3 className="mt-2 text-[19px] font-semibold sm:text-[20px]">{g.rotulo}</h3>
                </div>

                {/* grade de fio de cabelo, como a grade de patrocinadores do original */}
                <div className="grid grid-cols-2 border-l border-t border-[var(--lp-line)] sm:grid-cols-3">
                  {doGrupo.map(([chave, m]) => (
                    <Link
                      key={chave}
                      href={`/docs/biblioteca/${chave}`}
                      className="group border-b border-r border-[var(--lp-line)] p-5 transition-colors hover:bg-white/[.035]"
                    >
                      <p className="lp-mono text-[13px] font-medium text-white transition-colors group-hover:text-[var(--lp-warm)]">
                        {m.nome}
                      </p>
                      <p className="mt-2 text-[12.5px] leading-[19px] text-white/45">{m.desc}</p>
                      <p className="lp-mono mt-3 text-[11px] text-white/30">
                        {m.funcoes.length} símbolos
                      </p>
                    </Link>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        <Sobe className="mt-14">
          <Link href="/docs/biblioteca" className="lp-btn">
            Ver a biblioteca
          </Link>
        </Sobe>
      </div>
    </section>
  );
}
