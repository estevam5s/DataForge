/**
 * Quanto cada `adopt` custa, ao lado da linha.
 *
 * Uma linha de import não parece cara. `adopt Arcane.Math` traz 52
 * símbolos e 5 KB de código para dentro do processo, e um programa que
 * só queria `sqrt` paga por todos.
 *
 * A informação aparece em cinza no fim da linha, como o
 * "Import Cost" do JavaScript — e pelo mesmo motivo: o custo tem de
 * estar onde a decisão é tomada, não num relatório que ninguém abre.
 */

import * as vscode from 'vscode';
import { exigirExecutavel, raizDe, rodar } from './dataforge';

const ADOPT = /^\s*adopt\s+([A-Za-z_][\w.]*)/;

/** Quantos símbolos cada módulo traz, medido uma vez por sessão. */
const tamanhos = new Map<string, { simbolos: number; kb: number }>();

let decoracao: vscode.TextEditorDecorationType | undefined;

function obterDecoracao(): vscode.TextEditorDecorationType {
  if (!decoracao) {
    decoracao = vscode.window.createTextEditorDecorationType({
      after: {
        color: new vscode.ThemeColor('editorCodeLens.foreground'),
        margin: '0 0 0 1.5em',
        fontStyle: 'italic',
      },
    });
  }
  return decoracao;
}

async function medir(raiz: string, arquivo: string) {
  const exe = await exigirExecutavel();
  if (!exe) return;

  try {
    const { saida } = await rodar(exe, ['custo', arquivo, '--no-color'], 15000, raiz);
    for (const linha of saida.split('\n')) {
      const limpa = linha.replace(/\x1b\[[0-9;]*m/g, '');
      const casou = /●\s+([\w.]+)\s+(\d+) simbolos(?:, (\d+) KB)?/.exec(limpa);
      if (casou) {
        tamanhos.set(casou[1], {
          simbolos: parseInt(casou[2], 10),
          kb: casou[3] ? parseInt(casou[3], 10) : 0,
        });
      }
    }
  } catch {
    /* sem medida: as linhas ficam sem anotação */
  }
}

export async function anotar(editor: vscode.TextEditor | undefined) {
  if (!editor || editor.document.languageId !== 'dataforge') return;
  if (!vscode.workspace.getConfiguration('dataforge').get('custoDeImport', true)) {
    editor.setDecorations(obterDecoracao(), []);
    return;
  }

  await medir(raizDe(editor.document), editor.document.uri.fsPath);

  const marcas: vscode.DecorationOptions[] = [];
  for (let i = 0; i < editor.document.lineCount; i++) {
    const texto = editor.document.lineAt(i).text;
    const casou = ADOPT.exec(texto);
    if (!casou) continue;

    const dados = tamanhos.get(casou[1]);
    if (!dados) continue;

    // A cor vem do peso: verde até 20 símbolos, amarelo acima de 60.
    // Não é julgamento — um módulo grande pode ser exatamente o que se
    // precisa — é só o número ficando visível.
    const rotulo = dados.kb
      ? `${dados.simbolos} símbolos · ${dados.kb} KB`
      : `${dados.simbolos} símbolos`;

    marcas.push({
      range: new vscode.Range(i, texto.length, i, texto.length),
      renderOptions: { after: { contentText: `  ${rotulo}` } },
      hoverMessage: new vscode.MarkdownString(
        `**${casou[1]}** traz ${dados.simbolos} símbolos para o processo.\n\n` +
          (dados.simbolos > 40
            ? `Traga só o que usa:\n\n\`\`\`dataforge\nadopt ${casou[1]}.{ sqrt, floor }\n\`\`\``
            : 'Módulo pequeno — importar inteiro custa pouco.'),
      ),
    });
  }

  editor.setDecorations(obterDecoracao(), marcas);
}
