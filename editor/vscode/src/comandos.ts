/**
 * Os comandos que faltavam entre a CLI e o editor.
 *
 * A CLI tem 40 comandos; a extensão expunha 20. Os que faltavam não
 * eram menos úteis — eram os que ninguém descobre, porque descobrir um
 * comando de CLI exige ler `--help`, e ler `--help` exige já suspeitar
 * que ele existe.
 *
 * Nem todos entram: `lsp` é iniciado pela própria extensão, e `help`
 * não faz sentido numa paleta que já lista tudo.
 */

import * as vscode from 'vscode';

import { exigirExecutavel, raizDe, rodar } from './dataforge';
import { rodarNoTerminal } from './executar';

/** Roda e mostra a saída num documento novo, sem sujar o terminal. */
async function mostrar(
  args: string[],
  titulo: string,
  linguagem = 'plaintext',
  cwd?: string,
): Promise<void> {
  const binario = await exigirExecutavel();
  if (!binario) return;

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Window, title: `DataForge: ${titulo}` },
    async () => {
      const r = await rodar(binario, args, 30000, cwd);
      const texto = (r.saida || r.erro || '(sem saída)').trimEnd();
      const doc = await vscode.workspace.openTextDocument({
        content: texto,
        language: linguagem,
      });
      // 'Beside' e não 'Active': o que se olha é a saída COM o código
      // do lado, e substituir o arquivo obrigaria a voltar.
      await vscode.window.showTextDocument(doc, {
        viewColumn: vscode.ViewColumn.Beside,
        preview: true,
      });
    },
  );
}

function documentoAtual(): vscode.TextDocument | undefined {
  const doc = vscode.window.activeTextEditor?.document;
  if (!doc || doc.languageId !== 'dataforge') {
    vscode.window.showWarningMessage('DataForge: abra um arquivo .df primeiro.');
    return undefined;
  }
  return doc;
}

async function salvarSePreciso(doc: vscode.TextDocument): Promise<void> {
  // A CLI lê do DISCO. Sem salvar, ela analisaria a versão anterior — e
  // o resultado apontaria para linhas que já mudaram.
  if (doc.isDirty) await doc.save();
}

// ── inspecionar o arquivo ──────────────────────────────────

export async function verTokens(): Promise<void> {
  const doc = documentoAtual();
  if (!doc) return;
  await salvarSePreciso(doc);
  await mostrar(['tokens', doc.fileName], 'tokens');
}

export async function verAst(): Promise<void> {
  const doc = documentoAtual();
  if (!doc) return;
  await salvarSePreciso(doc);
  await mostrar(['ast', doc.fileName], 'árvore sintática');
}

export async function verEstatisticas(): Promise<void> {
  const doc = documentoAtual();
  if (!doc) return;
  await salvarSePreciso(doc);
  await mostrar(['stats', raizDe(doc)], 'inventário', 'plaintext', raizDe(doc));
}

export async function perfilar(): Promise<void> {
  const doc = documentoAtual();
  if (!doc) return;
  await salvarSePreciso(doc);
  await mostrar(['profile', doc.fileName], 'tempo por ação');
}

export async function porQue(): Promise<void> {
  const escolha = await vscode.window.showInputBox({
    prompt: 'Por que isto é assim, no DataForge?',
    placeHolder: 'yield, ~/, monitor, given…',
  });
  if (!escolha) return;
  await mostrar(['why', escolha], `por que '${escolha}'`, 'markdown');
}

// ── qualidade ──────────────────────────────────────────────

export async function lint(): Promise<void> {
  const doc = documentoAtual();
  if (!doc) return;
  await salvarSePreciso(doc);
  await mostrar(['lint', doc.fileName], 'lint');
}

export async function corrigir(): Promise<void> {
  const doc = documentoAtual();
  if (!doc) return;
  await salvarSePreciso(doc);
  const binario = await exigirExecutavel();
  if (!binario) return;
  const r = await rodar(binario, ['fix', doc.fileName], 30000, raizDe(doc));
  vscode.window.showInformationMessage(
    `DataForge: ${(r.saida || 'nada a corrigir').split('\n')[0]}`);
}

export async function gerarDoc(): Promise<void> {
  const doc = documentoAtual();
  if (!doc) return;
  await salvarSePreciso(doc);
  await mostrar(['doc', doc.fileName], 'documentação', 'markdown');
}

export async function crucible(): Promise<void> {
  const doc = documentoAtual();
  if (!doc) return;
  await rodarNoTerminal(doc, ['crucible']);
}

// ── depurar ────────────────────────────────────────────────

export async function depurar(): Promise<void> {
  const doc = documentoAtual();
  if (!doc) return;
  await salvarSePreciso(doc);

  // As paradas do editor viram '--parar': é o que liga o que a pessoa
  // clicou na margem ao depurador que roda no terminal.
  const paradas = vscode.debug.breakpoints
    .filter((b): b is vscode.SourceBreakpoint =>
      b instanceof vscode.SourceBreakpoint)
    .filter((b) => b.location.uri.fsPath === doc.fileName)
    .map((b) => b.location.range.start.line + 1);

  const args = paradas.length ? [`--parar=${paradas.join(',')}`] : [];
  await rodarNoTerminal(doc, ['debug', ...args]);
}

// ── pacotes ────────────────────────────────────────────────

export async function instalarPacotes(): Promise<void> {
  const doc = documentoAtual();
  if (!doc) return;
  await rodarNoTerminal(doc, ['install']);
}

export async function acrescentarPacote(): Promise<void> {
  const nome = await vscode.window.showInputBox({
    prompt: 'Qual pacote?',
    placeHolder: 'validador, tabela, datas, cofre…',
  });
  if (!nome) return;
  const doc = documentoAtual();
  if (!doc) return;
  await rodarNoTerminal(doc, ['add', nome]);
}

export async function procurarPacote(): Promise<void> {
  const termo = await vscode.window.showInputBox({
    prompt: 'Procurar no registro',
    placeHolder: 'validação, data, tabela…',
  });
  if (!termo) return;
  await mostrar(['search', termo], `pacotes: ${termo}`);
}

export async function listarPacotes(): Promise<void> {
  const raiz = vscode.workspace.workspaceFolders?.[0].uri.fsPath;
  await mostrar(['list'], 'pacotes instalados', 'plaintext', raiz);
}

export async function pacotesDesatualizados(): Promise<void> {
  const raiz = vscode.workspace.workspaceFolders?.[0].uri.fsPath;
  await mostrar(['outdated'], 'pacotes desatualizados', 'plaintext', raiz);
}

export async function arvoreDeDependencias(): Promise<void> {
  const raiz = vscode.workspace.workspaceFolders?.[0].uri.fsPath;
  await mostrar(['tree'], 'árvore de dependências', 'plaintext', raiz);
}

// ── projeto ────────────────────────────────────────────────

export async function infoDoProjeto(): Promise<void> {
  const raiz = vscode.workspace.workspaceFolders?.[0].uri.fsPath;
  await mostrar(['info'], 'o manifesto', 'plaintext', raiz);
}

export async function limpar(): Promise<void> {
  const raiz = vscode.workspace.workspaceFolders?.[0].uri.fsPath;
  const escolha = await vscode.window.showWarningMessage(
    'Apagar caches e artefatos de build?', { modal: true }, 'Apagar');
  if (escolha !== 'Apagar') return;
  await mostrar(['clean'], 'limpeza', 'plaintext', raiz);
}

export async function listarErros(): Promise<void> {
  await mostrar(['erros'], 'os códigos de erro', 'markdown');
}

export async function avaliar(): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  const selecao = editor?.document.getText(editor.selection).trim();
  const expressao = selecao || await vscode.window.showInputBox({
    prompt: 'Avaliar uma expressão DataForge',
    placeHolder: '2 + 2  ·  [1,2,3] >> morph n: n * 2',
  });
  if (!expressao) return;
  const binario = await exigirExecutavel();
  if (!binario) return;
  const r = await rodar(binario, ['eval', expressao]);
  const saida = (r.saida || r.erro || '').trim();
  vscode.window.showInformationMessage(`${expressao} = ${saida}`);
}

export async function medirDesempenho(): Promise<void> {
  const doc = documentoAtual();
  if (!doc) return;
  await salvarSePreciso(doc);
  await rodarNoTerminal(doc, ['bench']);
}

export async function observarArquivo(): Promise<void> {
  const doc = documentoAtual();
  if (!doc) return;
  await salvarSePreciso(doc);
  await rodarNoTerminal(doc, ['watch']);
}
