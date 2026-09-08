/**
 * A ponte com a CLI do DataForge.
 *
 * Toda análise — erros, complexidade, custo de import — é feita pelo
 * interpretador, não aqui. A extensão só chama e desenha.
 *
 * Não é preguiça: é a única forma de o editor e o terminal nunca
 * discordarem. Uma segunda implementação em TypeScript divergiria da
 * primeira no dia em que a linguagem ganhasse um nó novo, e o
 * programador veria um erro no editor que o `dataforge check` não
 * confirma — ou pior, o contrário.
 */

import { execFile } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

/** Onde o executável mora, na ordem em que vale a pena procurar. */
function candidatos(): string[] {
  const config = vscode.workspace.getConfiguration('dataforge');
  const definido = config.get<string>('caminho', '').trim();
  const lista = definido ? [definido] : [];

  const casa = process.env.HOME || process.env.USERPROFILE || '';
  return lista.concat([
    'dataforge',
    path.join(casa, '.dataforge', 'bin', 'dataforge'),
    path.join(casa, '.dataforge', 'Scripts', 'dataforge.exe'),
    '/usr/local/bin/dataforge',
    '/opt/homebrew/bin/dataforge',
  ]);
}

let achado: string | null = null;

/**
 * O caminho do executável, procurado uma vez e lembrado.
 *
 * Procurar a cada chamada custaria um `spawn` por tecla digitada —
 * a análise roda ao salvar e ao editar.
 */
export async function executavel(): Promise<string | null> {
  if (achado) return achado;

  for (const alvo of candidatos()) {
    try {
      await rodar(alvo, ['--version'], 4000);
      achado = alvo;
      return alvo;
    } catch {
      /* tenta o próximo */
    }
  }
  return null;
}

export function esquecerExecutavel() {
  achado = null;
}

/** Roda um comando e devolve a saída. Rejeita se o processo falhar. */
export function rodar(
  comando: string,
  args: string[],
  prazo = 20000,
  cwd?: string,
): Promise<{ saida: string; erro: string; codigo: number }> {
  return new Promise((resolver, rejeitar) => {
    execFile(
      comando,
      args,
      { timeout: prazo, cwd, maxBuffer: 12 * 1024 * 1024 },
      (falha, saida, erro) => {
        const codigo = falha ? ((falha as any).code ?? 1) : 0;
        // Código de saída ≠ 0 NÃO é motivo para rejeitar: `check` sai
        // com 1 quando acha erro, e é justamente essa saída que
        // queremos ler.
        if (falha && (falha as any).code === undefined) {
          rejeitar(falha);
          return;
        }
        resolver({ saida: saida ?? '', erro: erro ?? '', codigo });
      },
    );
  });
}

/** Roda um subcomando do dataforge e devolve JSON já convertido. */
export async function json<T>(args: string[], cwd?: string): Promise<T | null> {
  const exe = await executavel();
  if (!exe) return null;
  try {
    const { saida } = await rodar(exe, args, 30000, cwd);
    const inicio = saida.indexOf('{');
    const fim = saida.lastIndexOf('}');
    if (inicio < 0 || fim < inicio) return null;
    return JSON.parse(saida.slice(inicio, fim + 1)) as T;
  } catch {
    return null;
  }
}

/** A pasta do projeto que contém o arquivo, ou a pasta do arquivo. */
export function raizDe(documento: vscode.TextDocument): string {
  const pasta = vscode.workspace.getWorkspaceFolder(documento.uri);
  if (pasta) return pasta.uri.fsPath;
  return path.dirname(documento.uri.fsPath);
}

/** O `forge.toml` mais próximo, subindo a partir do arquivo. */
export function projetoDe(arquivo: string): string | null {
  let atual = path.dirname(arquivo);
  for (let i = 0; i < 12; i++) {
    if (fs.existsSync(path.join(atual, 'forge.toml'))) return atual;
    const acima = path.dirname(atual);
    if (acima === atual) break;
    atual = acima;
  }
  return null;
}

/** Avisa uma vez só que o executável não foi encontrado. */
let jaAvisou = false;
export async function exigirExecutavel(): Promise<string | null> {
  const exe = await executavel();
  if (exe) return exe;

  if (!jaAvisou) {
    jaAvisou = true;
    const escolha = await vscode.window.showWarningMessage(
      'DataForge não foi encontrado no PATH.',
      'Como instalar',
      'Informar o caminho',
    );
    if (escolha === 'Como instalar') {
      vscode.env.openExternal(
        vscode.Uri.parse('https://dataforge-lang.vercel.app/docs/instalacao'),
      );
    } else if (escolha === 'Informar o caminho') {
      vscode.commands.executeCommand(
        'workbench.action.openSettings',
        'dataforge.caminho',
      );
    }
  }
  return null;
}
