/**
 * Conexões de banco de dados no painel lateral.
 *
 * Guarda as URLs configuradas, testa cada uma e lista as tabelas —
 * tudo pelo `Forge`, o mesmo módulo que o programa usa. Assim uma
 * conexão que funciona aqui funciona no código, e vice-versa.
 *
 * ─── Senha ──────────────────────────────────────────────────
 *
 * A URL vai para as configurações do VS Code, que ficam em texto
 * claro num arquivo JSON — e que muita gente versiona. Por isso a
 * senha é guardada no cofre do sistema (`SecretStorage`) e a URL
 * salva com um marcador no lugar dela.
 */

import * as vscode from 'vscode';
import { exigirExecutavel, rodar } from './dataforge';

export interface Conexao {
  nome: string;
  url: string;
}

const CHAVE = 'dataforge.conexoes';
const MARCA_SENHA = '***';

/** Troca a senha da URL pelo marcador, para o que é salvo não vazá-la. */
function semSenha(url: string): string {
  return url.replace(/:\/\/([^:@/]+):([^@]+)@/, `://$1:${MARCA_SENHA}@`);
}

function temMarca(url: string): boolean {
  return url.includes(`:${MARCA_SENHA}@`);
}

export class ArvoreDeConexoes implements vscode.TreeDataProvider<Item> {
  private mudou = new vscode.EventEmitter<Item | undefined>();
  readonly onDidChangeTreeData = this.mudou.event;

  constructor(private contexto: vscode.ExtensionContext) {}

  atualizar() {
    this.mudou.fire(undefined);
  }

  getTreeItem(item: Item): vscode.TreeItem {
    return item;
  }

  async getChildren(pai?: Item): Promise<Item[]> {
    if (!pai) {
      const conexoes = this.contexto.globalState.get<Conexao[]>(CHAVE, []);
      if (!conexoes.length) {
        const vazio = new Item(
          'Nenhuma conexão',
          vscode.TreeItemCollapsibleState.None,
        );
        vazio.description = 'clique em + para adicionar';
        vazio.iconPath = new vscode.ThemeIcon('info');
        return [vazio];
      }
      return conexoes.map((c) => {
        const item = new Item(
          c.nome,
          vscode.TreeItemCollapsibleState.Collapsed,
        );
        item.description = semSenha(c.url);
        item.contextValue = 'conexao';
        item.iconPath = new vscode.ThemeIcon('database');
        item.conexao = c;
        return item;
      });
    }

    if (pai.conexao) return this.tabelas(pai.conexao);
    return [];
  }

  private async tabelas(conexao: Conexao): Promise<Item[]> {
    const url = await this.urlCompleta(conexao);
    const exe = await exigirExecutavel();
    if (!exe || !url) return [];

    // Um programa de três linhas em DataForge lista as tabelas. Usar a
    // própria linguagem aqui é o que garante que o painel e o código
    // vejam o mesmo banco.
    const programa = [
      'adopt Forge',
      `db := Forge.conectar("${url.replace(/"/g, '\\"')}")`,
      'cycle t in Forge.tabelas(db):',
      '    out t',
    ].join('\n');

    try {
      const { saida, codigo } = await rodar(exe, ['eval', programa], 20000);
      if (codigo !== 0) {
        const erro = new Item('não conectou', vscode.TreeItemCollapsibleState.None);
        erro.iconPath = new vscode.ThemeIcon('error');
        return [erro];
      }
      return saida
        .split('\n')
        .map((l) => l.trim())
        .filter(Boolean)
        .map((nome) => {
          const item = new Item(nome, vscode.TreeItemCollapsibleState.None);
          item.iconPath = new vscode.ThemeIcon('table');
          item.contextValue = 'tabela';
          item.tabela = nome;
          item.conexao = conexao;
          return item;
        });
    } catch {
      return [];
    }
  }

  /** A URL com a senha vinda do cofre. */
  async urlCompleta(conexao: Conexao): Promise<string> {
    if (!temMarca(conexao.url)) return conexao.url;
    const senha = await this.contexto.secrets.get(`${CHAVE}:${conexao.nome}`);
    if (!senha) return conexao.url;
    return conexao.url.replace(`:${MARCA_SENHA}@`, `:${senha}@`);
  }

  async adicionar() {
    const nome = await vscode.window.showInputBox({
      title: 'Nome da conexão',
      placeHolder: 'produção, local, staging…',
    });
    if (!nome) return;

    const url = await vscode.window.showInputBox({
      title: 'URL',
      placeHolder: 'postgres://usuario:senha@localhost:5432/app',
      prompt: 'aceita postgres, mysql, mariadb, mongodb, redis e sqlite',
      validateInput: (v) =>
        v.includes('://') || v.endsWith('.db') || v === ':memory:'
          ? null
          : 'uma URL, um caminho .db ou :memory:',
    });
    if (!url) return;

    // Separa a senha ANTES de guardar: o globalState vai para disco em
    // texto claro.
    const senha = /:\/\/[^:@/]+:([^@]+)@/.exec(url)?.[1];
    if (senha) {
      await this.contexto.secrets.store(`${CHAVE}:${nome}`, senha);
    }

    const conexoes = this.contexto.globalState.get<Conexao[]>(CHAVE, []);
    conexoes.push({ nome, url: senha ? semSenha(url) : url });
    await this.contexto.globalState.update(CHAVE, conexoes);
    this.atualizar();

    void this.testar({ nome, url: senha ? semSenha(url) : url });
  }

  async remover(item: Item) {
    if (!item.conexao) return;
    const conexoes = this.contexto.globalState
      .get<Conexao[]>(CHAVE, [])
      .filter((c) => c.nome !== item.conexao!.nome);
    await this.contexto.globalState.update(CHAVE, conexoes);
    await this.contexto.secrets.delete(`${CHAVE}:${item.conexao.nome}`);
    this.atualizar();
  }

  async testar(conexao: Conexao) {
    const exe = await exigirExecutavel();
    if (!exe) return;

    const url = await this.urlCompleta(conexao);
    const programa = [
      'adopt Forge',
      `db := Forge.conectar("${url.replace(/"/g, '\\"')}")`,
      'out "ok", Forge.versao(db)',
    ].join('\n');

    await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: `Testando ${conexao.nome}…` },
      async () => {
        try {
          const { saida, erro, codigo } = await rodar(exe, ['eval', programa], 20000);
          if (codigo === 0) {
            vscode.window.showInformationMessage(
              `${conexao.nome}: ${saida.trim() || 'conectou'}`,
            );
          } else {
            const primeira = (erro || saida).split('\n').find((l) => l.trim());
            vscode.window.showErrorMessage(
              `${conexao.nome} não conectou. ${primeira ?? ''}`,
            );
          }
        } catch (e) {
          vscode.window.showErrorMessage(`${conexao.nome}: ${e}`);
        }
      },
    );
  }

  /** Insere no editor o código que abre esta conexão. */
  async inserirCodigo(item: Item) {
    if (!item.conexao) return;
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    const linhas = item.tabela
      ? [
          `linhas := Forge.de(db, "${item.tabela}")`,
          `    .limite(20)`,
          `    .buscar()`,
        ]
      : [
          `adopt Forge`,
          ``,
          `db := Forge.conectar(ambiente("DATABASE_URL"))`,
        ];

    await editor.edit((edicao) => {
      edicao.insert(editor.selection.active, linhas.join('\n') + '\n');
    });
  }
}

export class Item extends vscode.TreeItem {
  conexao?: Conexao;
  tabela?: string;
}
