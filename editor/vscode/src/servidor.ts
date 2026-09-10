/**
 * O cliente do servidor de linguagem.
 *
 * Ele é quem dá ao editor o autocompletar sensível a contexto, o erro
 * sublinhado enquanto se digita, ir-para-definição, renomear com
 * segurança e o esquema do arquivo. Do lado de lá é `dataforge lsp`,
 * que serve do mesmo analisador estático que o `dataforge check` usa.
 *
 * ─── Por que isto substitui o diagnóstico antigo ───────────
 *
 * A extensão já sublinhava erros chamando `dataforge check` ao salvar.
 * Isso funcionava, mas só ao salvar, e uma vez por arquivo. O servidor
 * analisa a cada tecla, guarda o resultado e responde cinco perguntas
 * diferentes sobre a mesma análise. Manter os dois faria o mesmo erro
 * aparecer duas vezes no painel de problemas.
 *
 * ─── Falhar em silêncio não é opção ─────────────────────────
 *
 * Se o executável não for encontrado, o editor simplesmente não teria
 * autocompletar — e nada explicaria por quê. Por isso a falha vira uma
 * mensagem com a ação de configurar o caminho.
 */

import * as vscode from 'vscode';

import { executavel } from './dataforge';

/**
 * O cliente é carregado sob demanda, e a falta dele não é fatal.
 *
 * `vscode-languageclient` é a única dependência de execução da
 * extensão. Numa cópia instalada sem `npm install` — o que acontece
 * quando a pasta é copiada em vez de empacotada — o `import` no topo
 * derrubaria a extensão INTEIRA no carregamento: sem botão de rodar,
 * sem snippets, sem ícone, e sem nenhuma pista do motivo.
 *
 * Carregando aqui, a falta dela custa só o servidor, e o verificador
 * antigo continua cobrindo os erros ao salvar.
 */
function carregarCliente(): any | null {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    return require('vscode-languageclient/node');
  } catch {
    return null;
  }
}

let cliente: any | undefined;

export async function iniciarServidor(
  contexto: vscode.ExtensionContext,
  saida: vscode.OutputChannel,
): Promise<boolean> {
  const config = vscode.workspace.getConfiguration('dataforge');
  if (!config.get<boolean>('servidor.ativo', true)) {
    saida.appendLine('servidor de linguagem desligado por configuração');
    return false;
  }

  const lib = carregarCliente();
  if (!lib) {
    saida.appendLine(
      'vscode-languageclient não encontrado — o servidor de linguagem fica ' +
      'de fora, e os erros continuam vindo do check ao salvar. ' +
      'Numa cópia de desenvolvimento, rode "npm install" em editor/vscode.');
    return false;
  }

  const binario = await executavel();
  if (!binario) {
    const escolha = await vscode.window.showWarningMessage(
      'DataForge: não encontrei o executável — sem autocompletar nem erros ao digitar.',
      'Configurar caminho',
      'Como instalar',
    );
    if (escolha === 'Configurar caminho') {
      vscode.commands.executeCommand(
        'workbench.action.openSettings', 'dataforge.caminho');
    } else if (escolha === 'Como instalar') {
      vscode.env.openExternal(
        vscode.Uri.parse('https://dataforge-lang.vercel.app/instalar'));
    }
    return false;
  }

  const argumentos = ['lsp'];
  const registro = config.get<string>('servidor.log', '').trim();
  if (registro) {
    argumentos.push(`--log=${registro}`);
  }

  const servidor = {
    run: { command: binario, args: argumentos, transport: lib.TransportKind.stdio },
    debug: { command: binario, args: argumentos, transport: lib.TransportKind.stdio },
  };

  const opcoes = {
    documentSelector: [{ scheme: 'file', language: 'dataforge' }],
    outputChannel: saida,
    // Um erro do servidor não deve roubar o foco do editor: ele aparece
    // no canal de saída, e quem quiser olha.
    revealOutputChannelOn: 4,
    synchronize: {
      fileEvents: vscode.workspace.createFileSystemWatcher('**/forge.toml'),
    },
  };

  cliente = new lib.LanguageClient(
    'dataforge', 'DataForge', servidor, opcoes);

  try {
    await cliente.start();
    saida.appendLine(`servidor de linguagem ativo (${binario} lsp)`);
    contexto.subscriptions.push({ dispose: () => cliente?.stop() });
    return true;
  } catch (erro) {
    saida.appendLine(`o servidor de linguagem não subiu: ${erro}`);
    cliente = undefined;
    return false;
  }
}

export function servidorAtivo(): boolean {
  return cliente !== undefined;
}

export async function reiniciarServidor(
  contexto: vscode.ExtensionContext,
  saida: vscode.OutputChannel,
): Promise<void> {
  if (cliente) {
    await cliente.stop();
    cliente = undefined;
  }
  const subiu = await iniciarServidor(contexto, saida);
  vscode.window.showInformationMessage(
    subiu ? 'DataForge: servidor reiniciado.'
          : 'DataForge: o servidor não subiu — veja o canal de saída.');
}

export async function pararServidor(): Promise<void> {
  if (cliente) {
    await cliente.stop();
    cliente = undefined;
  }
}
