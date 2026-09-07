'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { Cabecalho, Icone } from '@/components/painel/Casca';
import { Editor } from '@/components/painel/Editor';
import { corrigir, prepararRuntime, rodar, type Correcao } from '@/lib/runtime';
import {
  buscarSolucao, listarProblemas, listarResolucoes, registrarSubmissao,
  type Dificuldade, type Problema, type Resolucao,
} from '@/lib/supabase/pratica';
import { useAuth } from '@/lib/supabase/auth';

const CORES_DIFICULDADE: Record<Dificuldade, string> = {
  facil: 'text-emerald-400 bg-emerald-400/10',
  medio: 'text-amber-400 bg-amber-400/10',
  dificil: 'text-accent bg-accent/10',
};

const ROTULO_DIFICULDADE: Record<Dificuldade, string> = {
  facil: 'Fácil',
  medio: 'Médio',
  dificil: 'Difícil',
};

/** Como o resultado de cada caso aparece na lista. */
function valorLegivel(valor: unknown): string {
  if (valor === undefined) return '—';
  if (typeof valor === 'string') return JSON.stringify(valor);
  return JSON.stringify(valor) ?? String(valor);
}

export default function Praticar() {
  const { demonstracao } = useAuth();

  const [problemas, setProblemas] = useState<Problema[]>([]);
  const [resolucoes, setResolucoes] = useState<Resolucao[]>([]);
  const [atual, setAtual] = useState<Problema | null>(null);
  const [codigo, setCodigo] = useState('');
  const [carregando, setCarregando] = useState(true);

  const [runtime, setRuntime] = useState<'frio' | 'aquecendo' | 'pronto' | 'erro'>('frio');
  const [etapa, setEtapa] = useState('');
  const [rodando, setRodando] = useState(false);
  const [correcao, setCorrecao] = useState<Correcao | null>(null);
  const [saidaLivre, setSaidaLivre] = useState<string | null>(null);
  const [dicasAbertas, setDicasAbertas] = useState(false);
  const [solucao, setSolucao] = useState<string | null>(null);

  const [filtro, setFiltro] = useState<'todos' | Dificuldade>('todos');
  const [busca, setBusca] = useState('');

  useEffect(() => {
    (async () => {
      const [p, r] = await Promise.all([listarProblemas(), listarResolucoes()]);
      setProblemas(p.dados);
      setResolucoes(r.dados);
      setCarregando(false);
      if (p.dados[0]) escolher(p.dados[0]);
    })();
    // escolher é estável o bastante para o primeiro carregamento
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const escolher = (p: Problema) => {
    setAtual(p);
    setCodigo(`${p.assinatura}\n    `);
    setCorrecao(null);
    setSaidaLivre(null);
    setSolucao(null);
    setDicasAbertas(false);
  };

  /** Aquece o interpretador. São ~4 s, uma vez por sessão. */
  const aquecer = useCallback(async () => {
    if (runtime === 'pronto' || runtime === 'aquecendo') return;
    setRuntime('aquecendo');
    try {
      await prepararRuntime(setEtapa);
      setRuntime('pronto');
    } catch (erro) {
      setRuntime('erro');
      setEtapa(erro instanceof Error ? erro.message : 'falhou');
    }
  }, [runtime]);

  const executar = async () => {
    if (!atual) return;
    setRodando(true);
    setCorrecao(null);
    setSaidaLivre(null);
    try {
      await aquecer();
      const resultado = await corrigir(codigo, atual.casos);
      setCorrecao(resultado);

      const erro = await registrarSubmissao({
        problemaId: atual.id,
        codigo,
        estado: resultado.estado,
        testesOk: resultado.passaram,
        testesTotal: resultado.total,
        duracaoMs: resultado.duracaoMs,
        detalhe: resultado.detalhe,
      });

      if (!erro && resultado.estado === 'aceito') {
        // Recarrega o resumo para a lista mostrar o problema resolvido.
        const r = await listarResolucoes();
        setResolucoes(r.dados);
      }
    } finally {
      setRodando(false);
    }
  };

  const soRodar = async () => {
    setRodando(true);
    setCorrecao(null);
    try {
      await aquecer();
      const r = await rodar(codigo);
      setSaidaLivre(r.erro ? r.erro : r.saida || '(sem saída)');
    } finally {
      setRodando(false);
    }
  };

  const revelarSolucao = async () => {
    if (!atual) return;
    const { dados } = await buscarSolucao(atual.id);
    setSolucao(dados);
  };

  const resolvidos = useMemo(
    () => new Set(resolucoes.filter((r) => r.resolvido).map((r) => r.problema_id)),
    [resolucoes]
  );

  const visiveis = useMemo(
    () =>
      problemas.filter(
        (p) =>
          (filtro === 'todos' || p.dificuldade === filtro) &&
          (busca === '' ||
            p.titulo.toLowerCase().includes(busca.toLowerCase()) ||
            p.categoria.includes(busca.toLowerCase()))
      ),
    [problemas, filtro, busca]
  );

  if (carregando) {
    return (
      <>
        <Cabecalho titulo="Praticar" descricao="Carregando os problemas…" />
        <div className="h-64 animate-pulse rounded-xl border border-line bg-raised/30" />
      </>
    );
  }

  return (
    <>
      <Cabecalho
        titulo="Praticar"
        descricao={`${resolvidos.size} de ${problemas.length} resolvidos. O código roda no seu navegador, com o interpretador de verdade.`}
      />

      <div className="grid gap-5 lg:grid-cols-[300px_1fr]">
        {/* ── Lista de problemas ── */}
        <aside className="space-y-3">
          <input
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Buscar…"
            className="w-full rounded-xl border border-line bg-raised/40 px-3 py-2 text-[13.5px] outline-none transition-colors placeholder:text-muted focus:border-accent/50"
          />

          <div className="flex gap-1">
            {(['todos', 'facil', 'medio', 'dificil'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFiltro(f)}
                className={`flex-1 rounded-lg px-2 py-1.5 text-[12px] font-semibold transition-colors ${
                  filtro === f
                    ? 'bg-accent text-white'
                    : 'bg-raised/50 text-muted hover:text-strong'
                }`}
              >
                {f === 'todos' ? 'Todos' : ROTULO_DIFICULDADE[f]}
              </button>
            ))}
          </div>

          <ul className="max-h-[560px] space-y-1 overflow-y-auto pr-1">
            {visiveis.map((p) => {
              const feito = resolvidos.has(p.id);
              const ativo = atual?.id === p.id;
              return (
                <li key={p.id}>
                  <button
                    onClick={() => escolher(p)}
                    className={`w-full rounded-xl border px-3 py-2.5 text-left transition-all ${
                      ativo
                        ? 'border-accent/50 bg-accent/10'
                        : 'border-line bg-raised/25 hover:border-line hover:bg-raised/60'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <span
                        className={`text-[13.5px] font-medium ${
                          ativo ? 'text-accent' : 'text-strong'
                        }`}
                      >
                        {p.titulo}
                      </span>
                      {feito && (
                        <span className="mt-0.5 shrink-0 text-emerald-400" title="resolvido">
                          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                            <path
                              d="M3 8.5l3.5 3.5L13 5"
                              stroke="currentColor"
                              strokeWidth="2.2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                        </span>
                      )}
                    </div>
                    <div className="mt-1 flex items-center gap-2">
                      <span
                        className={`rounded px-1.5 py-px text-[10px] font-bold uppercase ${
                          CORES_DIFICULDADE[p.dificuldade]
                        }`}
                      >
                        {ROTULO_DIFICULDADE[p.dificuldade]}
                      </span>
                      <span className="text-[11.5px] text-muted">{p.categoria}</span>
                    </div>
                  </button>
                </li>
              );
            })}
          </ul>
        </aside>

        {/* ── Problema e editor ── */}
        {atual && (
          <section className="min-w-0 space-y-4">
            <div className="rounded-xl border border-line bg-raised/25 p-5">
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <h2 className="text-[20px] font-bold text-strong">{atual.titulo}</h2>
                <span
                  className={`rounded px-2 py-0.5 text-[11px] font-bold uppercase ${
                    CORES_DIFICULDADE[atual.dificuldade]
                  }`}
                >
                  {ROTULO_DIFICULDADE[atual.dificuldade]}
                </span>
                {resolvidos.has(atual.id) && (
                  <span className="rounded bg-emerald-400/10 px-2 py-0.5 text-[11px] font-bold uppercase text-emerald-400">
                    resolvido
                  </span>
                )}
              </div>

              {atual.enunciado.split('\n\n').map((paragrafo, i) => (
                <p key={i} className="mb-2.5 text-[14.5px] leading-[24px] text-body last:mb-0">
                  {paragrafo}
                </p>
              ))}

              {atual.exemplos.length > 0 && (
                <div className="mt-4 space-y-2">
                  {atual.exemplos.map((ex, i) => (
                    <div
                      key={i}
                      className="rounded-lg border border-line/70 bg-black/25 px-3 py-2 font-mono text-[12.5px]"
                    >
                      <span className="text-muted">entrada </span>
                      <span className="text-body">{ex.entrada}</span>
                      <span className="mx-2 text-muted">→</span>
                      <span className="text-accent">{ex.saida}</span>
                    </div>
                  ))}
                </div>
              )}

              {atual.dicas.length > 0 && (
                <div className="mt-4">
                  <button
                    onClick={() => setDicasAbertas((v) => !v)}
                    className="text-[13px] font-semibold text-muted transition-colors hover:text-strong"
                  >
                    {dicasAbertas ? '− esconder' : '+ mostrar'} {atual.dicas.length} dica
                    {atual.dicas.length > 1 ? 's' : ''}
                  </button>
                  {dicasAbertas && (
                    <ul className="mt-2 space-y-1.5">
                      {atual.dicas.map((d, i) => (
                        <li key={i} className="text-[13.5px] leading-[22px] text-muted">
                          <span className="mr-1.5 text-accent">·</span>
                          {d}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>

            <Editor valor={codigo} aoMudar={setCodigo} aoExecutar={executar} altura={300} />

            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={executar}
                disabled={rodando}
                className="rounded-xl bg-accent px-5 py-2.5 text-[14px] font-bold text-white transition-all hover:bg-accent-soft disabled:opacity-50"
              >
                {rodando ? 'Rodando…' : 'Enviar solução'}
              </button>
              <button
                onClick={soRodar}
                disabled={rodando}
                className="rounded-xl border border-line px-4 py-2.5 text-[14px] font-semibold text-body transition-colors hover:bg-raised hover:text-strong disabled:opacity-50"
              >
                Só rodar
              </button>
              <span className="text-[12px] text-muted">⌘/Ctrl + Enter</span>

              <button
                onClick={revelarSolucao}
                className="ml-auto text-[13px] text-muted transition-colors hover:text-strong"
              >
                ver solução
              </button>
            </div>

            {runtime === 'aquecendo' && (
              <div className="flex items-center gap-2.5 rounded-xl border border-line bg-raised/30 px-4 py-3 text-[13.5px] text-muted">
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-accent border-t-transparent" />
                {etapa} <span className="text-muted/70">— só na primeira vez</span>
              </div>
            )}

            {runtime === 'erro' && (
              <div className="rounded-xl border border-accent/40 bg-accent/8 px-4 py-3 text-[13.5px]">
                <strong className="text-strong">Não consegui carregar o interpretador.</strong>{' '}
                <span className="text-muted">{etapa}</span>
              </div>
            )}

            {saidaLivre !== null && (
              <div className="rounded-xl border border-line bg-black/30 p-4">
                <p className="mb-2 text-[11px] font-bold uppercase tracking-wide text-muted">
                  Saída
                </p>
                <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-[12.5px] leading-[20px] text-body">
                  {saidaLivre}
                </pre>
              </div>
            )}

            {correcao && <Resultado correcao={correcao} />}

            {solucao && (
              <div className="rounded-xl border border-line bg-raised/25 p-4">
                <p className="mb-2 text-[11px] font-bold uppercase tracking-wide text-muted">
                  Solução de referência
                </p>
                <Editor valor={solucao} aoMudar={() => {}} altura={180} somenteLeitura />
                <button
                  onClick={() => setCodigo(solucao)}
                  className="mt-2 text-[13px] text-accent transition-colors hover:text-accent-soft"
                >
                  copiar para o editor
                </button>
              </div>
            )}

            {demonstracao && (
              <p className="text-[12.5px] text-muted">
                Modo demonstração: a correção funciona, mas o resultado não é gravado.
              </p>
            )}
          </section>
        )}
      </div>
    </>
  );
}

function Resultado({ correcao }: { correcao: Correcao }) {
  const aceito = correcao.estado === 'aceito';

  const titulo = {
    aceito: 'Aceito',
    errado: 'Resposta errada',
    erro_sintaxe: 'Erro de sintaxe',
    erro_execucao: 'Erro na execução',
    tempo_esgotado: 'Demorou demais',
  }[correcao.estado];

  return (
    <div
      className={`rounded-xl border p-4 ${
        aceito ? 'border-emerald-400/40 bg-emerald-400/8' : 'border-accent/40 bg-accent/8'
      }`}
    >
      <div className="mb-3 flex flex-wrap items-center gap-3">
        <span
          className={`text-[15px] font-bold ${
            aceito ? 'text-emerald-400' : 'text-accent'
          }`}
        >
          {titulo}
        </span>
        <span className="text-[13px] text-muted">
          {correcao.passaram} de {correcao.total} casos · {correcao.duracaoMs} ms
        </span>
      </div>

      {correcao.detalhe && (
        <pre className="mb-3 overflow-x-auto whitespace-pre-wrap rounded-lg bg-black/35 p-3 font-mono text-[12px] leading-[19px] text-body">
          {correcao.detalhe}
        </pre>
      )}

      {correcao.saida.trim() && (
        <details className="mb-3">
          <summary className="cursor-pointer text-[12.5px] text-muted">
            saída do programa
          </summary>
          <pre className="mt-2 overflow-x-auto whitespace-pre-wrap rounded-lg bg-black/35 p-3 font-mono text-[12px] text-body">
            {correcao.saida}
          </pre>
        </details>
      )}

      <ul className="space-y-1">
        {correcao.casos.map((caso, i) => (
          <li
            key={i}
            className="flex flex-wrap items-baseline gap-x-2.5 gap-y-1 rounded-lg bg-black/20 px-3 py-2 font-mono text-[12px]"
          >
            <span className={caso.passou ? 'text-emerald-400' : 'text-accent'}>
              {caso.passou ? '✓' : '✗'}
            </span>
            <span className="text-muted">
              resolver({caso.entrada.map(valorLegivel).join(', ')})
            </span>
            {!caso.passou && !caso.erro && (
              <>
                <span className="text-accent">devolveu {valorLegivel(caso.obtido)}</span>
                <span className="text-muted">
                  esperava {valorLegivel(caso.esperado)}
                </span>
              </>
            )}
            {caso.passou && (
              <span className="text-body">= {valorLegivel(caso.obtido)}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
