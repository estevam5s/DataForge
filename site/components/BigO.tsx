'use client';

import { useEffect, useMemo, useRef, useState } from 'react';

/**
 * As curvas de crescimento, desenhadas.
 *
 * Uma tabela de números diz que O(n²) é pior que O(n log n). O gráfico
 * mostra *quanto* — e é a diferença entre saber a ordem e entender por
 * que ela decide o projeto.
 *
 * A escala é logarítmica no eixo vertical de propósito: em escala
 * linear, O(2ⁿ) vira uma linha vertical e esmaga todas as outras contra
 * o eixo, que é exatamente a informação que o leitor precisa comparar.
 */

type Classe = {
  nome: string;
  notacao: string;
  cor: string;
  f: (n: number) => number;
  descricao: string;
};

const CLASSES: Classe[] = [
  { nome: 'constante', notacao: 'O(1)', cor: '#22c55e', f: () => 1,
    descricao: 'o tamanho da entrada não muda o tempo' },
  { nome: 'logarítmica', notacao: 'O(log n)', cor: '#14b8a6', f: (n) => Math.log2(n + 1),
    descricao: 'cada passo descarta metade do que sobrou' },
  { nome: 'linear', notacao: 'O(n)', cor: '#3b82f6', f: (n) => n,
    descricao: 'dobrar a entrada dobra o tempo' },
  { nome: 'linearítmica', notacao: 'O(n log n)', cor: '#8b5cf6', f: (n) => n * Math.log2(n + 1),
    descricao: 'o melhor possível para ordenar comparando' },
  { nome: 'quadrática', notacao: 'O(n²)', cor: '#f59e0b', f: (n) => n * n,
    descricao: 'dobrar a entrada quadruplica o tempo' },
  { nome: 'cúbica', notacao: 'O(n³)', cor: '#f97316', f: (n) => n ** 3,
    descricao: 'só serve para entrada pequena' },
  { nome: 'exponencial', notacao: 'O(2ⁿ)', cor: '#ef4444', f: (n) => 2 ** Math.min(n, 40),
    descricao: 'cada item a mais dobra o custo' },
];

const LARGURA = 720;
const ALTURA = 340;
const MARGEM = { topo: 16, direita: 16, baixo: 32, esquerda: 46 };

/** Gráfico com as curvas desenhando-se da esquerda para a direita. */
export function CurvasBigO() {
  const [visiveis, setVisiveis] = useState<Set<string>>(
    () => new Set(CLASSES.map((c) => c.notacao)),
  );
  const [n, setN] = useState(30);
  const [animou, setAnimou] = useState(false);
  const caixa = useRef<HTMLDivElement>(null);

  // A animação começa quando o gráfico entra na tela, não ao carregar:
  // uma curva que já terminou de desenhar antes de o leitor rolar até
  // ela não anima coisa nenhuma.
  useEffect(() => {
    const elemento = caixa.current;
    if (!elemento) return;
    const observador = new IntersectionObserver(
      ([entrada]) => entrada.isIntersecting && setAnimou(true),
      { threshold: 0.25 },
    );
    observador.observe(elemento);
    return () => observador.disconnect();
  }, []);

  const largura = LARGURA - MARGEM.esquerda - MARGEM.direita;
  const altura = ALTURA - MARGEM.topo - MARGEM.baixo;

  // O teto vem da maior curva visível, para o desenho usar a altura
  // inteira em vez de espremer tudo embaixo.
  const teto = useMemo(() => {
    const ativas = CLASSES.filter((c) => visiveis.has(c.notacao));
    if (!ativas.length) return 10;
    return Math.max(...ativas.map((c) => c.f(n)));
  }, [visiveis, n]);

  const y = (v: number) => {
    const t = Math.log10(Math.max(v, 1) + 1) / Math.log10(teto + 1);
    return MARGEM.topo + altura - t * altura;
  };
  const x = (v: number) => MARGEM.esquerda + (v / n) * largura;

  const caminho = (c: Classe) => {
    const passos = 90;
    const pontos: string[] = [];
    for (let i = 0; i <= passos; i++) {
      const v = (i / passos) * n;
      pontos.push(`${i === 0 ? 'M' : 'L'} ${x(v).toFixed(1)} ${y(c.f(v)).toFixed(1)}`);
    }
    return pontos.join(' ');
  };

  const alternar = (notacao: string) =>
    setVisiveis((antes) => {
      const proximo = new Set(antes);
      proximo.has(notacao) ? proximo.delete(notacao) : proximo.add(notacao);
      return proximo;
    });

  return (
    <div ref={caixa} className="my-8 rounded-2xl border border-line bg-surface/40 p-4 sm:p-5">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        {CLASSES.map((c) => {
          const ativa = visiveis.has(c.notacao);
          return (
            <button
              key={c.notacao}
              onClick={() => alternar(c.notacao)}
              className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[12px] font-medium transition-all ${
                ativa
                  ? 'border-transparent text-strong'
                  : 'border-line text-muted opacity-50 hover:opacity-80'
              }`}
              style={ativa ? { background: `${c.cor}22`, borderColor: `${c.cor}66` } : {}}
              aria-pressed={ativa}
            >
              <span
                className="h-2 w-2 shrink-0 rounded-full"
                style={{ background: c.cor }}
                aria-hidden
              />
              {c.notacao}
            </button>
          );
        })}
      </div>

      <div className="overflow-x-auto">
        <svg
          viewBox={`0 0 ${LARGURA} ${ALTURA}`}
          className="w-full min-w-[520px]"
          role="img"
          aria-label="Curvas de crescimento das classes de complexidade"
        >
          {/* grade */}
          {[0, 0.25, 0.5, 0.75, 1].map((t) => (
            <line
              key={t}
              x1={MARGEM.esquerda}
              x2={LARGURA - MARGEM.direita}
              y1={MARGEM.topo + altura * t}
              y2={MARGEM.topo + altura * t}
              stroke="currentColor"
              className="text-line"
              strokeWidth="1"
              strokeDasharray="3 4"
            />
          ))}

          <line
            x1={MARGEM.esquerda} y1={MARGEM.topo}
            x2={MARGEM.esquerda} y2={MARGEM.topo + altura}
            stroke="currentColor" className="text-line" strokeWidth="1.5"
          />
          <line
            x1={MARGEM.esquerda} y1={MARGEM.topo + altura}
            x2={LARGURA - MARGEM.direita} y2={MARGEM.topo + altura}
            stroke="currentColor" className="text-line" strokeWidth="1.5"
          />

          <text x={MARGEM.esquerda - 8} y={MARGEM.topo + 4} textAnchor="end"
                className="fill-muted text-[10px]">operações</text>
          <text x={LARGURA - MARGEM.direita} y={ALTURA - 8} textAnchor="end"
                className="fill-muted text-[10px]">n (tamanho da entrada)</text>

          {CLASSES.filter((c) => visiveis.has(c.notacao)).map((c, i) => (
            <path
              key={c.notacao}
              d={caminho(c)}
              fill="none"
              stroke={c.cor}
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{
                strokeDasharray: 2400,
                strokeDashoffset: animou ? 0 : 2400,
                transition: `stroke-dashoffset 1.1s cubic-bezier(.22,1,.36,1) ${i * 90}ms`,
              }}
            />
          ))}
        </svg>
      </div>

      <label className="mt-3 flex items-center gap-3 text-[12.5px] text-muted">
        <span className="shrink-0">n = {n}</span>
        <input
          type="range"
          min={5}
          max={100}
          value={n}
          onChange={(e) => setN(Number(e.target.value))}
          className="h-1 flex-1 cursor-pointer appearance-none rounded-full bg-line accent-accent"
          aria-label="Tamanho da entrada"
        />
      </label>
      <p className="mt-2 text-[12px] leading-[18px] text-muted">
        Escala logarítmica na vertical — em escala linear, O(2ⁿ) vira uma
        reta e esmaga todas as outras contra o eixo.
      </p>
    </div>
  );
}

/** A tabela de operações por tamanho, com a barra crescendo. */
export function EscalaBigO() {
  const [animou, setAnimou] = useState(false);
  const caixa = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const elemento = caixa.current;
    if (!elemento) return;
    const observador = new IntersectionObserver(
      ([e]) => e.isIntersecting && setAnimou(true),
      { threshold: 0.2 },
    );
    observador.observe(elemento);
    return () => observador.disconnect();
  }, []);

  const linhas = [
    { notacao: 'O(1)', cor: '#22c55e', n10: '1', n1k: '1', n1m: '1', peso: 0.04 },
    { notacao: 'O(log n)', cor: '#14b8a6', n10: '3', n1k: '10', n1m: '20', peso: 0.1 },
    { notacao: 'O(n)', cor: '#3b82f6', n10: '10', n1k: '1.000', n1m: '1 milhão', peso: 0.3 },
    { notacao: 'O(n log n)', cor: '#8b5cf6', n10: '33', n1k: '10 mil', n1m: '20 milhões', peso: 0.45 },
    { notacao: 'O(n²)', cor: '#f59e0b', n10: '100', n1k: '1 milhão', n1m: '10¹²', peso: 0.68 },
    { notacao: 'O(n³)', cor: '#f97316', n10: '1.000', n1k: '10⁹', n1m: '10¹⁸', peso: 0.85 },
    { notacao: 'O(2ⁿ)', cor: '#ef4444', n10: '1.024', n1k: '10³⁰¹', n1m: '—', peso: 1 },
  ];

  return (
    <div ref={caixa} className="my-8 overflow-x-auto">
      <table className="w-full min-w-[440px] border-collapse text-[13px]">
        <thead>
          <tr className="border-b border-line text-left text-muted">
            <th className="py-2 pr-3 font-medium">classe</th>
            <th className="py-2 pr-3 text-right font-medium">n=10</th>
            <th className="py-2 pr-3 text-right font-medium">n=1.000</th>
            <th className="py-2 pr-3 text-right font-medium">n=1 milhão</th>
            <th className="w-[28%] py-2 font-medium">crescimento</th>
          </tr>
        </thead>
        <tbody>
          {linhas.map((l, i) => (
            <tr key={l.notacao} className="border-b border-line/40">
              <td className="py-2 pr-3">
                <span className="font-mono font-semibold" style={{ color: l.cor }}>
                  {l.notacao}
                </span>
              </td>
              <td className="py-2 pr-3 text-right tabular-nums text-body">{l.n10}</td>
              <td className="py-2 pr-3 text-right tabular-nums text-body">{l.n1k}</td>
              <td className="py-2 pr-3 text-right tabular-nums text-body">{l.n1m}</td>
              <td className="py-2">
                <span className="block h-1.5 rounded-full bg-line/50">
                  <span
                    className="block h-full rounded-full"
                    style={{
                      background: l.cor,
                      width: animou ? `${l.peso * 100}%` : '0%',
                      transition: `width .9s cubic-bezier(.22,1,.36,1) ${i * 70}ms`,
                    }}
                  />
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/**
 * Dois algoritmos correndo lado a lado, passo a passo.
 *
 * Ver a busca linear percorrer trinta caixas enquanto a binária
 * descarta metade a cada passo é o argumento que a notação não faz
 * sozinha.
 */
export function CorridaBusca() {
  const TOTAL = 32;
  const alvo = 27;
  const [passo, setPasso] = useState(0);
  const [rodando, setRodando] = useState(false);

  const linear = useMemo(() => {
    const passos: number[] = [];
    for (let i = 0; i < TOTAL; i++) {
      passos.push(i);
      if (i === alvo) break;
    }
    return passos;
  }, []);

  const binaria = useMemo(() => {
    const passos: number[] = [];
    let baixo = 0;
    let alto = TOTAL - 1;
    while (baixo <= alto) {
      const meio = Math.floor((baixo + alto) / 2);
      passos.push(meio);
      if (meio === alvo) break;
      if (meio < alvo) baixo = meio + 1;
      else alto = meio - 1;
    }
    return passos;
  }, []);

  const maximo = Math.max(linear.length, binaria.length);

  useEffect(() => {
    if (!rodando) return;
    if (passo >= maximo) {
      setRodando(false);
      return;
    }
    const t = setTimeout(() => setPasso((p) => p + 1), 220);
    return () => clearTimeout(t);
  }, [rodando, passo, maximo]);

  const Faixa = ({
    titulo,
    notacao,
    passos,
    cor,
  }: { titulo: string; notacao: string; passos: number[]; cor: string }) => {
    const vistos = passos.slice(0, passo);
    const atual = vistos[vistos.length - 1];
    const achou = vistos.includes(alvo);
    return (
      <div className="mb-4">
        <div className="mb-1.5 flex items-baseline justify-between text-[12.5px]">
          <span className="font-medium text-strong">
            {titulo} <span className="font-mono text-muted">{notacao}</span>
          </span>
          <span className="tabular-nums text-muted">
            {Math.min(vistos.length, passos.length)} passo(s)
            {achou && <span className="ml-1.5 font-semibold" style={{ color: cor }}>achou</span>}
          </span>
        </div>
        <div className="flex flex-wrap gap-[3px]">
          {Array.from({ length: TOTAL }, (_, i) => {
            const olhado = vistos.includes(i);
            const agora = i === atual;
            return (
              <span
                key={i}
                className="h-4 w-4 rounded-[3px] transition-all duration-200"
                style={{
                  background: agora
                    ? cor
                    : olhado
                      ? `${cor}55`
                      : i === alvo && achou
                        ? cor
                        : 'rgb(var(--line))',
                  transform: agora ? 'scale(1.25)' : 'scale(1)',
                }}
              />
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="my-8 rounded-2xl border border-line bg-surface/40 p-4 sm:p-5">
      <Faixa titulo="Busca linear" notacao="O(n)" passos={linear} cor="#3b82f6" />
      <Faixa titulo="Busca binária" notacao="O(log n)" passos={binaria} cor="#22c55e" />

      <div className="mt-3 flex items-center gap-3">
        <button
          onClick={() => {
            setPasso(0);
            setRodando(true);
          }}
          className="rounded-lg bg-accent px-3 py-1.5 text-[12.5px] font-semibold text-white transition-colors hover:bg-accent-soft"
        >
          {rodando ? 'rodando…' : passo > 0 ? 'de novo' : 'procurar o 27'}
        </button>
        <p className="text-[12px] text-muted">
          {linear.length} contra {binaria.length} passos em 32 itens. Com 1
          milhão, seriam 1.000.000 contra 20.
        </p>
      </div>
    </div>
  );
}
