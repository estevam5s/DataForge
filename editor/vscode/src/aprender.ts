/**
 * Os comandos de APRENDER: o que a extensão sabe e não mostrava.
 *
 * O hover dizia o que uma palavra faz e mostrava um exemplo. O passo que
 * faltava era o seguinte: ir ler. Quem para o mouse em `distill` e quer
 * entender pipelines tinha de sair do editor, abrir o site e procurar — e
 * quem faz isso três vezes para de fazer.
 *
 * Nada aqui repete a tabela de palavras nem o mapa de documentação. A
 * lista vem de `dataforge palavras --json` e o link vem do próprio hover
 * do LSP, que já o carrega. Uma segunda cópia divergiria da primeira, e
 * um link quebrado num cartão é pior que nenhum link: gasta a confiança
 * de quem clicou.
 */

import * as vscode from 'vscode';

import { exigirExecutavel, rodar } from './dataforge';

/** Uma palavra, como `dataforge palavras --json` a entrega. */
interface Palavra {
  palavra: string;
  explicacao: string;
  exemplo: string;
  especie: string;
  doc: string;
}

/** O endereço escondido no markdown do hover, se houver. */
function linkDoHover(hovers: vscode.Hover[]): string | undefined {
  for (const hover of hovers) {
    for (const parte of hover.contents) {
      const texto =
        typeof parte === 'string' ? parte : (parte as vscode.MarkdownString).value ?? '';
      // O cartão termina com `[rótulo](url)`. Pega o ÚLTIMO, que é o
      // rodapé — um exemplo no meio do cartão pode conter um link.
      const achados = [...texto.matchAll(/\]\((https?:\/\/[^)]+)\)/g)];
      if (achados.length > 0) return achados[achados.length - 1][1];
    }
  }
  return undefined;
}

/**
 * Abre a documentação do símbolo sob o cursor.
 *
 * Pergunta ao LSP em vez de resolver aqui: o servidor já sabe se aquilo é
 * palavra reservada, módulo, membro de módulo ou embutida, e já carrega o
 * endereço no cartão. Reimplementar essa decisão na extensão criaria duas
 * respostas para a mesma pergunta.
 */
export async function abrirDocDoSimbolo(): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== 'dataforge') {
    vscode.window.showInformationMessage(
      'DataForge: abra um arquivo .df e ponha o cursor sobre um nome.',
    );
    return;
  }

  const hovers = await vscode.commands.executeCommand<vscode.Hover[]>(
    'vscode.executeHoverProvider',
    editor.document.uri,
    editor.selection.active,
  );

  const url = hovers ? linkDoHover(hovers) : undefined;
  if (!url) {
    const palavra = editor.document.getText(
      editor.document.getWordRangeAtPosition(editor.selection.active),
    );
    vscode.window.showInformationMessage(
      palavra
        ? `DataForge: não há página para '${palavra}'.`
        : 'DataForge: ponha o cursor sobre um nome.',
    );
    return;
  }
  await vscode.env.openExternal(vscode.Uri.parse(url));
}

/**
 * A lista das 100 palavras, com o exemplo e o caminho para a doc.
 *
 * A lista sai da CLI (`dataforge palavras --json`), que a lê do mesmo
 * arquivo que alimenta o hover e a página do site. Já esteve escrita em
 * dois lugares, e os dois divergiram.
 */
export async function palavrasReservadas(): Promise<void> {
  const binario = await exigirExecutavel();
  if (!binario) return;

  const r = await rodar(binario, ['palavras', '--json'], 15000);
  let palavras: Palavra[];
  try {
    palavras = JSON.parse(r.saida) as Palavra[];
  } catch {
    vscode.window.showErrorMessage(
      'DataForge: não consegui ler a lista de palavras. ' +
        "Confira 'dataforge palavras --json' no terminal.",
    );
    return;
  }

  const escolha = await vscode.window.showQuickPick(
    palavras.map((p) => ({
      label: p.palavra,
      description: p.especie,
      detail: p.explicacao,
      palavra: p,
    })),
    {
      title: `DataForge — ${palavras.length} palavras`,
      placeHolder: 'procure por nome ou pelo que faz',
      matchOnDetail: true,
    },
  );
  if (!escolha) return;

  // Três coisas se pode querer com uma palavra, e adivinhar qual seria
  // errado em dois terços das vezes.
  const acao = await vscode.window.showQuickPick(
    [
      { label: '$(code) Inserir o exemplo aqui', id: 'inserir' },
      { label: '$(book) Abrir a documentação', id: 'doc' },
      { label: '$(preview) Ver o exemplo ao lado', id: 'ver' },
    ],
    { title: escolha.palavra.palavra, placeHolder: escolha.palavra.explicacao },
  );
  if (!acao) return;

  const { exemplo, doc, palavra } = escolha.palavra;

  if (acao.id === 'doc') {
    await vscode.env.openExternal(vscode.Uri.parse(doc));
    return;
  }
  if (acao.id === 'ver') {
    const documento = await vscode.workspace.openTextDocument({
      content: `// ${palavra} — ${escolha.palavra.explicacao}\n// ${doc}\n\n${exemplo}\n`,
      language: 'dataforge',
    });
    await vscode.window.showTextDocument(documento, {
      viewColumn: vscode.ViewColumn.Beside,
      preview: true,
    });
    return;
  }

  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showInformationMessage('DataForge: abra um arquivo primeiro.');
    return;
  }
  await editor.edit((edicao) => {
    edicao.insert(editor.selection.active, exemplo);
  });
}

/** Aplica um dos dois temas de cor do DataForge. */
export async function temaDeCores(): Promise<void> {
  const escolha = await vscode.window.showQuickPick(
    [
      { label: '$(color-mode) DataForge Escuro', tema: 'DataForge Escuro' },
      { label: '$(color-mode) DataForge Claro', tema: 'DataForge Claro' },
    ],
    {
      title: 'Tema de cores do DataForge',
      placeHolder: 'as 43 marcas da gramática têm cor própria nos dois',
    },
  );
  if (!escolha) return;

  // Global, e não por pasta: um tema por projeto faria a janela trocar de
  // cor ao mudar de aba, que é desorientador e ninguém pede.
  await vscode.workspace
    .getConfiguration('workbench')
    .update('colorTheme', escolha.tema, vscode.ConfigurationTarget.Global);
}

/**
 * O idioma das mensagens do DataForge.
 *
 * O runtime fala português por padrão e `DF_IDIOMA=en` volta ao inglês —
 * que é a forma que aparece em toda busca na internet, e por isso a que
 * se quer ao reportar um bug.
 */
export async function idioma(): Promise<void> {
  const config = vscode.workspace.getConfiguration('dataforge');
  const atual = config.get<string>('idioma') ?? 'pt';

  const escolha = await vscode.window.showQuickPick(
    [
      {
        label: '$(globe) Português',
        description: atual === 'pt' ? 'em uso' : '',
        valor: 'pt',
        detail: 'o padrão do runtime e do analisador',
      },
      {
        label: '$(globe) English',
        description: atual === 'en' ? 'em uso' : '',
        valor: 'en',
        detail: 'o texto original — o que aparece nas buscas na internet',
      },
    ],
    { title: 'Idioma das mensagens', placeHolder: `em uso: ${atual}` },
  );
  if (!escolha) return;

  await config.update('idioma', escolha.valor, vscode.ConfigurationTarget.Global);
  vscode.window.showInformationMessage(
    `DataForge: mensagens em ${escolha.valor === 'pt' ? 'português' : 'inglês'}. ` +
      'Vale para o que a extensão rodar daqui em diante.',
  );
}
