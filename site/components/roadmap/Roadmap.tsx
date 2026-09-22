'use client';

/**
 * A página `/roadmap`.
 *
 * Ela responde duas perguntas que a documentação, lida página a
 * página, não responde:
 *
 * 1. **Por onde eu começo, e o que vem depois?** — as sete trilhas.
 *    É a única parte escrita à mão aqui, porque a ordem em que vale a
 *    pena aprender as coisas é julgamento, e não dado. Os destinos,
 *    porém, são conferidos: `tests/test_roadmap.py` cobra que toda
 *    rota citada exista.
 *
 * 2. **O que esta linguagem É, por dentro?** — os três mapas em três
 *    dimensões, e todos os três saem de `roadmap-gerado.json`, que vem
 *    de `Arcane.Percurso` e `Arcane.Ecossistema`. Nenhum número aqui é
 *    escrito à mão.
 *
 * O mapa do ecossistema mostra **o que não existe** junto com o que
 * existe, e é isso que o separa de propaganda. Um roadmap que só lista
 * conquistas não ajuda ninguém a decidir se a linguagem serve para o
 * que a pessoa precisa fazer.
 */

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { Mapa3D, type Modo, type No } from './Mapa3D';
import { TRILHAS, type Trilha } from '@/lib/trilhas';
import dados from '@/lib/roadmap-gerado.json';

const MODOS: { id: Modo; rotulo: string; sub: string }[] = [
  { id: 'percurso', rotulo: 'O percurso', sub: 'as 10 fases de um arquivo' },
  { id: 'ecossistema', rotulo: 'O ecossistema', sub: '41 componentes, conferidos' },
  { id: 'biblioteca', rotulo: 'A biblioteca', sub: '83 módulos Arcane' },
];

const COR_DO_NIVEL: Record<Trilha['nivel'], string> = {
  início: 'bg-[#2fa96b]/12 text-[#2fa96b] border-[#2fa96b]/25',
  intermediário: 'bg-[#d9992a]/12 text-[#b8811f] border-[#d9992a]/25',
  avançado: 'bg-accent/10 text-accent border-accent/25',
};

/** Marca `crase` como <code>, que é como o resto do site escreve. */
function comCodigo(texto: string) {
  return texto.split(/(`[^`]+`)/g).map((parte, i) =>
    parte.startsWith('`') && parte.endsWith('`') ? (
      <code
        key={i}
        className="rounded bg-raised px-1 py-px text-[0.92em] text-strong"
      >
        {parte.slice(1, -1)}
      </code>
    ) : (
      <span key={i}>{parte}</span>
    ),
  );
}

export function Roadmap() {
  const [modo, setModo] = useState<Modo>('percurso');
  const [aberta, setAberta] = useState<string | null>('fundamentos');

  const nos: No[] = useMemo(() => {
    if (modo === 'percurso') {
      return dados.fases.map((f, i) => ({
        id: f.fase,
        rotulo: `${i + 1}. ${f.fase}`,
        grupo: 'percurso',
        detalhe: f.o_que_faz,
        onde: [f.modulo],
      }));
    }
    if (modo === 'ecossistema') {
      return dados.componentes.map((c) => ({
        id: `${c.grupo}/${c.no}`,
        rotulo: c.no,
        grupo: c.grupo,
        estado: c.estado,
        detalhe: c.o_que_e,
        nota: c.aqui || undefined,
        porque: c.porque || undefined,
        onde: c.onde,
      }));
    }
    return dados.modulos.flatMap((g) =>
      g.modulos.map((m) => ({
        id: m.chave,
        rotulo: m.nome.replace(/^Arcane\./, ''),
        grupo: g.rotulo,
        detalhe: m.desc,
        href: `/docs/biblioteca/${m.chave}`,
        peso: m.simbolos ?? 0,
      })),
    );
  }, [modo]);

  const n = dados.numeros;

  return (
    <main className="mx-auto w-full max-w-[1100px] px-4 py-10 sm:px-6 sm:py-14">
      {/* ── Cabeçalho ──────────────────────────────────────── */}
      <header className="mb-10">
        <p className="mb-2 text-[12.5px] font-semibold uppercase tracking-[0.14em] text-accent">
          Roadmap
        </p>
        <h1 className="text-[30px] font-bold leading-[1.15] tracking-tight text-strong sm:text-[38px]">
          O mapa da linguagem
        </h1>
        <p className="mt-4 max-w-[68ch] text-[15px] leading-[25px] text-body sm:text-[16px] sm:leading-[27px]">
          Duas perguntas que a documentação, lida página a página, não responde:{' '}
          <strong className="text-strong">por onde eu começo</strong> e{' '}
          <strong className="text-strong">o que esta linguagem é por dentro</strong>.
          Abaixo, sete trilhas e três mapas.
        </p>
        <p className="mt-3 max-w-[68ch] text-[14px] leading-[23px] text-muted">
          Os mapas mostram <strong className="text-strong">o que não existe</strong>{' '}
          junto com o que existe — e é isso que os separa de propaganda. Os números
          saem de <code className="rounded bg-raised px-1 py-px text-[0.92em]">Arcane.Ecossistema</code>,
          que confere cada componente contra o disco nas duas direções: o que o
          mapa cita e sumiu, e o módulo que existe e nenhum componente reivindica.
        </p>

        <dl className="mt-7 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {[
            { k: 'módulos', v: n.modulos },
            { k: 'símbolos', v: n.simbolos },
            { k: 'comandos', v: n.comandos },
            { k: 'componentes', v: n.componentes },
          ].map((c) => (
            <div key={c.k} className="rounded-xl border border-line bg-surface/50 px-4 py-3">
              <dt className="text-[12px] uppercase tracking-wide text-muted">{c.k}</dt>
              <dd className="mt-0.5 text-[22px] font-semibold tabular-nums text-strong">
                {c.v}
              </dd>
            </div>
          ))}
        </dl>
      </header>

      {/* ── Os três mapas ──────────────────────────────────── */}
      <section className="mb-14">
        <h2 className="mb-1 text-[22px] font-bold tracking-tight text-strong">
          A arquitetura, em três dimensões
        </h2>
        <p className="mb-5 max-w-[68ch] text-[14px] leading-[23px] text-muted">
          Arraste para girar, clique num ponto para abrir o que ele é. A posição de
          cada nó é determinística — a mesma peça fica sempre no mesmo lugar, porque
          um mapa que muda de forma a cada recarregamento não é um mapa.
        </p>

        <div
          className="mb-4 flex flex-wrap gap-2"
          role="tablist"
          aria-label="Qual mapa mostrar"
        >
          {MODOS.map((m) => (
            <button
              key={m.id}
              role="tab"
              aria-selected={modo === m.id}
              onClick={() => setModo(m.id)}
              className={`rounded-xl border px-3.5 py-2 text-left transition-colors ${
                modo === m.id
                  ? 'border-accent/40 bg-accent/10'
                  : 'border-line bg-surface/50 hover:bg-raised/60'
              }`}
            >
              <span
                className={`block text-[13.5px] font-semibold ${
                  modo === m.id ? 'text-accent' : 'text-strong'
                }`}
              >
                {m.rotulo}
              </span>
              <span className="block text-[11.5px] text-muted">{m.sub}</span>
            </button>
          ))}
        </div>

        <Mapa3D nos={nos} modo={modo} />
      </section>

      {/* ── O que não existe ───────────────────────────────── */}
      <section className="mb-14">
        <h2 className="mb-1 text-[22px] font-bold tracking-tight text-strong">
          O que não existe
        </h2>
        <p className="mb-5 max-w-[68ch] text-[14px] leading-[23px] text-muted">
          Esta lista sai de{' '}
          <code className="rounded bg-raised px-1 py-px text-[0.92em]">
            Arcane.Ecossistema.o_que_nao_existe()
          </code>
          , e por isso ela encolhe sozinha quando um item passa a existir. Escrita à
          mão, ela envelheceria exatamente no dia em que alguém implementasse um
          deles — e ninguém apaga a linha que diz que o próprio trabalho não estava
          feito.
        </p>

        <ul className="space-y-3">
          {dados.naoExiste.map((item) => (
            <li
              key={`${item.grupo}/${item.no}`}
              className="rounded-xl border border-line bg-surface/40 p-4"
            >
              <div className="flex flex-wrap items-baseline gap-x-3">
                <h3 className="text-[14.5px] font-semibold text-strong">{item.no}</h3>
                <span className="text-[12px] text-muted">{item.grupo}</span>
              </div>
              <p className="mt-1 text-[13.5px] leading-[21px] text-body">
                {item.o_que_e}
              </p>
              {item.aqui && (
                <p className="mt-1.5 text-[13.5px] leading-[21px] text-muted">
                  <strong className="text-strong">No lugar dele:</strong> {item.aqui}
                </p>
              )}
            </li>
          ))}
        </ul>
      </section>

      {/* ── As trilhas ─────────────────────────────────────── */}
      <section>
        <h2 className="mb-1 text-[22px] font-bold tracking-tight text-strong">
          As trilhas
        </h2>
        <p className="mb-6 max-w-[68ch] text-[14px] leading-[23px] text-muted">
          Cada passo diz o que você{' '}
          <strong className="text-strong">sabe fazer depois dele</strong>, e não o que
          ele contém — um índice já existe na barra lateral. Onde há exercícios do
          repositório que exercitam o assunto, eles estão ao lado.
        </p>

        <div className="space-y-3">
          {TRILHAS.map((t) => {
            const abertaAgora = aberta === t.id;
            return (
              <article
                key={t.id}
                className="overflow-hidden rounded-2xl border border-line bg-surface/40"
              >
                <button
                  onClick={() => setAberta(abertaAgora ? null : t.id)}
                  aria-expanded={abertaAgora}
                  className="flex w-full items-start gap-3 px-4 py-4 text-left transition-colors hover:bg-raised/40 sm:px-5"
                >
                  <span
                    className="mt-1 shrink-0 text-muted transition-transform"
                    style={{ transform: abertaAgora ? 'rotate(90deg)' : 'none' }}
                    aria-hidden="true"
                  >
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <path
                        d="M4 2l4 4-4 4"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </span>

                  <span className="min-w-0 flex-1">
                    <span className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
                      <span className="text-[16px] font-semibold text-strong">
                        {t.titulo}
                      </span>
                      <span
                        className={`rounded-full border px-2 py-0.5 text-[11px] font-medium ${COR_DO_NIVEL[t.nivel]}`}
                      >
                        {t.nivel}
                      </span>
                      <span className="text-[12px] text-muted">{t.duracao}</span>
                      <span className="text-[12px] text-muted">
                        {t.passos.length} passos
                      </span>
                    </span>
                    <span className="mt-1.5 block text-[13.5px] leading-[21px] text-body">
                      {t.resumo}
                    </span>
                    {t.antes.length > 0 && (
                      <span className="mt-1.5 block text-[12.5px] text-muted">
                        antes:{' '}
                        {t.antes
                          .map(
                            (id) => TRILHAS.find((o) => o.id === id)?.titulo ?? id,
                          )
                          .join(', ')}
                      </span>
                    )}
                  </span>
                </button>

                {abertaAgora && (
                  <ol className="border-t border-line/60 px-4 pb-4 pt-1 sm:px-5">
                    {t.passos.map((p, i) => (
                      <li
                        key={p.href + i}
                        className="flex gap-3 border-b border-line/40 py-3 last:border-b-0"
                      >
                        <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-line bg-raised/60 text-[11.5px] font-semibold tabular-nums text-muted">
                          {i + 1}
                        </span>
                        <div className="min-w-0 flex-1">
                          <Link
                            href={p.href}
                            className="text-[14px] font-semibold text-strong hover:text-accent"
                          >
                            {p.titulo}
                          </Link>
                          <p className="mt-0.5 text-[13px] leading-[20px] text-muted">
                            {comCodigo(p.ganho)}
                          </p>
                          {p.exercicios && (
                            <Link
                              href={p.exercicios}
                              className="mt-1 inline-block text-[12.5px] font-medium text-accent hover:underline"
                            >
                              exercícios →
                            </Link>
                          )}
                        </div>
                      </li>
                    ))}
                  </ol>
                )}
              </article>
            );
          })}
        </div>
      </section>

      <p className="mt-12 border-t border-line pt-6 text-[13px] leading-[21px] text-muted">
        As fases e os componentes desta página são gerados por{' '}
        <code className="rounded bg-raised px-1 py-px text-[0.92em]">
          site/scripts/gerar_roadmap.py
        </code>{' '}
        a partir do próprio código, e há teste comparando o arquivo versionado com o
        que o gerador produz. As trilhas são escritas à mão — e todo destino delas é
        conferido contra as rotas que existem.
      </p>
    </main>
  );
}
