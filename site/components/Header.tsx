'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTemSessao } from '@/lib/supabase/sessao-leve';
import { useEffect, useState } from 'react';
import { Logo } from './Logo';
import { Search } from './Search';
import { ThemeToggle } from './ThemeToggle';
import { Sidebar } from './Sidebar';
import { Redes } from './Redes';

/**
 * Cabeçalho flutuante.
 *
 * É um cartão com margem, não uma barra colada no topo: o fundo aparece
 * em volta e a página inteira lê como uma superfície sobre outra. Ao
 * rolar, ganha sombra e o fundo fecha — a única mudança, porque um
 * cabeçalho que muda de tamanho faz o conteúdo pular.
 *
 * A marca aparece sozinha, sem o nome ao lado: uma marca reconhecível
 * não precisa se apresentar em toda página.
 */
export function Header() {
  const [menuAberto, setMenuAberto] = useState(false);
  const temSessao = useTemSessao();

  // Dentro da documentação, os atalhos de assunto SAEM do topo.
  //
  // "Começar", "Exercícios", "Kiln" e "Biblioteca" são quatro das 190
  // rotas que a barra lateral já lista — e a barra lateral está ali,
  // aberta, a dois centímetros. Repetir quatro delas no topo não
  // ajuda a achar nada e gasta a largura que o campo de busca usa.
  //
  // Fora da documentação eles continuam: na home e na página de
  // download não há barra lateral, e ali eles são a única porta.
  const caminho = usePathname() ?? '';
  const naDocumentacao = caminho.startsWith('/docs');
  const [rolou, setRolou] = useState(false);

  useEffect(() => {
    const aoRolar = () => setRolou(window.scrollY > 8);
    aoRolar();
    window.addEventListener('scroll', aoRolar, { passive: true });
    return () => window.removeEventListener('scroll', aoRolar);
  }, []);

  // Com o menu do celular aberto, a página atrás não deve rolar.
  useEffect(() => {
    document.body.style.overflow = menuAberto ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [menuAberto]);

  return (
    <>
      <div className="sticky top-0 z-40 px-2 pt-2 sm:px-4 sm:pt-4">
        <header
          className={`mx-auto flex h-[64px] max-w-[1620px] items-center gap-3 rounded-2xl border px-3 transition-all duration-300 sm:px-4 ${
            rolou
              ? 'border-line bg-surface/90 shadow-[0_8px_30px_-12px_rgb(0_0_0/0.5)] backdrop-blur-xl'
              : 'border-line/60 bg-surface/60 backdrop-blur-lg'
          }`}
        >
          <button
            onClick={() => setMenuAberto(true)}
            className="rounded-xl p-2 text-muted transition-colors hover:bg-raised hover:text-strong lg:hidden"
            aria-label="Abrir navegação"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path
                d="M3 5.5h14M3 10h14M3 14.5h14"
                stroke="currentColor"
                strokeWidth="1.7"
                strokeLinecap="round"
              />
            </svg>
          </button>

          <Link
            href="/docs"
            className="group flex shrink-0 items-center rounded-xl p-1 transition-transform duration-300 hover:scale-105"
            aria-label="DataForge — início da documentação"
          >
            <Logo size={44} className="transition-opacity group-hover:opacity-90" />
          </Link>

          {/* A busca mora AO LADO dos links do topo, e não no meio do
              cabeçalho: centralizada, ela ficava isolada entre a marca e
              a navegação, longe de onde o olho já está quando procura
              "Download" ou "Roadmap". */}
          <nav className="ml-auto flex items-center gap-0.5">
            <div className="mr-2 hidden md:block md:w-[190px] lg:w-[240px] xl:w-[280px]">
              <Search />
            </div>
            {!naDocumentacao && (
              <>
                <Link href="/docs/primeiros-passos" className="link-topo hidden lg:block">
                  Começar
                </Link>
                <Link href="/docs/exercicios" className="link-topo hidden lg:block">
                  Exercícios
                </Link>
                <Link href="/docs/kiln" className="link-topo hidden xl:block">
                  Kiln
                </Link>
                <Link href="/docs/biblioteca" className="link-topo hidden xl:block">
                  Biblioteca
                </Link>
              </>
            )}
            <Link href="/download" className="link-topo hidden lg:block">
              Download
            </Link>
            <Link href="/roadmap" className="link-topo hidden lg:block">
              Roadmap
            </Link>

            {/* Quem já entrou vê o painel; quem não entrou vê as duas
                portas. `temSessao` é `null` enquanto a resposta não
                chega, e nesse intervalo NADA é desenhado: mostrar
                "Entrar" e trocar por "Painel" um instante depois é o
                pulo que faz a página parecer quebrada para quem já
                está autenticado. */}
            {temSessao === true && (
              <Link
                href="/painel"
                className="ml-2 hidden rounded-xl bg-accent px-4 py-2 text-[13.5px] font-semibold text-white shadow-[0_4px_16px_-6px_rgb(var(--accent))] transition-all hover:bg-accent-soft hover:shadow-[0_6px_20px_-6px_rgb(var(--accent))] sm:block"
              >
                Painel
              </Link>
            )}
            {temSessao === false && (
              <span className="ml-2 hidden items-center gap-1.5 sm:flex">
                <Link
                  href="/painel"
                  className="whitespace-nowrap rounded-xl border border-line px-3 py-2 text-[13.5px] font-semibold text-strong transition-colors hover:bg-raised"
                >
                  Entrar
                </Link>
                <Link
                  href="/painel?criar=1"
                  className="whitespace-nowrap rounded-xl bg-accent px-3.5 py-2 text-[13.5px] font-semibold text-white shadow-[0_4px_16px_-6px_rgb(var(--accent))] transition-all hover:bg-accent-soft hover:shadow-[0_6px_20px_-6px_rgb(var(--accent))]"
                >
                  Criar conta
                </Link>
              </span>
            )}

            <span className="mx-1.5 hidden h-5 w-px bg-line sm:block" aria-hidden="true" />

            <Redes tamanho={17} gap="gap-0.5" className="hidden sm:flex" />

            <ThemeToggle />
          </nav>
        </header>
      </div>

      {/* Navegação do celular */}
      {menuAberto && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-[fade_.2s_ease]"
            onClick={() => setMenuAberto(false)}
            aria-label="Fechar navegação"
          />
          <div className="absolute inset-y-0 left-0 flex w-[86%] max-w-[330px] flex-col border-r border-line bg-surface shadow-2xl animate-[entrar-lado_.24s_cubic-bezier(.22,1,.36,1)]">
            <div className="flex h-[64px] shrink-0 items-center justify-between border-b border-line px-4">
              <Logo size={34} />
              <button
                onClick={() => setMenuAberto(false)}
                className="rounded-xl p-2 text-muted transition-colors hover:bg-raised hover:text-strong"
                aria-label="Fechar"
              >
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
                  <path
                    d="M4 4l10 10M14 4L4 14"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto px-3 py-4">
              <div className="mb-4 md:hidden">
                <Search />
              </div>

              {/* As rotas de TOPO, que no celular ficam escondidas
                  (`hidden lg:block`). Sem esta fila, '/roadmap' e
                  '/download' seriam inalcancaveis no telefone: o menu
                  do celular mostra a barra lateral, e nenhuma das duas
                  esta nela — a do roadmap de proposito. */}
              <div className="mb-4 flex flex-wrap gap-1.5 border-b border-line pb-4 lg:hidden">
                {[
                  { href: '/roadmap', rotulo: 'Roadmap' },
                  { href: '/download', rotulo: 'Download' },
                  ...(temSessao === false
                    ? [
                        { href: '/painel', rotulo: 'Entrar' },
                        { href: '/painel?criar=1', rotulo: 'Criar conta' },
                      ]
                    : temSessao === true
                      ? [{ href: '/painel', rotulo: 'Painel' }]
                      : []),
                ].map((l) => (
                  <Link
                    key={l.href}
                    href={l.href}
                    onClick={() => setMenuAberto(false)}
                    className="rounded-lg border border-line bg-raised/50 px-3 py-1.5 text-[13px] font-medium text-strong transition-colors hover:bg-raised"
                  >
                    {l.rotulo}
                  </Link>
                ))}
              </div>

              <Sidebar onNavigate={() => setMenuAberto(false)} />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
