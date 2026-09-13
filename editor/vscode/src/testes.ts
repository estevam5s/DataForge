import * as path from 'path';
import * as vscode from 'vscode';

import { exigirExecutavel, projetoDe, raizDe, rodar } from './dataforge';

/**
 * Os testes no painel do VS Code.
 *
 * O `dataforge test` já existia e já era bom. O que faltava era ele
 * aparecer **onde se olha**: o painel de testes do editor, com o
 * triângulo ao lado de cada `trial` e o erro na linha que falhou.
 *
 * Três decisões:
 *
 * 1. **Um item por `trial`, e não por arquivo.** "1 de 2 falhou" sem
 *    dizer qual não serve para nada — é a mesma lição que o corredor
 *    de testes aprendeu quando contava arquivos.
 *
 * 2. **A descoberta é por LEITURA do arquivo, e não por execução.** Um
 *    painel que precisa rodar a suíte para saber o que existe não
 *    serve: rodar é o que se quer decidir depois de ver a lista.
 *
 * 3. **A saída do processo é anexada ao item que falhou.** O erro
 *    aparece no lugar onde se está olhando, e não num terminal que
 *    ficou para trás.
 */

const CRUCIBLE = /^\s*crucible\s+"([^"]+)"\s*:/;
const TRIAL = /^\s*trial\s+"([^"]+)"/;

export function registrar(
  contexto: vscode.ExtensionContext,
  aoTerminar?: (passaram: number, total: number) => void,
) {
  const painel = vscode.tests.createTestController(
    'dataforge', 'DataForge');
  contexto.subscriptions.push(painel);

  painel.resolveHandler = async (item) => {
    if (!item) await descobrirTudo(painel);
  };

  const rodarPerfil = painel.createRunProfile(
    'Rodar', vscode.TestRunProfileKind.Run,
    (pedido, cancelar) => executar(painel, pedido, cancelar, aoTerminar),
    true);
  contexto.subscriptions.push(rodarPerfil);

  contexto.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument((d) => {
      if (d.languageId === 'dataforge' && ehArquivoDeTeste(d.uri.fsPath)) {
        lerArquivo(painel, d.uri);
      }
    }),
    vscode.workspace.onDidDeleteFiles((e) => {
      for (const uri of e.files) painel.items.delete(uri.toString());
    }),
  );

  void descobrirTudo(painel);
  return painel;
}

/**
 * O que é arquivo de teste.
 *
 * A mesma regra do corredor: `*_test.df` ou dentro de `tests/`. Duas
 * definições divergiriam, e o painel mostraria uma lista diferente da
 * que `dataforge test` roda — que é pior que não ter painel.
 */
export function ehArquivoDeTeste(caminho: string) {
  const nome = path.basename(caminho);
  if (!nome.endsWith('.df')) return false;
  if (nome.endsWith('_test.df') || nome.endsWith('_teste.df')) return true;
  return caminho.split(path.sep).includes('tests');
}

async function descobrirTudo(painel: vscode.TestController) {
  const achados = await vscode.workspace.findFiles(
    '**/*.df', '{**/node_modules/**,**/forge_modules/**,**/.venv/**}');
  for (const uri of achados) {
    if (ehArquivoDeTeste(uri.fsPath)) await lerArquivo(painel, uri);
  }
}

async function lerArquivo(painel: vscode.TestController, uri: vscode.Uri) {
  let texto: string;
  try {
    texto = (await vscode.workspace.fs.readFile(uri)).toString();
  } catch {
    return;
  }

  const arquivo = painel.createTestItem(
    uri.toString(), path.basename(uri.fsPath), uri);
  arquivo.canResolveChildren = true;

  let suite: vscode.TestItem | null = null;
  const linhas = texto.split('\n');
  for (let i = 0; i < linhas.length; i++) {
    const daSuite = linhas[i].match(CRUCIBLE);
    if (daSuite) {
      suite = painel.createTestItem(
        `${uri.toString()}::${daSuite[1]}`, daSuite[1], uri);
      suite.range = new vscode.Range(i, 0, i, linhas[i].length);
      arquivo.children.add(suite);
      continue;
    }
    const doTrial = linhas[i].match(TRIAL);
    if (doTrial) {
      const item = painel.createTestItem(
        `${uri.toString()}::${suite?.label ?? ''}::${doTrial[1]}`,
        doTrial[1], uri);
      item.range = new vscode.Range(i, 0, i, linhas[i].length);
      (suite ?? arquivo).children.add(item);
    }
  }

  // Um arquivo sem 'trial' nenhum não vira item: ele não é uma suíte,
  // e um painel com trinta arquivos vazios esconde os que importam.
  if (arquivo.children.size === 0) {
    painel.items.delete(uri.toString());
    return;
  }
  painel.items.add(arquivo);
}

async function executar(
  painel: vscode.TestController,
  pedido: vscode.TestRunRequest,
  cancelar: vscode.CancellationToken,
  aoTerminar?: (passaram: number, total: number) => void,
) {
  const executavelDf = await exigirExecutavel();
  if (!executavelDf) return;

  const corrida = painel.createTestRun(pedido);
  const alvos: vscode.TestItem[] = [];
  if (pedido.include) {
    for (const i of pedido.include) juntar(i, alvos);
  } else {
    painel.items.forEach((i) => juntar(i, alvos));
  }
  for (const item of alvos) corrida.enqueued(item);

  // Um processo por ARQUIVO, e não por trial: o corredor do DataForge
  // já roda o arquivo inteiro, e subir um processo por teste custaria
  // mais que os testes.
  const porArquivo = new Map<string, vscode.TestItem[]>();
  for (const item of alvos) {
    const arquivo = item.uri?.fsPath;
    if (!arquivo) continue;
    porArquivo.set(arquivo, [...(porArquivo.get(arquivo) ?? []), item]);
  }

  let passaram = 0;
  let total = 0;

  for (const [arquivo, itens] of porArquivo) {
    if (cancelar.isCancellationRequested) break;
    for (const i of itens) corrida.started(i);

    const raiz = projetoDe(arquivo)
      ?? path.dirname(arquivo);
    const comeco = Date.now();
    let saida = '';
    let codigo = 0;
    try {
      const r = await rodar(executavelDf, ['test', arquivo, '-v'], 120000, raiz);
      saida = (r.saida || '') + (r.erro || '');
      codigo = r.codigo;
    } catch (erro) {
      saida = String(erro);
      codigo = 1;
    }
    const gasto = Date.now() - comeco;
    corrida.appendOutput(saida.replace(/\n/g, '\r\n'));

    const falhos = nomesQueFalharam(saida);
    for (const item of itens) {
      total++;
      if (codigo === 0 || !falhos.has(item.label)) {
        if (codigo !== 0 && falhos.size === 0) {
          // O arquivo quebrou antes de rodar teste nenhum — erro de
          // sintaxe, import faltando. Marcar tudo como falho é o
          // honesto: nenhum deles rodou.
          corrida.failed(item, new vscode.TestMessage(primeiraLinhaDeErro(saida)),
                         gasto / itens.length);
          continue;
        }
        passaram++;
        corrida.passed(item, gasto / itens.length);
      } else {
        const mensagem = new vscode.TestMessage(
          falhos.get(item.label) || 'falhou');
        if (item.uri && item.range) {
          mensagem.location = new vscode.Location(item.uri, item.range);
        }
        corrida.failed(item, mensagem, gasto / itens.length);
      }
    }
  }

  corrida.end();
  aoTerminar?.(passaram, total);
}

function juntar(item: vscode.TestItem, saida: vscode.TestItem[]) {
  if (item.children.size === 0) {
    saida.push(item);
    return;
  }
  item.children.forEach((f) => juntar(f, saida));
}

/** Os `trial` que falharam, e o motivo de cada um. */
function nomesQueFalharam(saida: string) {
  const mapa = new Map<string, string>();
  const linhas = saida.split('\n');
  for (let i = 0; i < linhas.length; i++) {
    // O corredor marca a falha com '✗' e o nome do trial.
    const casou = linhas[i].match(/[✗x]\s+(.+?)\s*$/);
    if (!casou) continue;
    const nome = casou[1].replace(/\s*\([^)]*\)\s*$/, '').trim();
    const motivo = linhas.slice(i + 1, i + 6)
      .filter((l) => l.trim() && !/^[✓✗]/.test(l.trim()))
      .join('\n').trim();
    mapa.set(nome, motivo || linhas[i].trim());
  }
  return mapa;
}

function primeiraLinhaDeErro(saida: string) {
  const linha = saida.split('\n').find(
    (l) => /erro|error|Traceback/i.test(l));
  return (linha || saida.split('\n')[0] || 'o arquivo não rodou').trim();
}
