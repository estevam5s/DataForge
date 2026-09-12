/**
 * Criar projetos pelo editor.
 *
 * Os modelos vêm de `dataforge new --listar`, não de uma lista
 * escrita aqui. Duplicar a lista garantiria que ela envelhecesse: um
 * modelo novo na CLI não apareceria no editor, e ninguém notaria até
 * alguém procurar por ele.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import { exigirExecutavel, rodar } from './dataforge';

interface Modelo {
  nome: string;
  descricao: string;
}

/** Reserva: se a CLI não responder, ainda dá para criar algo. */
const RESERVA: Modelo[] = [
  { nome: 'cli', descricao: 'ferramenta de linha de comando' },
  { nome: 'api', descricao: 'API HTTP com rotas e testes' },
  { nome: 'web', descricao: 'site com páginas e arquivos estáticos' },
  { nome: 'data', descricao: 'análise de dados e planilhas' },
  { nome: 'lib', descricao: 'biblioteca publicável no registro' },
  { nome: 'oop', descricao: 'modelagem com blueprints e traits' },
  { nome: 'script', descricao: 'automação: arquivos, JSON, datas' },
  { nome: 'test', descricao: 'suíte de testes com o Crucible' },
];

async function listarModelos(): Promise<Modelo[]> {
  const exe = await exigirExecutavel();
  if (!exe) return RESERVA;

  try {
    const { saida } = await rodar(exe, ['new', '--listar', '--no-color'], 10000);
    const achados: Modelo[] = [];
    for (const linha of saida.split('\n')) {
      const limpa = linha.replace(/\x1b\[[0-9;]*m/g, '');
      const casou = /^\s{2,}([a-z][\w-]*)\s{2,}(.+?)\s*$/.exec(limpa);
      if (casou) achados.push({ nome: casou[1], descricao: casou[2] });
    }
    return achados.length ? achados : RESERVA;
  } catch {
    return RESERVA;
  }
}

export async function criarProjeto() {
  const modelos = await listarModelos();

  const escolha = await vscode.window.showQuickPick(
    modelos.map((m) => ({
      label: m.nome,
      description: m.descricao,
      modelo: m,
    })),
    { title: 'Que tipo de projeto?', matchOnDescription: true },
  );
  if (!escolha) return;

  const nome = await vscode.window.showInputBox({
    title: 'Nome do projeto',
    prompt: 'vira o nome da pasta e o do forge.toml',
    validateInput: (v) =>
      /^[a-z][a-z0-9_-]*$/.test(v)
        ? null
        : 'minúsculas, números, - e _; começando por letra',
  });
  if (!nome) return;

  const pastas = await vscode.window.showOpenDialog({
    canSelectFolders: true,
    canSelectFiles: false,
    canSelectMany: false,
    openLabel: 'Criar aqui',
    defaultUri: vscode.workspace.workspaceFolders?.[0]?.uri,
  });
  if (!pastas?.length) return;

  const destino = pastas[0].fsPath;
  if (fs.existsSync(path.join(destino, nome))) {
    vscode.window.showErrorMessage(`Já existe uma pasta '${nome}' aí.`);
    return;
  }

  const exe = await exigirExecutavel();
  if (!exe) return;

  // '--silencioso' e a parte que faltava: sem ele a CLI pode cair num
  // prompt, e o editor nao tem ninguem para responder. O comando ficava
  // esperando para sempre, o projeto nunca aparecia, e a mensagem
  // mandava rodar no terminal exatamente o comando que nao funcionava.
  const argumentos = [
    'new', nome, `--modelo=${escolha.modelo.nome}`, '--silencioso',
  ];

  let resultado = { saida: '', erro: '', codigo: 0 };
  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: `Criando ${nome}…` },
    async () => {
      resultado = await rodar(exe, argumentos, 60000, destino);
    },
  );

  const criado = path.join(destino, nome);
  if (!fs.existsSync(criado)) {
    // O motivo REAL, que a CLI acabou de imprimir. Mandar o usuario
    // reproduzir no terminal e pedir que ele faca o trabalho que a
    // extensao ja fez — e o comando esta aqui, com a saida dele.
    const motivo = (resultado.erro || resultado.saida || '')
      .replace(/\x1b\[[0-9;]*m/g, '')
      .split('\n')
      .map((l) => l.trim())
      .filter((l) => l.length > 0)
      .slice(-4)
      .join('  ');

    const escolhido = await vscode.window.showErrorMessage(
      motivo
        ? `Não foi possível criar '${nome}': ${motivo}`
        : `Não foi possível criar '${nome}'. A CLI não disse por quê.`,
      'Ver a saída completa',
    );
    if (escolhido) {
      const canal = vscode.window.createOutputChannel('DataForge');
      canal.appendLine(`$ dataforge ${argumentos.join(' ')}`);
      canal.appendLine(`  (em ${destino})`);
      canal.appendLine('');
      canal.appendLine(resultado.saida || '(sem saída)');
      if (resultado.erro) {
        canal.appendLine('--- erro ---');
        canal.appendLine(resultado.erro);
      }
      canal.show();
    }
    return;
  }

  const abrir = await vscode.window.showInformationMessage(
    `Projeto '${nome}' criado.`,
    'Abrir',
    'Abrir em nova janela',
  );
  if (abrir) {
    await vscode.commands.executeCommand(
      'vscode.openFolder',
      vscode.Uri.file(criado),
      abrir === 'Abrir em nova janela',
    );
  }
}
