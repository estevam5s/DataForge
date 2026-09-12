/**
 * A depuração no painel do editor.
 *
 * O adaptador mora no DataForge — `dataforge dap` fala o protocolo por
 * stdio. Aqui não há lógica de depuração nenhuma: só se diz ao VS Code
 * qual processo iniciar e qual configuração usar quando a pessoa aperta
 * F5 sem ter escrito `launch.json`.
 *
 * Essa divisão é deliberada. O adaptador em Python serve **qualquer**
 * editor que fale DAP — Neovim, Helix, Emacs — e não só este. Escrever
 * a máquina em TypeScript a amarraria ao VS Code, e ela já existe:
 * `depurador.py` decide quando parar, e `dap.py` traduz.
 */

import * as vscode from 'vscode';

import { executavel } from './dataforge';

/** O tipo que aparece no `launch.json`. */
export const TIPO = 'dataforge';

/**
 * F5 sem `launch.json`.
 *
 * Sem isto, apertar F5 num `.df` abre o menu "selecione um
 * depurador" — que é onde a maioria das pessoas desiste.
 */
class Padroes implements vscode.DebugConfigurationProvider {
  resolveDebugConfiguration(
    _pasta: vscode.WorkspaceFolder | undefined,
    config: vscode.DebugConfiguration,
  ): vscode.ProviderResult<vscode.DebugConfiguration> {
    if (!config.type && !config.request && !config.name) {
      const editor = vscode.window.activeTextEditor;
      if (editor?.document.languageId !== 'dataforge') {
        return undefined;
      }
      config.type = TIPO;
      config.name = 'Depurar este arquivo';
      config.request = 'launch';
      config.program = '${file}';
      config.stopOnEntry = false;
    }

    if (!config.program) {
      void vscode.window.showErrorMessage(
        'Não sei qual arquivo depurar — abra um .df ou ponha "program" no launch.json.',
      );
      return undefined;
    }
    if (!config.cwd) {
      // A pasta do projeto, e não a do arquivo: é ela que tem o
      // `forge.toml`, e um `adopt ./vizinho` se resolve a partir dela.
      config.cwd = '${workspaceFolder}';
    }
    return config;
  }
}

/**
 * Onde está o `dataforge`.
 *
 * O executável é procurado uma vez e lembrado (`dataforge.ts`): há três
 * lugares onde ele pode estar instalado, e uma cópia antiga produz erros
 * que não existem no projeto.
 */
class Fabrica implements vscode.DebugAdapterDescriptorFactory {
  async createDebugAdapterDescriptor(): Promise<
    vscode.DebugAdapterDescriptor | undefined
  > {
    const exe = await executavel();
    if (!exe) {
      void vscode.window.showErrorMessage(
        'Não encontrei o `dataforge`. Instale-o, ou aponte o caminho em ' +
          'Configurações → dataforge.caminho.',
      );
      return undefined;
    }
    return new vscode.DebugAdapterExecutable(exe, ['dap']);
  }
}

export function registrar(contexto: vscode.ExtensionContext): void {
  contexto.subscriptions.push(
    vscode.debug.registerDebugConfigurationProvider(TIPO, new Padroes()),
    vscode.debug.registerDebugAdapterDescriptorFactory(TIPO, new Fabrica()),
  );
}
