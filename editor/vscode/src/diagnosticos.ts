/**
 * Erros e avisos sublinhados enquanto se escreve.
 *
 * Chama `dataforge check --json` e transforma o resultado em
 * diagnósticos do VS Code. É o "eslint" da linguagem — e é o MESMO
 * analisador que roda no terminal e no CI, então o que o editor
 * sublinha é exatamente o que quebra o build.
 *
 * ─── Por que com atraso ─────────────────────────────────────
 *
 * Analisar a cada tecla lançaria um processo por caractere digitado.
 * O atraso de 400 ms depois da última tecla é o suficiente para
 * parecer imediato e para agrupar uma frase inteira numa análise só.
 */

import * as vscode from 'vscode';
import { exigirExecutavel, raizDe, rodar } from './dataforge';

/** Uma linha de `dataforge check`: `arquivo:linha:coluna: nível: texto`. */
const LINHA = /^(.+?):(\d+):(\d+):\s*(erro|error|aviso|warning|nota|note):\s*(.+)$/i;

/** A sugestão vem na linha seguinte, indentada. */
const SUGESTAO = /^\s+(sugestão|sugestao|hint|dica):\s*(.+)$/i;

export class Verificador {
  private colecao: vscode.DiagnosticCollection;
  private pendentes = new Map<string, NodeJS.Timeout>();
  private ligado = true;

  constructor(contexto: vscode.ExtensionContext) {
    this.colecao = vscode.languages.createDiagnosticCollection('dataforge');
    contexto.subscriptions.push(this.colecao);
  }

  /**
   * Cala este verificador — o servidor de linguagem assumiu.
   *
   * Ele analisa a cada tecla; este só ao salvar. Com os dois ligados, o
   * mesmo erro apareceria duas vezes no painel, e a cópia deste ficaria
   * desatualizada entre um salvamento e outro. Limpar a coleção junto
   * importa: sem isso, os erros já publicados ficariam na tela para
   * sempre, sem ninguém para atualizá-los.
   */
  desligar() {
    this.ligado = false;
    for (const t of this.pendentes.values()) clearTimeout(t);
    this.pendentes.clear();
    this.colecao.clear();
  }

  /** Agenda uma verificação, cancelando a anterior do mesmo arquivo. */
  agendar(documento: vscode.TextDocument, atraso = 400) {
    if (!this.ligado) return;
    if (documento.languageId !== 'dataforge') return;
    if (!vscode.workspace.getConfiguration('dataforge').get('verificar', true)) {
      return;
    }

    const chave = documento.uri.toString();
    const anterior = this.pendentes.get(chave);
    if (anterior) clearTimeout(anterior);

    this.pendentes.set(
      chave,
      setTimeout(() => {
        this.pendentes.delete(chave);
        void this.verificar(documento);
      }, atraso),
    );
  }

  async verificar(documento: vscode.TextDocument) {
    const exe = await exigirExecutavel();
    if (!exe) return;

    // O analisador lê do disco. Num arquivo com alterações não salvas,
    // ele veria a versão antiga e sublinharia a linha errada — pior
    // que não sublinhar nada. Aí a análise espera o salvamento.
    if (documento.isDirty) return;

    try {
      const { saida, erro } = await rodar(
        exe,
        ['check', documento.uri.fsPath, '--no-color'],
        20000,
        raizDe(documento),
      );
      this.colecao.set(documento.uri, this.interpretar(saida + '\n' + erro, documento));
    } catch {
      this.colecao.delete(documento.uri);
    }
  }

  private interpretar(
    texto: string,
    documento: vscode.TextDocument,
  ): vscode.Diagnostic[] {
    const saida: vscode.Diagnostic[] = [];
    const linhas = texto.split('\n');

    for (let i = 0; i < linhas.length; i++) {
      const casou = LINHA.exec(linhas[i].replace(/\x1b\[[0-9;]*m/g, ''));
      if (!casou) continue;

      const [, , linhaTxt, colunaTxt, nivel, mensagem] = casou;
      const linha = Math.max(0, parseInt(linhaTxt, 10) - 1);
      const coluna = Math.max(0, parseInt(colunaTxt, 10) - 1);

      // Sublinha a palavra inteira, não um caractere: um til embaixo de
      // uma letra é difícil de ver e de clicar.
      const textoDaLinha = linha < documento.lineCount
        ? documento.lineAt(linha).text
        : '';
      let fim = coluna + 1;
      while (fim < textoDaLinha.length && /[\w.]/.test(textoDaLinha[fim])) fim++;

      const faixa = new vscode.Range(linha, coluna, linha, Math.max(fim, coluna + 1));
      const severidade = /erro|error/i.test(nivel)
        ? vscode.DiagnosticSeverity.Error
        : /aviso|warning/i.test(nivel)
          ? vscode.DiagnosticSeverity.Warning
          : vscode.DiagnosticSeverity.Information;

      const diagnostico = new vscode.Diagnostic(faixa, mensagem.trim(), severidade);
      diagnostico.source = 'dataforge';

      const proxima = linhas[i + 1]
        ? SUGESTAO.exec(linhas[i + 1].replace(/\x1b\[[0-9;]*m/g, ''))
        : null;
      if (proxima) {
        diagnostico.message += `\n${proxima[2].trim()}`;
        i++;
      }

      // O código DF é o que liga o erro ao `dataforge explain`.
      const codigo = /\bDF\d{4}\b/.exec(mensagem);
      if (codigo) {
        diagnostico.code = {
          value: codigo[0],
          target: vscode.Uri.parse(
            `https://dataforge-lang.vercel.app/docs/erros/${codigo[0].toLowerCase()}`,
          ),
        };
      }

      saida.push(diagnostico);
    }
    return saida;
  }

  limpar(documento: vscode.TextDocument) {
    this.colecao.delete(documento.uri);
  }
}
