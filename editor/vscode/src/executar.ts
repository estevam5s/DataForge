/**
 * Rodar o arquivo, e saber quanto tempo levou.
 *
 * Duas formas, porque servem a coisas diferentes:
 *
 *   terminal   saída ao vivo, entrada do teclado, cores. É o que se
 *              quer ao desenvolver.
 *   medido     captura tudo e cronometra. É o que se quer ao comparar
 *              duas versões do mesmo algoritmo.
 *
 * O terminal é reaproveitado entre execuções: abrir um novo a cada F5
 * enche a lista de terminais em cinco minutos.
 */

import * as path from 'path';
import * as vscode from 'vscode';
import { exigirExecutavel, projetoDe, raizDe, rodar } from './dataforge';

let terminal: vscode.Terminal | undefined;

function obterTerminal(): vscode.Terminal {
  if (!terminal || terminal.exitStatus !== undefined) {
    terminal = vscode.window.createTerminal({
      name: 'DataForge',
      iconPath: new vscode.ThemeIcon('flame'),
    });
  }
  return terminal;
}

export function fecharTerminal() {
  terminal?.dispose();
  terminal = undefined;
}

/** Salva o arquivo antes de rodar. Rodar a versão antiga confunde. */
async function garantirSalvo(documento: vscode.TextDocument): Promise<boolean> {
  if (!documento.isDirty) return true;
  return documento.save();
}

export async function rodarNoTerminal(
  documento: vscode.TextDocument,
  extras: string[] = [],
) {
  const exe = await exigirExecutavel();
  if (!exe) return;
  if (!(await garantirSalvo(documento))) return;

  const t = obterTerminal();
  t.show(true);

  const cwd = projetoDe(documento.uri.fsPath) ?? raizDe(documento);
  const arquivo = path.relative(cwd, documento.uri.fsPath) || documento.uri.fsPath;

  // Aspas em volta do caminho: uma pasta com espaço no nome quebra a
  // linha de comando, e "Meus Documentos" é comum no Windows.
  const partes = [exe, ...extras, `"${arquivo}"`];
  t.sendText(`cd "${cwd}"`, true);
  t.sendText(partes.join(' '), true);
}

export interface Medida {
  saida: string;
  erro: string;
  codigo: number;
  ms: number;
}

/**
 * Roda capturando tudo e cronometrando.
 *
 * O tempo medido inclui a subida do interpretador (~40 ms), e a
 * mensagem diz isso: apresentar 42 ms como "o tempo do seu algoritmo"
 * quando 40 deles são a partida seria enganoso ao comparar programas
 * curtos.
 */
export async function rodarMedindo(
  documento: vscode.TextDocument,
): Promise<Medida | null> {
  const exe = await exigirExecutavel();
  if (!exe) return null;
  if (!(await garantirSalvo(documento))) return null;

  const cwd = projetoDe(documento.uri.fsPath) ?? raizDe(documento);
  const inicio = Date.now();
  const { saida, erro, codigo } = await rodar(
    exe,
    ['run', documento.uri.fsPath],
    120000,
    cwd,
  );
  return { saida, erro, codigo, ms: Date.now() - inicio };
}

/** O canal onde as execuções medidas aparecem, uma após a outra. */
let canal: vscode.OutputChannel | undefined;

export function obterCanal(): vscode.OutputChannel {
  if (!canal) canal = vscode.window.createOutputChannel('DataForge');
  return canal;
}

export async function rodarEMostrarTempo(documento: vscode.TextDocument) {
  const saida = obterCanal();
  saida.show(true);

  const nome = path.basename(documento.uri.fsPath);
  saida.appendLine('');
  saida.appendLine(`─── ${nome} · ${new Date().toLocaleTimeString()} ───`);

  const medida = await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Window, title: `Rodando ${nome}…` },
    () => rodarMedindo(documento),
  );
  if (!medida) return;

  if (medida.saida.trim()) saida.appendLine(medida.saida.trimEnd());
  if (medida.erro.trim()) saida.appendLine(medida.erro.trimEnd());

  const tempo = formatarTempo(medida.ms);
  saida.appendLine(
    medida.codigo === 0
      ? `✓ terminou em ${tempo}  (inclui ~40ms de partida do interpretador)`
      : `✗ saiu com código ${medida.codigo} depois de ${tempo}`,
  );

  if (medida.codigo === 0) {
    vscode.window.setStatusBarMessage(`DataForge: ${nome} em ${tempo}`, 6000);
  }
}

export function formatarTempo(ms: number): string {
  if (ms < 1000) return `${ms} ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(2)} s`;
  return `${Math.floor(ms / 60000)} min ${((ms % 60000) / 1000).toFixed(0)} s`;
}

/** Roda o arquivo várias vezes e mostra a distribuição, não só a média. */
export async function medirRepetido(documento: vscode.TextDocument) {
  const resposta = await vscode.window.showInputBox({
    prompt: 'Quantas execuções?',
    value: '10',
    validateInput: (v) =>
      /^\d+$/.test(v) && +v > 0 && +v <= 500 ? null : 'um número entre 1 e 500',
  });
  if (!resposta) return;

  const vezes = parseInt(resposta, 10);
  const saida = obterCanal();
  saida.show(true);
  saida.appendLine('');
  saida.appendLine(`─── ${path.basename(documento.uri.fsPath)} × ${vezes} ───`);

  const tempos: number[] = [];
  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: 'Medindo…', cancellable: true },
    async (progresso, cancelar) => {
      for (let i = 0; i < vezes; i++) {
        if (cancelar.isCancellationRequested) break;
        const m = await rodarMedindo(documento);
        if (!m) break;
        tempos.push(m.ms);
        progresso.report({ increment: 100 / vezes, message: `${i + 1}/${vezes}` });
      }
    },
  );

  if (!tempos.length) return;
  tempos.sort((a, b) => a - b);
  const soma = tempos.reduce((a, b) => a + b, 0);

  // Mediana e p95 junto da média: uma pausa do coletor de lixo no meio
  // de dez execuções move a média e não aparece nela.
  saida.appendLine(`  execuções  ${tempos.length}`);
  saida.appendLine(`  média      ${formatarTempo(Math.round(soma / tempos.length))}`);
  saida.appendLine(`  mediana    ${formatarTempo(tempos[Math.floor(tempos.length / 2)])}`);
  saida.appendLine(`  mínimo     ${formatarTempo(tempos[0])}`);
  saida.appendLine(`  máximo     ${formatarTempo(tempos[tempos.length - 1])}`);
  saida.appendLine(
    `  p95        ${formatarTempo(tempos[Math.min(tempos.length - 1, Math.floor(tempos.length * 0.95))])}`,
  );
}
