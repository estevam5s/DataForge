/**
 * Subir o servidor da linguagem sem sair do editor.
 *
 * Um framework web tem um ciclo próprio — sobe, recarrega, cai — e ele
 * não é o mesmo de "rodar este arquivo". Tratar os dois como a mesma
 * coisa dá dois problemas concretos: o terminal de execução fica preso
 * para sempre num processo que não termina, e não há onde apertar para
 * parar ou reiniciar.
 *
 * Quatro decisões:
 *
 * 1. **Terminal próprio, um por projeto.** O do `run` é reaproveitado
 *    entre execuções; se o servidor morar nele, a próxima execução mata
 *    o servidor sem avisar.
 * 2. **A entrada é descoberta, não perguntada.** `forge.toml` diz qual
 *    é; sem ele, procura-se por `main.df`/`app.df`/`servidor.df` na
 *    raiz. Perguntar a cada vez é o tipo de atrito que faz a pessoa
 *    voltar para o terminal.
 * 3. **`--host` e porta ficam visíveis e configuráveis.** Dentro de um
 *    container o padrão `127.0.0.1` responde só a si mesmo, e o sintoma
 *    engana: o log diz "no ar" e o navegador não recebe nada.
 * 4. **A barra de status mostra que há servidor de pé.** Um processo
 *    servindo numa aba escondida é a forma mais fácil de deixar a porta
 *    ocupada e não entender por quê.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

import { exigirExecutavel, projetoDe, raizDe } from './dataforge';

/** Os nomes que um arquivo de entrada costuma ter. */
const CANDIDATOS = ['main.df', 'app.df', 'servidor.df', 'server.df',
                    'src/main.df', 'src/app.df', 'src/servidor.df'];

type Servidor = {
  terminal: vscode.Terminal;
  arquivo: string;
  porta: number;
  vitrine: boolean;
};

const emPe = new Map<string, Servidor>();
let indicador: vscode.StatusBarItem | undefined;

export function prepararIndicador(contexto: vscode.ExtensionContext) {
  indicador = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left, 96);
  indicador.command = 'dataforge.servidorParar';
  contexto.subscriptions.push(indicador);
  atualizarIndicador();
}

function atualizarIndicador() {
  if (!indicador) return;
  if (emPe.size === 0) {
    indicador.hide();
    return;
  }
  const portas = [...emPe.values()].map((s) => s.porta).join(', ');
  indicador.text = `$(radio-tower) DataForge :${portas}`;
  indicador.tooltip = 'Um servidor DataForge está no ar. Clique para parar.';
  indicador.show();
}

/** O `entrada = ` do forge.toml, quando houver. */
function entradaDoManifesto(raiz: string): string | null {
  const manifesto = path.join(raiz, 'forge.toml');
  if (!fs.existsSync(manifesto)) return null;
  try {
    const texto = fs.readFileSync(manifesto, 'utf8');
    const achado = texto.match(/^\s*(?:entrada|entry|main)\s*=\s*["']([^"']+)["']/m);
    if (!achado) return null;
    const completo = path.join(raiz, achado[1]);
    return fs.existsSync(completo) ? completo : null;
  } catch {
    return null;
  }
}

/**
 * Qual arquivo sobe o servidor.
 *
 * A ordem importa: o que está aberto ganha do manifesto, porque quem
 * apertou o botão com `api.df` na tela quer subir `api.df`.
 */
function descobrirEntrada(raiz: string): string | null {
  const aberto = vscode.window.activeTextEditor?.document;
  if (aberto?.languageId === 'dataforge' && !aberto.isUntitled) {
    const texto = aberto.getText();
    if (/\bignite\b|\bV\.rodar\b|\bVitrine\.rodar\b/.test(texto)) {
      return aberto.uri.fsPath;
    }
  }
  const doManifesto = entradaDoManifesto(raiz);
  if (doManifesto) return doManifesto;
  for (const candidato of CANDIDATOS) {
    const completo = path.join(raiz, candidato);
    if (fs.existsSync(completo)) return completo;
  }
  return aberto?.languageId === 'dataforge' ? aberto.uri.fsPath : null;
}

/** Um arquivo que chama `V.montar`/`V.rodar` é Vitrine, e sobe por outro comando. */
function ehVitrine(arquivo: string): boolean {
  try {
    const texto = fs.readFileSync(arquivo, 'utf8');
    return /\bV\.(montar|rodar)\b|adopt\s+Arcane\.Vitrine/.test(texto);
  } catch {
    return false;
  }
}

function configuracao() {
  const config = vscode.workspace.getConfiguration('dataforge');
  return {
    porta: config.get<number>('servidor.porta', 8000),
    host: config.get<string>('servidor.host', '127.0.0.1'),
    abrirNavegador: config.get<boolean>('servidor.abrirNavegador', true),
  };
}

export async function servidorIniciar() {
  const exe = await exigirExecutavel();
  if (!exe) return;

  const documento = vscode.window.activeTextEditor?.document;
  const raiz = documento
    ? (projetoDe(documento.uri.fsPath) ?? raizDe(documento))
    : (vscode.workspace.workspaceFolders?.[0]?.uri.fsPath ?? process.cwd());

  if (emPe.has(raiz)) {
    const escolha = await vscode.window.showWarningMessage(
      'Já há um servidor no ar para este projeto.',
      'Reiniciar', 'Mostrar terminal');
    if (escolha === 'Reiniciar') {
      await servidorParar(raiz);
    } else {
      emPe.get(raiz)?.terminal.show(true);
      return;
    }
  }

  const arquivo = descobrirEntrada(raiz);
  if (!arquivo) {
    vscode.window.showWarningMessage(
      'Não achei o arquivo que sobe o servidor. ' +
      'Abra-o, ou declare a entrada no forge.toml.');
    return;
  }

  if (documento?.isDirty) await documento.save();

  const { porta, host, abrirNavegador } = configuracao();
  const vitrine = ehVitrine(arquivo);
  const relativo = path.relative(raiz, arquivo) || arquivo;

  const terminal = vscode.window.createTerminal({
    name: `DataForge — servidor (${path.basename(arquivo)})`,
    iconPath: new vscode.ThemeIcon('radio-tower'),
  });
  terminal.show(true);
  terminal.sendText(`cd "${raiz}"`, true);
  terminal.sendText(
    vitrine
      ? `"${exe}" vitrine run "${relativo}" --porta=${porta} --host=${host}`
      : `"${exe}" run "${relativo}"`,
    true);

  emPe.set(raiz, { terminal, arquivo, porta, vitrine });
  atualizarIndicador();

  if (abrirNavegador) {
    // O servidor leva um instante para atender; abrir na mesma hora
    // mostra "não foi possível conectar" e ensina que está quebrado.
    await new Promise((r) => setTimeout(r, 1200));
    await vscode.env.openExternal(
      vscode.Uri.parse(`http://${host === '0.0.0.0' ? 'localhost' : host}:${porta}`));
  }
}

export async function servidorParar(raizPedida?: string) {
  const raiz = raizPedida ?? [...emPe.keys()][0];
  if (!raiz || !emPe.has(raiz)) {
    vscode.window.showInformationMessage('Nenhum servidor DataForge no ar.');
    return;
  }
  const servidor = emPe.get(raiz)!;
  // Ctrl-C antes de fechar: fechar o terminal direto deixa o processo
  // filho vivo em alguns shells, e a porta continua ocupada.
  servidor.terminal.sendText('', false);
  await new Promise((r) => setTimeout(r, 250));
  servidor.terminal.dispose();
  emPe.delete(raiz);
  atualizarIndicador();
  vscode.window.showInformationMessage(
    `Servidor parado (${path.basename(servidor.arquivo)}).`);
}

export async function servidorReiniciar() {
  const raiz = [...emPe.keys()][0];
  if (raiz) await servidorParar(raiz);
  await servidorIniciar();
}

export async function servidorAbrirNavegador() {
  const servidor = [...emPe.values()][0];
  const { porta, host } = configuracao();
  const alvo = servidor
    ? `http://localhost:${servidor.porta}`
    : `http://${host === '0.0.0.0' ? 'localhost' : host}:${porta}`;
  await vscode.env.openExternal(vscode.Uri.parse(alvo));
}

/** Chamado ao desligar a extensão: não deixar processo órfão. */
export function pararTudo() {
  for (const servidor of emPe.values()) servidor.terminal.dispose();
  emPe.clear();
}
