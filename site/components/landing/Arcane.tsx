import Link from 'next/link';
import dados from '@/lib/dados-gerados.json';
import { Rotulo, TextoRevelado, Sobe } from './Primitivos';

type Modulo = { nome: string; desc: string; funcoes: { nome: string }[] };
const modulos = Object.entries(dados.modulos as Record<string, Modulo>);
const total = modulos.reduce((n, [, m]) => n + m.funcoes.length, 0);

/* Agrupada pelo que cada módulo serve, na ordem em que costuma ser usada.
 *
 * A lista é escrita à mão de propósito — a ordem e o agrupamento são
 * julgamento, e nenhum gerador os adivinha. O preço de uma lista à mão
 * é envelhecer: um módulo novo que ninguém acrescentasse aqui SUMIRIA
 * da página, sem erro e sem aviso, e a seção continuaria dizendo o
 * total certo logo acima.
 *
 * Por isso o que sobra cai em 'Outros' (abaixo), e
 * 'test_a_landing_nao_engole_nenhum_modulo_da_arcane' reprova a
 * suíte enquanto ele estiver lá: aparecer no lugar errado é ruim,
 * desaparecer é pior. */
const grupos: { rotulo: string; chaves: string[] }[] = [
  { rotulo: 'Núcleo', chaves: ['math', 'text', 'io', 'regex', 'collections', 'functional', 'iter', 'decimal', 'bytes'] },
  { rotulo: 'Frameworks', chaves: ['kiln', 'vitrine', 'lavra', 'crucible', 'forge', 'api'] },
  { rotulo: 'Dados', chaves: ['quadro', 'data', 'analytics', 'cortex', 'lago', 'pipeline', 'qualidade', 'stream'] },
  { rotulo: 'Formatos', chaves: ['serialization', 'excel', 'archive', 'database', 'html'] },
  { rotulo: 'Sistema e rede', chaves: ['os', 'process', 'time', 'http', 'web', 'async', 'concurrent', 'ponte', 'malha', 'rede', 'email', 'url'] },
  { rotulo: 'Qualidade', chaves: ['test', 'bench', 'logging', 'crypto', 'observar', 'color', 'meta', 'cli', 'eventos'] },
  { rotulo: 'Objetos', chaves: ['reflexo', 'objetos', 'injecao', 'padroes'] },
  { rotulo: 'Tipos', chaves: ['tipos', 'resultado'] },
  { rotulo: 'Memória', chaves: ['posse', 'memoria'] },
  { rotulo: 'Transacional', chaves: ['stm'] },
  { rotulo: 'Metaprogramação', chaves: ['macro', 'dsl'] },
  { rotulo: 'Nativo', chaves: ['c'] },
  { rotulo: 'Compilador', chaves: ['compilador'] },
  { rotulo: 'Runtime', chaves: ['laco'] },
  { rotulo: 'Perfil', chaves: ['perfil'] },
  { rotulo: 'Partida', chaves: ['inicio', 'capacidade'] },
];

/** O que nenhum grupo reivindicou. Vazio é o estado esperado. */
const sobrando = modulos
  .map(([k]) => k)
  .filter((k) => !grupos.some((g) => g.chaves.includes(k)));

const todosOsGrupos = sobrando.length
  ? [...grupos, { rotulo: 'Outros', chaves: sobrando }]
  : grupos;

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
            {modulos.length} módulos, {total} símbolos, nenhum pacote a instalar
            e nenhuma dependência em tempo de execução. Cada nome abaixo tem
            página própria na documentação, com a assinatura extraída do
            código-fonte — e os mesmos dados estão em{' '}
            <Link href="/api" className="text-white/75 underline-offset-2 hover:underline">
              /api/modulos.json
            </Link>
            , se você quiser gerar algo a partir deles.
          </p>
        </Sobe>

        <div className="mt-16 space-y-14">
          {todosOsGrupos.map((g) => {
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
