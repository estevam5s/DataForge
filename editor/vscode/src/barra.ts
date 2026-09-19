import * as vscode from 'vscode';

import { executavel, rodar } from './dataforge';

/**
 * A barra de status: o que a extensão sabe, sempre visível.
 *
 * Antes havia um botão de rodar, e mais nada. Os 56 comandos viviam na
 * paleta — e a paleta só serve a quem já sabe que o comando existe.
 *
 * Cinco itens, e cada um responde uma pergunta que se faz o tempo todo:
 *
 *     DataForge 1.0.0    qual interpretador está sendo usado?
 *     2 erros, 5 avisos  este arquivo está limpo?
 *     O(n²)             a ação onde o cursor está custa quanto?
 *     ▷                 rodar
 *     🧪 12/12          os testes passam?
 *
 * Três decisões:
 *
 * 1. **O item principal abre um menu, e não um comando.** Ele é o
 *    índice do que a extensão faz — o lugar onde se DESCOBRE, que é o
 *    que a paleta não é.
 *
 * 2. **Cada item pode ser desligado.** Uma barra cheia é uma barra que
 *    ninguém lê, e quem trabalha em tela pequena precisa escolher.
 *
 * 3. **A complexidade é a do cursor, e não do arquivo.** "Este arquivo
 *    tem um O(n²) em algum lugar" não ajuda ninguém; "a ação onde você
 *    está é O(n²)" muda o que se escreve na linha seguinte.
 */

type Config = {
  principal: boolean;
  diagnosticos: boolean;
  complexidade: boolean;
  rodar: boolean;
  testes: boolean;
};

function config(): Config {
  const c = vscode.workspace.getConfiguration('dataforge.barra');
  return {
    principal: c.get('principal', true),
    diagnosticos: c.get('diagnosticos', true),
    complexidade: c.get('complexidade', true),
    rodar: c.get('rodar', true),
    testes: c.get('testes', true),
  };
}

export class Barra implements vscode.Disposable {
  private principal: vscode.StatusBarItem;
  private diagnosticos: vscode.StatusBarItem;
  private complexidade: vscode.StatusBarItem;
  private executar: vscode.StatusBarItem;
  private testes: vscode.StatusBarItem;
  private versao = '';
  private ultimoTeste = '';
  private descartaveis: vscode.Disposable[] = [];

  constructor(private contexto: vscode.ExtensionContext) {
    // A ordem na barra é a ordem de leitura: o que é sempre verdade à
    // esquerda, o que muda a cada arquivo à direita.
    this.principal = this.item(102, 'dataforge.menu');
    this.executar = this.item(101, 'dataforge.rodar');
    this.diagnosticos = this.item(100, 'workbench.actions.view.problems');
    this.complexidade = this.item(99, 'dataforge.complexidade');
    this.testes = this.item(98, 'dataforge.testar');

    this.principal.text = '$(flame) DataForge';
    this.principal.tooltip = 'O que a extensão sabe fazer';
    this.executar.text = '$(play)';
    this.executar.tooltip = 'Rodar este arquivo (Ctrl+F5)';

    this.descartaveis.push(
      vscode.languages.onDidChangeDiagnostics(() => this.pintarDiagnosticos()),
      vscode.window.onDidChangeActiveTextEditor(() => this.atualizar()),
      vscode.window.onDidChangeTextEditorSelection((e) =>
        this.pintarComplexidade(e.textEditor)),
      vscode.workspace.onDidChangeConfiguration((e) => {
        if (e.affectsConfiguration('dataforge.barra')) this.atualizar();
      }),
    );
    void this.descobrirVersao();
  }

  private item(ordem: number, comando: string) {
    const i = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Left, ordem);
    i.command = comando;
    this.contexto.subscriptions.push(i);
    return i;
  }

  // ── atualizar ───────────────────────────────────────────

  atualizar() {
    const editor = vscode.window.activeTextEditor;
    const nosso = editor?.document.languageId === 'dataforge';
    const c = config();

    // Fora de um .df, a barra some inteira. Um item de outra linguagem
    // ocupando espaço é ruído — e a barra é compartilhada com todas as
    // outras extensões instaladas.
    for (const [item, ligado] of [
      [this.principal, c.principal],
      [this.executar, c.rodar],
      [this.diagnosticos, c.diagnosticos],
      [this.complexidade, c.complexidade],
      [this.testes, c.testes],
    ] as [vscode.StatusBarItem, boolean][]) {
      if (nosso && ligado) item.show();
      else item.hide();
    }
    if (!nosso) return;

    this.pintarDiagnosticos();
    this.pintarComplexidade(editor);
    this.pintarTestes();
  }

  private async descobrirVersao() {
    const caminho = await executavel();
    if (caminho) {
      try {
        const { saida } = await rodar(caminho, ['--version'], 5000);
        this.versao = (saida.match(/([\d]+\.[\d.]+)/)?.[1] ?? '').trim();
      } catch {
        this.versao = '';
      }
    }
    this.principal.text = this.versao
      ? `$(flame) DataForge ${this.versao}`
      : '$(flame) DataForge';
    // O caminho do interpretador na dica resolve a dúvida mais cara da
    // extensão: por que o editor discorda do terminal. Quase sempre é
    // uma instalação velha no PATH, e a resposta está aqui.
    this.principal.tooltip = new vscode.MarkdownString(
      `**DataForge${this.versao ? ` ${this.versao}` : ''}**\n\n` +
      (caminho ? `Interpretador: \`${caminho}\`\n\n`
               : '_Interpretador não encontrado._\n\n') +
      'Clique para ver tudo o que a extensão faz.');
  }

  private pintarDiagnosticos() {
    const editor = vscode.window.activeTextEditor;
    if (editor?.document.languageId !== 'dataforge') return;

    const lista = vscode.languages.getDiagnostics(editor.document.uri);
    const erros = lista.filter(
      (d) => d.severity === vscode.DiagnosticSeverity.Error).length;
    const avisos = lista.filter(
      (d) => d.severity === vscode.DiagnosticSeverity.Warning).length;

    if (!erros && !avisos) {
      this.diagnosticos.text = '$(check) sem erros';
      this.diagnosticos.tooltip = 'O analisador não achou nada neste arquivo';
      this.diagnosticos.backgroundColor = undefined;
      return;
    }
    const partes: string[] = [];
    if (erros) partes.push(`$(error) ${erros}`);
    if (avisos) partes.push(`$(warning) ${avisos}`);
    this.diagnosticos.text = partes.join(' ');
    this.diagnosticos.tooltip =
      `${erros} erro(s) e ${avisos} aviso(s) — clique para abrir o painel`;
    // O fundo vermelho só para ERRO. Um aviso que pinta a barra de
    // vermelho ensina a ignorar o vermelho.
    this.diagnosticos.backgroundColor = erros
      ? new vscode.ThemeColor('statusBarItem.errorBackground')
      : undefined;
  }

  /**
   * A complexidade da ação onde o cursor está.
   *
   * "Este arquivo tem um O(n²) em algum lugar" não ajuda ninguém.
   * "A ação onde você está é O(n²)" muda o que se escreve na linha
   * seguinte — e é por isso que ela segue o cursor.
   */
  private pintarComplexidade(editor: vscode.TextEditor | undefined) {
    if (!editor || editor.document.languageId !== 'dataforge') return;
    const achada = acaoDoCursor(editor);
    if (!achada) {
      this.complexidade.hide();
      return;
    }
    if (config().complexidade) this.complexidade.show();
    this.complexidade.text = `$(graph) ${achada.ordem}`;
    this.complexidade.tooltip = new vscode.MarkdownString(
      `**${achada.nome}** — ${achada.ordem}\n\n${achada.porque}`);
  }

  private pintarTestes() {
    if (!this.ultimoTeste) {
      this.testes.text = '$(beaker) testes';
      this.testes.tooltip = 'Rodar os testes deste projeto';
      this.testes.backgroundColor = undefined;
      return;
    }
    this.testes.text = this.ultimoTeste;
  }

  /** Chamado pelo painel de testes quando uma execução termina. */
  contarTestes(passaram: number, total: number) {
    const tudo = passaram === total && total > 0;
    this.ultimoTeste = `$(beaker) ${passaram}/${total}`;
    this.testes.tooltip = tudo
      ? 'Todos os testes passaram'
      : `${total - passaram} teste(s) falharam — clique para rodar de novo`;
    this.testes.backgroundColor = tudo
      ? undefined
      : new vscode.ThemeColor('statusBarItem.errorBackground');
    this.pintarTestes();
  }

  dispose() {
    for (const d of this.descartaveis) d.dispose();
  }
}

// ─────────────────────────────────────────────────────────────

const LACOS = /^\s*(cycle|persist|perform)\b/;

/** A ação em que o cursor está, e o custo dela. */
export function acaoDoCursor(editor: vscode.TextEditor) {
  const linhas = editor.document.getText().split('\n');
  const cursor = editor.selection.active.line;

  let inicio = -1;
  let nome = '';
  for (let i = cursor; i >= 0; i--) {
    const casou = linhas[i].match(/^\s*(?:stream\s+)?action\s+(\w+)/);
    if (casou) {
      inicio = i;
      nome = casou[1];
      break;
    }
  }
  if (inicio < 0) return null;

  const recuo = linhas[inicio].length - linhas[inicio].trimStart().length;
  let fim = linhas.length;
  for (let i = inicio + 1; i < linhas.length; i++) {
    const linha = linhas[i];
    if (!linha.trim()) continue;
    const meu = linha.length - linha.trimStart().length;
    if (meu <= recuo) {
      fim = i;
      break;
    }
  }
  if (cursor > fim) return null;

  // A profundidade de laços ANINHADOS. É uma leitura de recuo, e não
  // uma análise: ela erra para menos num laço dentro de uma chamada, e
  // acerta no caso que importa — o laço dentro do laço, escrito ali.
  let profundidade = 0;
  let maxima = 0;
  const pilha: number[] = [];
  for (let i = inicio + 1; i < fim; i++) {
    const linha = linhas[i];
    if (!linha.trim()) continue;
    const meu = linha.length - linha.trimStart().length;
    while (pilha.length && meu <= pilha[pilha.length - 1]) {
      pilha.pop();
      profundidade--;
    }
    if (LACOS.test(linha)) {
      pilha.push(meu);
      profundidade++;
      maxima = Math.max(maxima, profundidade);
    }
  }

  const recursiva = new RegExp(`\\b${nome}\\s*\\(`).test(
    linhas.slice(inicio + 1, fim).join('\n'));

  const ordem = recursiva && maxima === 0 ? 'O(n)?'
    : maxima === 0 ? 'O(1)'
    : maxima === 1 ? 'O(n)'
    : maxima === 2 ? 'O(n²)'
    : `O(n^${maxima})`;

  const porque = recursiva && maxima === 0
    ? 'A ação chama a si mesma: o custo depende de quantas vezes.'
    : maxima === 0
    ? 'Nenhum laço: o custo não cresce com o tamanho da entrada.'
    : maxima === 1
    ? 'Um laço: o custo cresce junto com a entrada.'
    : `${maxima} laços aninhados. Dobrar a entrada multiplica o ` +
      `trabalho por ${2 ** maxima}.`;

  return { nome, ordem, porque, inicio, fim };
}

/** O menu do item principal: o índice do que a extensão faz. */
export async function abrirMenu() {
  const grupos: Array<{ rotulo: string; itens: Array<[string, string, string]> }> = [
    {
      rotulo: 'Rodar',
      itens: [
        ['$(play) Rodar este arquivo', 'dataforge.rodar', 'Ctrl+F5'],
        ['$(watch) Rodar e medir o tempo', 'dataforge.rodarComTempo', ''],
        ['$(bug) Rodar com --debug', 'dataforge.rodarDepurando', ''],
        ['$(debug-alt) Depurar no editor', 'dataforge.depurarNoEditor', 'F5'],
        ['$(terminal) Abrir o REPL', 'dataforge.repl', ''],
      ],
    },
    {
      rotulo: 'Conferir',
      itens: [
        ['$(check) Analisar (check)', 'dataforge.verificar', ''],
        ['$(law) Lint', 'dataforge.lint', ''],
        ['$(wand) Formatar', 'dataforge.formatar', ''],
        ['$(tools) Corrigir o que dá', 'dataforge.corrigir', ''],
        ['$(list-unordered) Listar os erros da linguagem', 'dataforge.listarErros', ''],
      ],
    },
    {
      rotulo: 'Testar',
      itens: [
        ['$(beaker) Rodar os testes', 'dataforge.testar', ''],
        ['$(shield) Cobertura', 'dataforge.cobertura', ''],
        ['$(dashboard) Medir desempenho', 'dataforge.medirDesempenho', ''],
      ],
    },
    {
      rotulo: 'Entender',
      itens: [
        ['$(graph) Complexidade deste arquivo', 'dataforge.complexidade', ''],
        ['$(symbol-numeric) Escala Big-O', 'dataforge.escalaBigO', ''],
        ['$(flame) Perfilar', 'dataforge.perfilar', ''],
        ['$(list-tree) Ver a AST', 'dataforge.verAst', ''],
        ['$(symbol-keyword) Ver os tokens', 'dataforge.verTokens', ''],
        ['$(graph-line) Estatísticas do projeto', 'dataforge.verEstatisticas', ''],
      ],
    },
    {
      rotulo: 'Projeto',
      itens: [
        ['$(new-folder) Novo projeto', 'dataforge.novoProjeto', ''],
        ['$(info) Informações do projeto', 'dataforge.infoDoProjeto', ''],
        ['$(package) Instalar dependências', 'dataforge.instalarPacotes', ''],
        ['$(add) Acrescentar pacote', 'dataforge.acrescentarPacote', ''],
        ['$(search) Procurar pacote', 'dataforge.procurarPacote', ''],
        ['$(cloud) DevOps: gerar artefatos', 'dataforge.devops', ''],
        ['$(pulse) DevOps: doctor', 'dataforge.devopsDoctor', ''],
      ],
    },
    {
      rotulo: 'Ajuda',
      itens: [
        ['$(book) Documentação', 'dataforge.documentacao', ''],
        ['$(question) Por que este erro?', 'dataforge.porQue', ''],
        ['$(refresh) Reiniciar o servidor de linguagem',
         'dataforge.reiniciarServidor', ''],
      ],
    },
  ];

  const opcoes: vscode.QuickPickItem[] = [];
  const comandoDe = new Map<string, string>();
  for (const grupo of grupos) {
    opcoes.push({ label: grupo.rotulo, kind: vscode.QuickPickItemKind.Separator });
    for (const [rotulo, comando, atalho] of grupo.itens) {
      opcoes.push({ label: rotulo, description: atalho });
      comandoDe.set(rotulo, comando);
    }
  }

  const escolhido = await vscode.window.showQuickPick(opcoes, {
    title: 'DataForge',
    placeHolder: 'O que você quer fazer?',
    matchOnDescription: true,
  });
  if (escolhido && comandoDe.has(escolhido.label)) {
    await vscode.commands.executeCommand(comandoDe.get(escolhido.label)!);
  }
}
