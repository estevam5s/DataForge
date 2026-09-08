/**
 * DataForge no VS Code.
 *
 * A extensão não reimplementa nada da linguagem: ela chama a CLI e
 * desenha o resultado. Isso é o que garante que o sublinhado no editor,
 * a saída do terminal e o que quebra o CI sejam sempre a mesma coisa.
 *
 * O que ela acrescenta é o que só faz sentido dentro do editor:
 * complexidade acima de cada ação, custo ao lado de cada import, um
 * botão para rodar, e o painel de conexões.
 */

import * as vscode from 'vscode';
import { anotar } from './custo';
import { ArvoreDeConexoes, Item } from './conexoes';
import { LenteDeComplexidade, acoesDe, explicar } from './complexidade';
import { criarProjeto } from './projetos';
import { esquecerExecutavel, exigirExecutavel, raizDe, rodar } from './dataforge';
import { Verificador } from './diagnosticos';
import {
  fecharTerminal,
  formatarTempo,
  medirRepetido,
  obterCanal,
  rodarEMostrarTempo,
  rodarNoTerminal,
} from './executar';

let barra: vscode.StatusBarItem;

export function activate(contexto: vscode.ExtensionContext) {
  const verificador = new Verificador(contexto);
  const lente = new LenteDeComplexidade();
  const conexoes = new ArvoreDeConexoes(contexto);

  // ── barra de status: o botão de rodar ──
  barra = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  barra.command = 'dataforge.rodar';
  barra.text = '$(play) DataForge';
  barra.tooltip = 'Rodar este arquivo (Ctrl+F5)';
  contexto.subscriptions.push(barra);
  atualizarBarra(vscode.window.activeTextEditor);

  // ── comandos ──
  const comandos: [string, (...a: any[]) => any][] = [
    ['dataforge.rodar', () => comEditor((d) => rodarNoTerminal(d))],
    ['dataforge.rodarComTempo', () => comEditor((d) => rodarEMostrarTempo(d))],
    ['dataforge.rodarDepurando', () => comEditor((d) => rodarNoTerminal(d, ['--debug']))],
    ['dataforge.medirRepetido', () => comEditor((d) => medirRepetido(d))],
    ['dataforge.verificar', () => comEditor((d) => verificador.verificar(d))],
    ['dataforge.formatar', () => comEditor(formatar)],
    ['dataforge.testar', () => comEditor((d) => rodarNoTerminal(d, ['crucible']))],
    ['dataforge.complexidade', () => comEditor(mostrarComplexidade)],
    ['dataforge.explicarComplexidade', (a) => explicar(a)],
    ['dataforge.escalaBigO', mostrarEscala],
    ['dataforge.custo', () => anotar(vscode.window.activeTextEditor)],
    ['dataforge.novoProjeto', criarProjeto],
    ['dataforge.repl', abrirRepl],
    ['dataforge.explicarErro', explicarErro],
    ['dataforge.conexoes.adicionar', () => conexoes.adicionar()],
    ['dataforge.conexoes.atualizar', () => conexoes.atualizar()],
    ['dataforge.conexoes.remover', (i: Item) => conexoes.remover(i)],
    ['dataforge.conexoes.testar', (i: Item) => i.conexao && conexoes.testar(i.conexao)],
    ['dataforge.conexoes.inserir', (i: Item) => conexoes.inserirCodigo(i)],
    ['dataforge.documentacao', () =>
      vscode.env.openExternal(
        vscode.Uri.parse('https://dataforge-lang.vercel.app/docs'))],
  ];
  for (const [nome, fn] of comandos) {
    contexto.subscriptions.push(vscode.commands.registerCommand(nome, fn));
  }

  // ── análise contínua ──
  contexto.subscriptions.push(
    vscode.languages.registerCodeLensProvider(
      { language: 'dataforge' },
      lente,
    ),
    vscode.languages.registerHoverProvider({ language: 'dataforge' }, {
      provideHover: (documento, posicao) => hoverDeComplexidade(documento, posicao),
    }),
    vscode.window.registerTreeDataProvider('dataforgeConexoes', conexoes),

    vscode.workspace.onDidSaveTextDocument((d) => {
      verificador.agendar(d, 0);
      lente.atualizar();
      if (vscode.window.activeTextEditor?.document === d) {
        void anotar(vscode.window.activeTextEditor);
      }
    }),
    vscode.workspace.onDidChangeTextDocument((e) =>
      verificador.agendar(e.document)),
    vscode.workspace.onDidCloseTextDocument((d) => verificador.limpar(d)),
    vscode.window.onDidChangeActiveTextEditor((e) => {
      atualizarBarra(e);
      if (e) {
        verificador.agendar(e.document, 0);
        void anotar(e);
      }
    }),
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration('dataforge.caminho')) esquecerExecutavel();
      lente.atualizar();
      void anotar(vscode.window.activeTextEditor);
    }),
    vscode.window.onDidCloseTerminal(() => fecharTerminal()),
  );

  // Analisa o que já está aberto: sem isto, o primeiro arquivo da
  // sessão fica sem sublinhado até alguém digitar nele.
  if (vscode.window.activeTextEditor) {
    verificador.agendar(vscode.window.activeTextEditor.document, 0);
    void anotar(vscode.window.activeTextEditor);
  }

  void avisarSeFaltaOExecutavel();
}

export function deactivate() {
  fecharTerminal();
}

// ─────────────────────────────────────────────────────────────

function comEditor(acao: (d: vscode.TextDocument) => any) {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== 'dataforge') {
    vscode.window.showInformationMessage('Abra um arquivo .df primeiro.');
    return;
  }
  return acao(editor.document);
}

function atualizarBarra(editor: vscode.TextEditor | undefined) {
  if (editor?.document.languageId === 'dataforge') barra.show();
  else barra.hide();
}

async function avisarSeFaltaOExecutavel() {
  // Só avisa se houver um .df aberto: quem instalou a extensão e ainda
  // não usou a linguagem não precisa de um popup.
  if (vscode.window.activeTextEditor?.document.languageId !== 'dataforge') return;
  await exigirExecutavel();
}

async function formatar(documento: vscode.TextDocument) {
  const exe = await exigirExecutavel();
  if (!exe) return;
  await documento.save();
  await rodar(exe, ['fmt', documento.uri.fsPath], 20000, raizDe(documento));
  vscode.window.setStatusBarMessage('DataForge: formatado', 3000);
}

async function abrirRepl() {
  const exe = await exigirExecutavel();
  if (!exe) return;
  const t = vscode.window.createTerminal({
    name: 'DataForge REPL',
    iconPath: new vscode.ThemeIcon('terminal'),
  });
  t.show();
  t.sendText(`${exe} repl`, true);
}

async function mostrarComplexidade(documento: vscode.TextDocument) {
  const exe = await exigirExecutavel();
  if (!exe) return;
  await documento.save();

  const saida = obterCanal();
  saida.show(true);
  const { saida: texto } = await rodar(
    exe,
    ['big-o', documento.uri.fsPath, '-v', '--no-color'],
    30000,
    raizDe(documento),
  );
  saida.appendLine('');
  saida.appendLine(texto.trimEnd());
}

async function mostrarEscala() {
  const exe = await exigirExecutavel();
  if (!exe) return;
  const saida = obterCanal();
  saida.show(true);
  const { saida: texto } = await rodar(exe, ['big-o', '--escala', '--no-color']);
  saida.appendLine(texto.trimEnd());
}

/** O código do erro sob o cursor, explicado. */
async function explicarErro() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) return;

  const selecionado = editor.document.getText(editor.selection).trim();
  const codigo =
    /^DF\d{4}$/i.test(selecionado)
      ? selecionado
      : await vscode.window.showInputBox({
          title: 'Código do erro',
          placeHolder: 'DF0601, ou o nome da classe (KeyError)',
        });
  if (!codigo) return;

  const exe = await exigirExecutavel();
  if (!exe) return;

  const saida = obterCanal();
  saida.show(true);
  const { saida: texto } = await rodar(exe, ['explain', codigo, '--no-color']);
  saida.appendLine(texto.trimEnd());
}

/** O hover mostra o porquê da complexidade da ação sob o cursor. */
function hoverDeComplexidade(
  documento: vscode.TextDocument,
  posicao: vscode.Position,
): vscode.Hover | undefined {
  const acoes = acoesDe(documento.uri);
  const acao = acoes.find((a) => a.linha - 1 === posicao.line);
  if (!acao) return undefined;

  const md = new vscode.MarkdownString();
  md.appendMarkdown(`**${acao.tempo.notacao}** de tempo — ${acao.tempo.nome}\n\n`);
  md.appendMarkdown(`**${acao.espaco.notacao}** de espaço\n\n`);
  if (acao.tempo.motivos.length) {
    acao.tempo.motivos.forEach((m) => md.appendMarkdown(`- ${m}\n`));
  }
  for (const aviso of acao.avisos) {
    md.appendMarkdown(`\n⚠ **${aviso.texto}**\n\n${aviso.sugestao}\n`);
  }
  md.isTrusted = true;
  return new vscode.Hover(md);
}
