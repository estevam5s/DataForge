'use client';

import { useEffect, useState } from 'react';
import dados from '@/lib/dados-gerados.json';

/**
 * Os números que vivem FORA do repositório.
 *
 * Estrelas, downloads do release e instalações da extensão mudam sem
 * que ninguém faça deploy. O site é um export estático — não há
 * servidor para consultar nada — então isto acontece em duas etapas:
 *
 * 1. `site/scripts/gerar_dados.py` grava um instantâneo no build, e é
 *    ele que a página mostra no primeiro quadro. Sem isso a primeira
 *    coisa que o visitante vê é um esqueleto piscando.
 * 2. O navegador pede os números de verdade e substitui. As duas APIs
 *    têm `Access-Control-Allow-Origin: *` — conferido.
 *
 * Falhar é normal e não pode aparecer: o GitHub limita a 60 pedidos
 * por hora por IP sem token, e a API da loja é intermitente. Quando a
 * busca não volta, fica o instantâneo, que é um número verdadeiro de
 * algumas horas atrás — melhor que um traço.
 */

const REPO = 'estevam5s/DataForge';
const EXTENSAO = 'EstevamSouza.dataforge-language';

export type Mundo = {
  estrelas: number | null;
  versao: string | null;
  publicado: string | null;
  baixados: number | null;
  instalacoes: number | null;
};

const DO_BUILD = (dados as unknown as { mundo: Mundo }).mundo;

async function comTempo<T>(promessa: Promise<T>, ms = 6000): Promise<T | null> {
  let alarme: ReturnType<typeof setTimeout> | undefined;
  try {
    return await Promise.race([
      promessa,
      new Promise<null>((ok) => {
        alarme = setTimeout(() => ok(null), ms);
      }),
    ]);
  } catch {
    return null;
  } finally {
    if (alarme) clearTimeout(alarme);
  }
}

async function doGitHub(): Promise<Partial<Mundo>> {
  const [repo, release] = await Promise.all([
    comTempo(fetch(`https://api.github.com/repos/${REPO}`).then((r) =>
      (r.ok ? r.json() : null))),
    comTempo(fetch(`https://api.github.com/repos/${REPO}/releases/latest`).then(
      (r) => (r.ok ? r.json() : null))),
  ]);

  const saida: Partial<Mundo> = {};
  if (repo && typeof repo.stargazers_count === 'number') {
    saida.estrelas = repo.stargazers_count;
  }
  if (release) {
    if (release.tag_name) saida.versao = release.tag_name;
    if (release.published_at) saida.publicado = String(release.published_at).slice(0, 10);
    if (Array.isArray(release.assets)) {
      saida.baixados = release.assets.reduce(
        (n: number, a: { download_count?: number }) => n + (a.download_count ?? 0),
        0,
      );
    }
  }
  return saida;
}

async function daLoja(): Promise<Partial<Mundo>> {
  const resposta = await comTempo(
    fetch('https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json;api-version=7.2-preview.1',
      },
      body: JSON.stringify({
        filters: [{ criteria: [{ filterType: 7, value: EXTENSAO }], pageSize: 1 }],
        flags: 914,
      }),
    }).then((r) => (r.ok ? r.json() : null)),
  );

  const estatisticas =
    resposta?.results?.[0]?.extensions?.[0]?.statistics as
      | { statisticName: string; value: number }[]
      | undefined;
  if (!estatisticas) return {};

  // 'install' é o número que a loja mostra na página, e ela só o
  // publica depois de algum tempo; até lá existe só 'downloadCount'.
  const porNome = new Map(estatisticas.map((e) => [e.statisticName, e.value]));
  const bruto = porNome.get('install') ?? porNome.get('downloadCount');
  return bruto === undefined ? {} : { instalacoes: Math.round(bruto) };
}

/** Os números, começando pelo instantâneo do build. */
export function useMundo(): Mundo {
  const [mundo, setMundo] = useState<Mundo>(DO_BUILD);

  useEffect(() => {
    let vivo = true;
    (async () => {
      const [gh, loja] = await Promise.all([doGitHub(), daLoja()]);
      if (!vivo) return;
      // Só um valor NOVO substitui um antigo: um pedido que falhou não
      // pode apagar o que o build trouxe.
      setMundo((antes) => ({ ...antes, ...gh, ...loja }));
    })();
    return () => {
      vivo = false;
    };
  }, []);

  return mundo;
}

/** `53872844` → `53.872.844`. Traço quando não há número. */
export function formatar(n: number | null | undefined): string {
  if (n === null || n === undefined) return '—';
  return n.toLocaleString('pt-BR');
}

/** `2026-09-12` → `12 set`. */
export function dataCurta(iso: string | null | undefined): string {
  if (!iso) return '—';
  const [ano, mes, dia] = iso.split('-').map(Number);
  if (!ano || !mes || !dia) return iso;
  const meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun',
                 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
  return `${dia} ${meses[mes - 1]}`;
}
