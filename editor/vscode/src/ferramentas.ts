/**
 * As ferramentas do DataForge no painel lateral.
 *
 * Elas já existiam — todas — mas só na paleta de comandos, atrás de
 * `Cmd+Shift+P` e do nome exato. Quem não sabe que `dataforge big-o`
 * existe nunca vai procurá-lo pelo nome; um painel com a lista visível
 * é como se descobre que a linguagem tem análise de complexidade.
 *
 * A árvore é ESTÁTICA de propósito: nada aqui consulta o disco nem
 * roda processo ao abrir. Um painel que trava enquanto o editor
 * carrega é pior que um painel ausente.
 */

import * as vscode from 'vscode';

interface Ferramenta {
  titulo: string;
  descricao: string;
  comando: string;
  icone: string;
  /** Só faz sentido com um arquivo .df aberto. */
  precisaDeArquivo?: boolean;
}

interface Grupo {
  titulo: string;
  icone: string;
  itens: Ferramenta[];
}

const GRUPOS: Grupo[] = [
  {
    titulo: 'Executar',
    icone: 'play',
    itens: [
      { titulo: 'Rodar', descricao: 'no terminal', comando: 'dataforge.rodar', icone: 'play', precisaDeArquivo: true },
      { titulo: 'Rodar e medir', descricao: '--time', comando: 'dataforge.rodarComTempo', icone: 'watch', precisaDeArquivo: true },
      { titulo: 'Rodar com --debug', descricao: 'tokens, AST, traceback', comando: 'dataforge.rodarDepurando', icone: 'debug-alt', precisaDeArquivo: true },
      { titulo: 'Medir repetido', descricao: 'média, mediana, p95', comando: 'dataforge.medirRepetido', icone: 'graph-line', precisaDeArquivo: true },
      { titulo: 'REPL', descricao: 'console interativo', comando: 'dataforge.repl', icone: 'terminal' },
    ],
  },
  {
    titulo: 'Qualidade',
    icone: 'checklist',
    itens: [
      { titulo: 'Verificar', descricao: 'análise estática', comando: 'dataforge.verificar', icone: 'search-fuzzy', precisaDeArquivo: true },
      { titulo: 'Formatar', descricao: 'dataforge fmt', comando: 'dataforge.formatar', icone: 'symbol-color', precisaDeArquivo: true },
      { titulo: 'Testes', descricao: 'Crucible', comando: 'dataforge.testar', icone: 'beaker' },
    ],
  },
  {
    titulo: 'Complexidade',
    icone: 'graph',
    itens: [
      { titulo: 'Analisar Big-O', descricao: 'classe por ação', comando: 'dataforge.complexidade', icone: 'graph', precisaDeArquivo: true },
      { titulo: 'Tabela de referência', descricao: 'as classes e o que custam', comando: 'dataforge.escalaBigO', icone: 'list-ordered' },
      { titulo: 'Custo dos imports', descricao: 'o que cada adopt pesa', comando: 'dataforge.custo', icone: 'package', precisaDeArquivo: true },
    ],
  },
  {
    titulo: 'Projeto',
    icone: 'folder',
    itens: [
      { titulo: 'Novo projeto…', descricao: '8 modelos', comando: 'dataforge.novoProjeto', icone: 'new-folder' },
      { titulo: 'Explicar um erro', descricao: 'DF0601', comando: 'dataforge.explicarErro', icone: 'question' },
      { titulo: 'Documentação', descricao: 'abre no navegador', comando: 'dataforge.documentacao', icone: 'book' },
    ],
  },
];

type No = { tipo: 'grupo'; grupo: Grupo } | { tipo: 'ferramenta'; f: Ferramenta };

export class ArvoreDeFerramentas implements vscode.TreeDataProvider<No> {
  private mudou = new vscode.EventEmitter<No | undefined>();
  readonly onDidChangeTreeData = this.mudou.event;

  constructor() {
    // Sem arquivo .df aberto, as ferramentas que precisam de um ficam
    // apagadas em vez de sumirem: um item que desaparece parece defeito,
    // um item apagado ensina quando ele serve.
    vscode.window.onDidChangeActiveTextEditor(() => this.mudou.fire(undefined));
  }

  private temArquivo(): boolean {
    return vscode.window.activeTextEditor?.document.languageId === 'dataforge';
  }

  getTreeItem(no: No): vscode.TreeItem {
    if (no.tipo === 'grupo') {
      const item = new vscode.TreeItem(
        no.grupo.titulo,
        vscode.TreeItemCollapsibleState.Expanded,
      );
      item.iconPath = new vscode.ThemeIcon(no.grupo.icone);
      item.contextValue = 'grupo';
      return item;
    }

    const { f } = no;
    const habilitada = !f.precisaDeArquivo || this.temArquivo();
    const item = new vscode.TreeItem(f.titulo, vscode.TreeItemCollapsibleState.None);
    item.description = f.descricao;
    item.iconPath = new vscode.ThemeIcon(f.icone);
    item.contextValue = 'ferramenta';
    item.tooltip = habilitada
      ? `${f.titulo} — ${f.descricao}`
      : `${f.titulo} precisa de um arquivo .df aberto`;
    if (habilitada) {
      item.command = { command: f.comando, title: f.titulo };
    }
    return item;
  }

  getChildren(no?: No): No[] {
    if (!no) return GRUPOS.map((grupo) => ({ tipo: 'grupo', grupo }));
    if (no.tipo === 'grupo') {
      return no.grupo.itens.map((f) => ({ tipo: 'ferramenta', f }));
    }
    return [];
  }
}
