/**
 * Python, JavaScript e TypeScript viram DataForge, de dentro do editor.
 *
 * O `dataforge converter` já faz a tradução no terminal. O que falta a
 * quem está migrando um projeto é o passo do meio: abrir o arquivo
 * antigo, ver o que sai, e decidir. Fazer isso pelo terminal obriga a
 * sair do editor, rodar, voltar e abrir o resultado — e são dezenas de
 * arquivos.
 *
 * Três decisões:
 *
 * 1. **O resultado abre ao lado, e não por cima.** Comparar é o ponto:
 *    a tradução nunca é completa, e o que ela não traduziu está marcado
 *    com `TODO(converter)` esperando julgamento.
 * 2. **Converter uma SELEÇÃO não grava arquivo nenhum.** É o modo de
 *    tirar dúvida — "como se escreve isto aqui?" — e criar um arquivo
 *    para responder isso deixaria lixo na pasta.
 * 3. **A contagem de pendências aparece na hora.** Um conversor que diz
 *    "pronto" sobre uma tradução com doze buracos ensina a confiar no
 *    que não devia.
 */

import * as path from 'path';
import * as vscode from 'vscode';

import { exigirExecutavel, projetoDe, raizDe, rodar } from './dataforge';

/** O que o conversor sabe ler. Fora disto, ele nem é oferecido. */
const CONVERSIVEIS = new Set([
  '.py', '.js', '.mjs', '.cjs', '.jsx', '.ts', '.tsx', '.mts', '.cts',
]);

const NOME_DA_LINGUAGEM: Record<string, string> = {
  '.py': 'Python',
  '.js': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript',
  '.jsx': 'JavaScript',
  '.ts': 'TypeScript', '.tsx': 'TypeScript', '.mts': 'TypeScript',
  '.cts': 'TypeScript',
};

export function ehConversivel(documento: vscode.TextDocument): boolean {
  return CONVERSIVEIS.has(path.extname(documento.uri.fsPath).toLowerCase());
}

/** Quantos `TODO(converter)` o texto traduzido carrega. */
function pendenciasEm(texto: string): number {
  return (texto.match(/TODO\(converter\)/g) ?? []).length;
}

/**
 * Converte o arquivo aberto e mostra o resultado ao lado.
 *
 * Grava só depois de perguntar: um `.df` criado sem aviso ao lado de um
 * `.ts` que a pessoa só queria espiar é lixo que alguém vai commitar.
 */
export async function converterArquivo() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage('Abra o arquivo que você quer converter.');
    return;
  }

  const origem = editor.document;
  const extensao = path.extname(origem.uri.fsPath).toLowerCase();
  if (!CONVERSIVEIS.has(extensao)) {
    vscode.window.showWarningMessage(
      `O conversor lê .py, .js e .ts — e este arquivo é '${extensao}'.`);
    return;
  }

  const exe = await exigirExecutavel();
  if (!exe) return;
  if (origem.isDirty && !(await origem.save())) return;

  const cwd = projetoDe(origem.uri.fsPath) ?? raizDe(origem);
  const linguagem = NOME_DA_LINGUAGEM[extensao] ?? 'o arquivo';

  const traduzido = await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification,
      title: `Convertendo de ${linguagem}…` },
    async () => {
      const { saida, codigo } = await rodar(
        exe, ['converter', origem.uri.fsPath, '--seco'], 60000, cwd);
      return codigo === 0 ? saida : null;
    },
  );

  if (traduzido === null) {
    vscode.window.showErrorMessage(
      'O conversor não conseguiu ler este arquivo. ' +
      'A mensagem completa está no terminal: dataforge converter <arquivo>');
    return;
  }

  // O modo '--seco' imprime um cabeçalho de separação antes do código.
  const corpo = traduzido.replace(/^[\s\S]*?── .*? ──\n/, '').trimEnd();
  if (!corpo) {
    vscode.window.showWarningMessage('O conversor não produziu saída.');
    return;
  }

  const documento = await vscode.workspace.openTextDocument({
    content: corpo + '\n',
    language: 'dataforge',
  });
  await vscode.window.showTextDocument(documento, {
    viewColumn: vscode.ViewColumn.Beside,
    preview: false,
  });

  const pendencias = pendenciasEm(corpo);
  const destino = origem.uri.fsPath.replace(/\.[^.]+$/, '.df');
  const resumo = pendencias
    ? `${pendencias} ponto(s) precisam de você — procure por TODO(converter).`
    : 'Nada ficou pendente.';

  const escolha = await vscode.window.showInformationMessage(
    `Convertido de ${linguagem}. ${resumo}`,
    'Salvar ao lado do original', 'Só olhar');
  if (escolha !== 'Salvar ao lado do original') return;

  const uri = vscode.Uri.file(destino);
  const jaExiste = await vscode.workspace.fs.stat(uri).then(() => true,
                                                            () => false);
  if (jaExiste) {
    const sobrescrever = await vscode.window.showWarningMessage(
      `'${path.basename(destino)}' já existe. Sobrescrever?`,
      { modal: true }, 'Sobrescrever');
    if (sobrescrever !== 'Sobrescrever') return;
  }
  await vscode.workspace.fs.writeFile(uri, Buffer.from(corpo + '\n', 'utf8'));
  await vscode.window.showTextDocument(await vscode.workspace.openTextDocument(uri));
}

/**
 * Converte o trecho selecionado e mostra o resultado — sem gravar nada.
 *
 * É o modo "como se escreve isto aqui?", e a resposta não deveria
 * custar um arquivo novo na pasta.
 */
export async function converterSelecao() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.selection.isEmpty) {
    vscode.window.showWarningMessage(
      'Selecione o trecho de Python, JavaScript ou TypeScript.');
    return;
  }

  const exe = await exigirExecutavel();
  if (!exe) return;

  const trecho = editor.document.getText(editor.selection);
  const extensao = path.extname(editor.document.uri.fsPath).toLowerCase();
  const sufixo = CONVERSIVEIS.has(extensao) ? extensao : '.js';

  const temporario = vscode.Uri.joinPath(
    vscode.Uri.file(require('os').tmpdir()),
    `df-trecho-${Date.now()}${sufixo}`);
  await vscode.workspace.fs.writeFile(temporario, Buffer.from(trecho, 'utf8'));

  try {
    const { saida, codigo } = await rodar(
      exe, ['converter', temporario.fsPath, '--seco'], 30000);
    const traduzido = codigo === 0 ? saida : null;
    if (traduzido === null) {
      vscode.window.showErrorMessage(
        'O conversor não conseguiu ler o trecho selecionado. ' +
        'Um pedaço solto às vezes não é um programa válido — ' +
        'tente selecionar a função inteira.');
      return;
    }
    const corpo = traduzido
      .replace(/^[\s\S]*?── .*? ──\n/, '')
      .replace(/^\/\/ Convertido de[\s\S]*?\n\n/, '')
      .trimEnd();
    const documento = await vscode.workspace.openTextDocument({
      content: corpo + '\n',
      language: 'dataforge',
    });
    await vscode.window.showTextDocument(documento, {
      viewColumn: vscode.ViewColumn.Beside,
      preview: true,
    });
  } finally {
    await vscode.workspace.fs.delete(temporario).then(undefined, () => undefined);
  }
}

/**
 * Converte uma pasta inteira. É o caminho de quem está migrando de
 * verdade, e por isso ele mostra o relatório no terminal em vez de
 * abrir cinquenta abas.
 */
export async function converterPasta() {
  const exe = await exigirExecutavel();
  if (!exe) return;

  const escolhida = await vscode.window.showOpenDialog({
    canSelectFiles: false,
    canSelectFolders: true,
    openLabel: 'Converter esta pasta',
  });
  if (!escolhida?.length) return;

  const terminal = vscode.window.createTerminal({
    name: 'DataForge — converter',
    iconPath: new vscode.ThemeIcon('arrow-swap'),
  });
  terminal.show(true);
  terminal.sendText(`"${exe}" converter "${escolhida[0].fsPath}"`, true);
}
