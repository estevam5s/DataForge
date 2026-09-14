/**
 * Big-O medido, e as curvas desenhadas.
 *
 * O `CodeLens` de `complexidade.ts` mostra a classe que o analisador
 * **lê** na árvore. Este arquivo traz a outra metade: a classe que
 * **acontece** quando o código roda, e o desenho que dá escala às
 * duas.
 *
 * ─── Por que as duas, e não uma ─────────────────────────────
 *
 * A análise estática vê `cycle` dentro de `cycle` e diz O(n²) — mesmo
 * quando o laço interno dá três voltas. A medição vê o tempo real,
 * com cache e interpretador dentro, e não sabe o que acontece com `n`
 * dez vezes maior.
 *
 * Quando as duas concordam, a classe está estabelecida. Quando
 * divergem, **a divergência é o resultado** — e é por isso que o painel
 * as põe lado a lado em vez de escolher uma.
 *
 * ─── Por que um webview, e não o terminal ───────────────────
 *
 * A curva é o ponto. `O(n log n)` e `O(n²)` são duas linhas de texto
 * quase iguais e dois desenhos completamente diferentes — e é o
 * desenho que faz alguém entender por que vale reescrever o laço.
 */

import * as vscode from 'vscode';
import { exigirExecutavel, raizDe, rodar } from './dataforge';

/** As curvas, e quanto cada uma custa em n = 1, 10, 100, 1.000, 10.000. */
const CURVAS: { nome: string; cor: string; f: (n: number) => number }[] = [
  { nome: 'O(1)', cor: '#22c55e', f: () => 1 },
  { nome: 'O(log n)', cor: '#84cc16', f: (n) => Math.log2(n || 1) },
  { nome: 'O(n)', cor: '#eab308', f: (n) => n },
  { nome: 'O(n log n)', cor: '#f97316', f: (n) => n * Math.log2(n || 1) },
  { nome: 'O(n²)', cor: '#ef4444', f: (n) => n * n },
  { nome: 'O(2ⁿ)', cor: '#a855f7', f: (n) => Math.pow(2, Math.min(n, 40)) },
];

/**
 * `dataforge big-o --medir` no arquivo aberto, num painel.
 *
 * Ele roda o programa — e por isso pede confirmação quando o arquivo
 * não é um `_test.df`. Um arquivo de trabalho pode escrever em disco,
 * subir servidor ou falar com um banco, e "analisar complexidade" não
 * é um nome que prepara alguém para isso acontecer.
 */
export async function medirComplexidade() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== 'dataforge') {
    void vscode.window.showWarningMessage(
      'Abra um arquivo .df para medir a complexidade.');
    return;
  }
  if (!(await exigirExecutavel())) return;

  const arquivo = editor.document.fileName;
  const escolha = await vscode.window.showWarningMessage(
    'Medir executa as ações do arquivo várias vezes, com entradas de '
    + 'tamanhos crescentes. Se ele escreve em disco ou fala com a rede, '
    + 'isso vai acontecer.',
    { modal: true }, 'Medir');
  if (escolha !== 'Medir') return;

  const painel = vscode.window.createWebviewPanel(
    'dataforgeBigO', 'Big-O medido', vscode.ViewColumn.Beside,
    { enableScripts: false });
  painel.webview.html = esqueleto(
    '<p class="espera">medindo…</p>'
    + '<p class="nota">Cada ação roda em quatro tamanhos. Uma ação '
    + 'quadrática no maior deles demora.</p>');

  const saida = await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Window, title: 'DataForge: medindo' },
    () => rodarCapturando(['big-o', '--medir', arquivo], raizDe(editor.document)),
  );

  painel.webview.html = esqueleto(tabelaDoTexto(saida));
}

/** O desenho das curvas, para dar escala ao que o CodeLens diz. */
export function abrirCurvas() {
  const painel = vscode.window.createWebviewPanel(
    'dataforgeCurvas', 'Big-O — as curvas', vscode.ViewColumn.Beside,
    { enableScripts: false });
  painel.webview.html = esqueleto(desenho() + tabelaDeEscala());
}

// ── execução ─────────────────────────────────────────────────

async function rodarCapturando(args: string[], cwd: string): Promise<string> {
  const exe = await exigirExecutavel();
  if (!exe) return 'não foi possível encontrar o dataforge';
  try {
    // Prazo largo: medir roda cada ação em quatro tamanhos, e uma
    // quadrática no maior deles leva segundos. O padrão de 20 s
    // cortaria a medida no meio e devolveria uma tabela pela metade.
    const { saida, erro } = await rodar(exe, args, 180000, cwd);
    return saida + (erro ? `\n${erro}` : '');
  } catch (e) {
    return String((e as Error).message);
  }
}

// ── desenho ──────────────────────────────────────────────────

function desenho(): string {
  const L = 520, A = 300, M = 34;
  const nMax = 32;
  // Escala LOGARÍTMICA no eixo do custo.
  //
  // Linear, a curva de O(2ⁿ) vira uma parede vertical e esmaga as
  // outras cinco contra o eixo — o desenho passaria a mostrar só a
  // pior, que é justamente a que ninguém precisa de ajuda para
  // reconhecer.
  const custoMax = Math.log2(Math.pow(2, nMax));

  const caminhos = CURVAS.map(({ nome, cor, f }) => {
    const pontos: string[] = [];
    for (let n = 1; n <= nMax; n += 1) {
      const x = M + ((n - 1) / (nMax - 1)) * (L - 2 * M);
      const custo = Math.max(f(n), 1);
      const y = A - M - (Math.log2(custo) / custoMax) * (A - 2 * M);
      pontos.push(`${x.toFixed(1)},${Math.max(M, y).toFixed(1)}`);
    }
    return `<polyline points="${pontos.join(' ')}" fill="none"
      stroke="${cor}" stroke-width="2" stroke-linejoin="round"/>
      <text x="${L - M + 4}" y="${
      A - M - (Math.log2(Math.max(f(nMax), 1)) / custoMax) * (A - 2 * M) + 4
    }" fill="${cor}" font-size="11">${nome}</text>`;
  }).join('\n');

  return `
<div class="grafico">
  <svg viewBox="0 0 ${L + 70} ${A}" role="img"
       aria-label="As seis curvas de crescimento, em escala logarítmica">
    <line x1="${M}" y1="${A - M}" x2="${L - M}" y2="${A - M}"
          stroke="currentColor" stroke-opacity=".25"/>
    <line x1="${M}" y1="${M}" x2="${M}" y2="${A - M}"
          stroke="currentColor" stroke-opacity=".25"/>
    <text x="${L / 2}" y="${A - 6}" text-anchor="middle"
          font-size="11" fill="currentColor" opacity=".55">n →</text>
    <text x="10" y="${A / 2}" font-size="11" fill="currentColor"
          opacity=".55" transform="rotate(-90 10 ${A / 2})">custo (log) →</text>
    ${caminhos}
  </svg>
  <p class="nota">Escala logarítmica no custo. Linear, a curva de O(2ⁿ)
  vira uma parede e esmaga as outras cinco contra o eixo.</p>
</div>`;
}

function tabelaDeEscala(): string {
  const ns = [10, 100, 1000, 10000, 100000];
  const linhas = CURVAS.map(({ nome, cor, f }) => {
    const celulas = ns.map((n) => {
      const v = f(n);
      return `<td>${formatar(v)}</td>`;
    }).join('');
    return `<tr><th style="color:${cor}">${nome}</th>${celulas}</tr>`;
  }).join('\n');

  return `
<h2>Quantas operações, por tamanho</h2>
<table>
  <thead><tr><th>classe</th>${
    ns.map((n) => `<th>n = ${n.toLocaleString('pt-BR')}</th>`).join('')
  }</tr></thead>
  <tbody>${linhas}</tbody>
</table>
<p class="nota">A diferença entre O(n log n) e O(n²) não aparece em n = 10.
Ela é a diferença entre responder e não responder em n = 100.000.</p>`;
}

function formatar(v: number): string {
  if (!isFinite(v)) return '∞';
  if (v >= 1e15) return v.toExponential(1).replace('e+', '×10^');
  if (v >= 1000) return Math.round(v).toLocaleString('pt-BR');
  return v < 10 ? v.toFixed(1) : String(Math.round(v));
}

/** A saída do comando, como tabela — sem reimplementar a análise. */
function tabelaDoTexto(texto: string): string {
  const limpo = texto.replace(/\x1b\[[0-9;]*m/g, '');
  const linhas = limpo.split('\n');
  const corpo = linhas
    .filter((l) => /^\s{2}\S/.test(l) && !/^\s+[─-]+/.test(l))
    .map((l) => l.trimEnd());

  if (corpo.length === 0) {
    return `<pre class="cru">${escapar(limpo)}</pre>`;
  }
  return `<h2>Analisado × medido</h2><pre class="tabela">${
    escapar(corpo.join('\n'))
  }</pre>
  <p class="nota">Quando as duas concordam, a classe está estabelecida.
  Quando divergem, a divergência é o resultado: a árvore conta estrutura
  e não sabe quantas voltas cada laço dá; o relógio vê o que houve e não
  sabe o que vem depois.</p>`;
}

function escapar(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/** O webview herda as cores do tema — um painel branco num editor escuro
 *  é a marca de extensão que não se importou. */
function esqueleto(conteudo: string): string {
  return `<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<style>
  body { font-family: var(--vscode-font-family); padding: 18px 22px;
         color: var(--vscode-foreground); font-size: 13px; line-height: 1.6; }
  h2 { font-size: 14px; margin: 22px 0 10px; }
  table { border-collapse: collapse; width: 100%; font-size: 12.5px; }
  th, td { text-align: right; padding: 5px 10px;
           border-bottom: 1px solid var(--vscode-panel-border); }
  th:first-child, thead th { text-align: left; }
  tbody th { font-weight: 600; }
  pre { background: var(--vscode-textCodeBlock-background);
        padding: 12px 14px; border-radius: 6px; overflow-x: auto;
        font-family: var(--vscode-editor-font-family); font-size: 12px; }
  .nota { opacity: .7; font-size: 12px; margin-top: 10px; }
  .espera { opacity: .7; }
  .grafico svg { width: 100%; height: auto; }
</style></head><body>${conteudo}</body></html>`;
}
