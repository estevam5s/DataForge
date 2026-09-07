import Link from 'next/link';
import { Logo } from './Logo';

const REPO = 'https://github.com/estevam5s/DataForge';

const colunas = [
  {
    titulo: 'Aprender',
    links: [
      { t: 'Primeiros passos', h: '/primeiros-passos' },
      { t: 'Instalação', h: '/instalacao' },
      { t: 'Exercícios', h: '/exercicios' },
      { t: 'Receitas', h: '/receitas/cli' },
    ],
  },
  {
    titulo: 'Referência',
    links: [
      { t: 'Gramática', h: '/referencia/gramatica' },
      { t: 'Palavras reservadas', h: '/referencia/palavras-reservadas' },
      { t: 'Funções embutidas', h: '/referencia/embutidas' },
      { t: 'Biblioteca Arcane', h: '/biblioteca' },
    ],
  },
  {
    titulo: 'Ferramentas',
    links: [
      { t: 'CLI', h: '/cli' },
      { t: 'Análise estática', h: '/tecnicas/analise-estatica' },
      { t: 'Testes', h: '/tecnicas/testes' },
      { t: 'forge.toml', h: '/cli/forge-toml' },
    ],
  },
  {
    titulo: 'Projeto',
    links: [
      { t: 'Roadmap', h: '/roadmap' },
      { t: 'Contribuir', h: '/contribuir' },
      { t: 'FAQ', h: '/faq' },
      { t: 'Migração 3.x → 4.0', h: '/faq/migracao' },
    ],
  },
];

export function Footer() {
  return (
    <footer className="mt-24 border-t border-line bg-surface/40">
      <div className="mx-auto max-w-[1600px] px-6 py-14">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-5">
          <div className="lg:col-span-1">
            <div className="mb-3 flex items-center gap-2.5">
              <Logo size={28} />
              <span className="font-extrabold text-strong">DataForge</span>
            </div>
            <p className="max-w-[240px] text-[13.5px] leading-[22px] text-muted">
              Uma linguagem de programação com vocabulário próprio, tipos
              verificados e pipelines nativos.
            </p>
          </div>

          {colunas.map((c) => (
            <div key={c.titulo}>
              <p className="nav-label mb-3 text-strong">{c.titulo}</p>
              <ul className="space-y-2">
                {c.links.map((l) => (
                  <li key={l.h}>
                    <Link href={l.h} className="text-[13.5px] link-quiet">
                      {l.t}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-line pt-6 text-[13px] text-muted sm:flex-row sm:items-center sm:justify-between">
          <p>DataForge 4.0 · licença MIT · documentação em português</p>
          <a href={REPO} target="_blank" rel="noreferrer noopener" className="link-quiet">
            github.com/estevam5s/DataForge
          </a>
        </div>
      </div>
    </footer>
  );
}
