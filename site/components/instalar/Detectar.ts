/**
 * Qual sistema o visitante está usando.
 *
 * O `user agent` mente com frequência — navegadores o mascaram por
 * privacidade, e no Windows 11 ele ainda diz "Windows NT 10.0". Por
 * isso a detecção alimenta um **padrão**, não uma decisão: as outras
 * opções continuam visíveis, e trocar é um clique.
 *
 * Uma página que esconde o instalador do Linux porque achou que você
 * está no Mac é pior que uma que mostra os três.
 */

export type Sistema = 'macos' | 'linux' | 'windows' | 'desconhecido';

export type Arquitetura = 'arm64' | 'x64' | 'desconhecida';

export function detectarSistema(): Sistema {
  if (typeof navigator === 'undefined') return 'desconhecido';

  // `userAgentData` é o caminho moderno e não mascarado; nem todo
  // navegador o tem, então o `userAgent` continua sendo a reserva.
  const dados = (navigator as any).userAgentData;
  const plataforma: string = (dados?.platform ?? navigator.platform ?? '')
    .toLowerCase();
  const agente = navigator.userAgent.toLowerCase();

  if (plataforma.includes('mac') || agente.includes('mac os')) return 'macos';
  if (plataforma.includes('win') || agente.includes('windows')) return 'windows';
  if (
    plataforma.includes('linux') ||
    agente.includes('linux') ||
    agente.includes('x11')
  ) {
    // Android também diz "linux", e o instalador não serve para ele.
    return agente.includes('android') ? 'desconhecido' : 'linux';
  }
  return 'desconhecido';
}

export function detectarArquitetura(): Arquitetura {
  if (typeof navigator === 'undefined') return 'desconhecida';
  const agente = navigator.userAgent.toLowerCase();
  const plataforma = (navigator.platform ?? '').toLowerCase();

  if (agente.includes('arm64') || agente.includes('aarch64')) return 'arm64';
  // Safari no Apple Silicon relata Intel por compatibilidade; não há
  // como distinguir pelo agente, e por isso a arquitetura é só
  // informativa — o instalador funciona nas duas.
  if (plataforma.includes('intel') || agente.includes('x86_64')) return 'x64';
  return 'desconhecida';
}

export const NOMES: Record<Sistema, string> = {
  macos: 'macOS',
  linux: 'Linux',
  windows: 'Windows',
  desconhecido: 'seu sistema',
};

/** O comando de instalação de cada sistema. */
export const COMANDOS: Record<Sistema, { shell: string; comando: string }> = {
  macos: {
    shell: 'Terminal',
    comando: 'curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh',
  },
  linux: {
    shell: 'Terminal',
    comando: 'curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh',
  },
  windows: {
    shell: 'PowerShell',
    comando: 'irm https://dataforge-lang.vercel.app/instalar.ps1 | iex',
  },
  desconhecido: {
    shell: 'Terminal',
    comando: 'curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh',
  },
};
