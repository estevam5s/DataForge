/**
 * Big-O acima de cada ação, no editor.
 *
 * Chama `dataforge big-o --json` e desenha o resultado como CodeLens —
 * a linha cinza acima da declaração. Ver `O(n²)` ali, enquanto se
 * escreve, é o que transforma complexidade de assunto de entrevista em
 * ferramenta de trabalho.
 *
 * ─── A decisão de design ────────────────────────────────────
 *
 * O CodeLens mostra a classe e nada mais. O porquê fica no hover e no
 * comando "explicar" — uma linha de sessenta caracteres acima de cada
 * ação transformaria o arquivo num muro de texto cinza, e a informação
 * mais útil (a classe) se perderia no meio.
 */

import * as vscode from 'vscode';
import { json } from './dataforge';

interface OrdemJson {
  notacao: string;
  nome: string;
  familia: string;
  gravidade: number;
  motivos: string[];
}

interface AcaoJson {
  nome: string;
  linha: number;
  tipo: string;
  tempo: OrdemJson;
  espaco: OrdemJson;
  recursiva: boolean;
  avisos: { nivel: string; texto: string; sugestao: string }[];
}

type Relatorio = Record<string, { acoes: AcaoJson[] }>;

/** O último relatório por arquivo, para o hover não reanalisar. */
const cache = new Map<string, AcaoJson[]>();

export function acoesDe(uri: vscode.Uri): AcaoJson[] {
  return cache.get(uri.toString()) ?? [];
}

export class LenteDeComplexidade implements vscode.CodeLensProvider {
  private mudou = new vscode.EventEmitter<void>();
  readonly onDidChangeCodeLenses = this.mudou.event;

  atualizar() {
    this.mudou.fire();
  }

  async provideCodeLenses(
    documento: vscode.TextDocument,
  ): Promise<vscode.CodeLens[]> {
    const config = vscode.workspace.getConfiguration('dataforge');
    if (!config.get('complexidade.mostrar', true)) return [];
    if (documento.isDirty) return this.doCache(documento);

    const relatorio = await json<Relatorio>([
      'big-o',
      documento.uri.fsPath,
      '--json',
    ]);
    if (!relatorio) return this.doCache(documento);

    const acoes = Object.values(relatorio)[0]?.acoes ?? [];
    cache.set(documento.uri.toString(), acoes);
    return this.desenhar(documento, acoes);
  }

  private doCache(documento: vscode.TextDocument): vscode.CodeLens[] {
    return this.desenhar(documento, acoesDe(documento.uri));
  }

  private desenhar(
    documento: vscode.TextDocument,
    acoes: AcaoJson[],
  ): vscode.CodeLens[] {
    const limite = vscode.workspace
      .getConfiguration('dataforge')
      .get<string>('complexidade.avisarAcimaDe', 'O(n log n)');
    const pesoLimite = peso(limite);

    return acoes
      .filter((a) => a.linha > 0 && a.linha <= documento.lineCount)
      .map((a) => {
        const linha = Math.max(0, a.linha - 1);
        const faixa = new vscode.Range(linha, 0, linha, 0);

        const marca = ['✓', '·', '▲', '■'][a.tempo.gravidade] ?? '·';
        const acima = peso(a.tempo.notacao) > pesoLimite ? '  ⟵ acima do limite' : '';
        const espaco =
          a.espaco.notacao === 'O(1)' ? '' : `  ·  ${a.espaco.notacao} espaço`;

        return new vscode.CodeLens(faixa, {
          title: `${marca}  ${a.tempo.notacao} tempo${espaco}${acima}`,
          tooltip: [
            `${a.nome} — ${a.tempo.nome}`,
            '',
            ...a.tempo.motivos.map((m) => `• ${m}`),
            ...(a.avisos.length ? [''] : []),
            ...a.avisos.map((w) => `⚠ ${w.texto}\n   ${w.sugestao}`),
          ].join('\n'),
          command: 'dataforge.explicarComplexidade',
          arguments: [a],
        });
      });
  }
}

/** Um peso comparável, para saber o que está "acima do limite". */
function peso(notacao: string): number {
  const tabela: Record<string, number> = {
    'O(1)': 0,
    'O(log n)': 1,
    'O(n)': 10,
    'O(n log n)': 11,
    'O(n^2)': 20,
    'O(n²)': 20,
    'O(n^2 log n)': 21,
    'O(n^3)': 30,
    'O(n³)': 30,
    'O(2^n)': 8002,
    'O(n!)': 9000,
    'O(?)': 10000,
  };
  return tabela[notacao] ?? 15;
}

/** O painel que explica uma classe, aberto pelo clique no CodeLens. */
export async function explicar(acao: AcaoJson) {
  const linhas: string[] = [
    `## ${acao.nome}`,
    '',
    `**${acao.tempo.notacao}** de tempo — ${acao.tempo.nome}`,
    `**${acao.espaco.notacao}** de espaço`,
    '',
  ];

  if (acao.tempo.motivos.length) {
    linhas.push('### Por quê', '');
    acao.tempo.motivos.forEach((m) => linhas.push(`- ${m}`));
    linhas.push('');
  }

  if (acao.avisos.length) {
    linhas.push('### O que fazer', '');
    acao.avisos.forEach((a) => {
      linhas.push(`**${a.texto}**`, '', a.sugestao, '');
    });
  }

  linhas.push(
    '### A escala',
    '',
    '| classe | n=10 | n=1.000 | n=1.000.000 |',
    '|---|---|---|---|',
    '| O(1) | 1 | 1 | 1 |',
    '| O(log n) | 3 | 10 | 20 |',
    '| O(n) | 10 | 1.000 | 1.000.000 |',
    '| O(n log n) | 33 | 10.000 | 20.000.000 |',
    '| O(n²) | 100 | 1.000.000 | 10¹² |',
    '| O(2ⁿ) | 1.024 | 10³⁰¹ | — |',
    '',
    '[A referência completa de Big-O](https://dataforge-lang.vercel.app/docs/big-o)',
  );

  const doc = await vscode.workspace.openTextDocument({
    content: linhas.join('\n'),
    language: 'markdown',
  });
  await vscode.commands.executeCommand('markdown.showPreviewToSide', doc.uri);
}
