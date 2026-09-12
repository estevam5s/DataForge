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
      { titulo: 'Depurar', descricao: 'breakpoints, pilha e variáveis', comando: 'dataforge.depurarNoEditor', icone: 'debug-alt', precisaDeArquivo: true },
      { titulo: 'Depurar no terminal', descricao: 'passo a passo, serve por ssh', comando: 'dataforge.depurar', icone: 'terminal', precisaDeArquivo: true },
      { titulo: 'Observar', descricao: 'reexecuta ao salvar', comando: 'dataforge.observarArquivo', icone: 'eye', precisaDeArquivo: true },
      { titulo: 'Avaliar', descricao: 'uma expressão', comando: 'dataforge.avaliar', icone: 'symbol-operator' },
    ],
  },
  {
    titulo: 'Qualidade',
    icone: 'checklist',
    itens: [
      { titulo: 'Verificar', descricao: 'análise estática', comando: 'dataforge.verificar', icone: 'search-fuzzy', precisaDeArquivo: true },
      { titulo: 'Formatar', descricao: 'dataforge fmt', comando: 'dataforge.formatar', icone: 'symbol-color', precisaDeArquivo: true },
      { titulo: 'Testes', descricao: 'dataforge test', comando: 'dataforge.testar', icone: 'beaker' },
      { titulo: 'Crucible', descricao: 'o framework de testes', comando: 'dataforge.crucible', icone: 'beaker', precisaDeArquivo: true },
      { titulo: 'Lint', descricao: 'estilo e higiene', comando: 'dataforge.lint', icone: 'checklist', precisaDeArquivo: true },
      { titulo: 'Corrigir', descricao: 'o que dá para corrigir', comando: 'dataforge.corrigir', icone: 'wand', precisaDeArquivo: true },
      { titulo: 'Gerar doc', descricao: 'dos comentários', comando: 'dataforge.gerarDoc', icone: 'book', precisaDeArquivo: true },
      { titulo: 'Cobertura', descricao: 'o que os testes NÃO rodaram', comando: 'dataforge.cobertura', icone: 'shield', precisaDeArquivo: true },
      { titulo: 'Cobertura mínima…', descricao: 'reprova abaixo de N%', comando: 'dataforge.coberturaMinima', icone: 'verified', precisaDeArquivo: true },
    ],
  },
  {
    titulo: 'Vitrine',
    icone: 'dashboard',
    itens: [
      { titulo: 'Subir (dev)', descricao: 'recarrega ao salvar', comando: 'dataforge.vitrineDev', icone: 'play-circle', precisaDeArquivo: true },
      { titulo: 'Por que não sobe?', descricao: 'diagnóstico', comando: 'dataforge.vitrineDoctor', icone: 'pulse', precisaDeArquivo: true },
    ],
  },
  {
    titulo: 'DevOps',
    icone: 'rocket',
    itens: [
      { titulo: 'Gerar artefatos…', descricao: 'Docker, CI, k8s, nginx', comando: 'dataforge.devops', icone: 'rocket' },
      { titulo: 'O que falta para subir?', descricao: 'devops doctor', comando: 'dataforge.devopsDoctor', icone: 'checklist' },
    ],
  },
  {
    titulo: 'Complexidade',
    icone: 'graph',
    itens: [
      { titulo: 'Analisar Big-O', descricao: 'classe por ação', comando: 'dataforge.complexidade', icone: 'graph', precisaDeArquivo: true },
      { titulo: 'Tabela de referência', descricao: 'as classes e o que custam', comando: 'dataforge.escalaBigO', icone: 'list-ordered' },
      { titulo: 'Custo dos imports', descricao: 'o que cada adopt pesa', comando: 'dataforge.custo', icone: 'package', precisaDeArquivo: true },
      { titulo: 'Perfilar', descricao: 'tempo por ação', comando: 'dataforge.perfilar', icone: 'dashboard', precisaDeArquivo: true },
      { titulo: 'Medir (bench)', descricao: 'desempenho repetido', comando: 'dataforge.medirDesempenho', icone: 'watch', precisaDeArquivo: true },
    ],
  },
  {
    titulo: 'Pacotes',
    icone: 'package',
    itens: [
      { titulo: 'Instalar', descricao: 'o forge.toml inteiro', comando: 'dataforge.instalarPacotes', icone: 'cloud-download', precisaDeArquivo: true },
      { titulo: 'Acrescentar…', descricao: 'um pacote novo', comando: 'dataforge.acrescentarPacote', icone: 'add', precisaDeArquivo: true },
      { titulo: 'Procurar…', descricao: 'no registro', comando: 'dataforge.procurarPacote', icone: 'search' },
      { titulo: 'Instalados', descricao: 'o que já está aqui', comando: 'dataforge.listarPacotes', icone: 'list-flat' },
      { titulo: 'Desatualizados', descricao: 'o que dá para subir', comando: 'dataforge.pacotesDesatualizados', icone: 'arrow-up' },
      { titulo: 'Árvore', descricao: 'quem depende de quem', comando: 'dataforge.arvoreDeDependencias', icone: 'type-hierarchy' },
    ],
  },
  {
    titulo: 'Inspecionar',
    icone: 'search',
    itens: [
      { titulo: 'Tokens', descricao: 'o que o lexer viu', comando: 'dataforge.verTokens', icone: 'symbol-key', precisaDeArquivo: true },
      { titulo: 'Árvore sintática', descricao: 'a AST', comando: 'dataforge.verAst', icone: 'list-tree', precisaDeArquivo: true },
      { titulo: 'Inventário', descricao: 'ações, blueprints, o mais longo', comando: 'dataforge.verEstatisticas', icone: 'graph-scatter', precisaDeArquivo: true },
      { titulo: 'Por que isto é assim?', descricao: 'as decisões da linguagem', comando: 'dataforge.porQue', icone: 'lightbulb' },
    ],
  },
  {
    titulo: 'Projeto',
    icone: 'folder',
    itens: [
      { titulo: 'Novo projeto…', descricao: '8 modelos', comando: 'dataforge.novoProjeto', icone: 'new-folder' },
      { titulo: 'Explicar um erro', descricao: 'DF0601', comando: 'dataforge.explicarErro', icone: 'question' },
      { titulo: 'Ver o forge.toml', descricao: 'o manifesto', comando: 'dataforge.infoDoProjeto', icone: 'file-code' },
      { titulo: 'Códigos de erro', descricao: 'todos, com explicação', comando: 'dataforge.listarErros', icone: 'error' },
      { titulo: 'Limpar', descricao: 'caches e artefatos', comando: 'dataforge.limpar', icone: 'trash' },
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
