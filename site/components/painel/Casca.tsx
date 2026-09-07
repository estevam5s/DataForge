'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { Logo } from '@/components/Logo';
import { useAuth } from '@/lib/supabase/auth';

/** O que qualquer pessoa logada vê. */
export const ROTAS_PAINEL = [
  { href: '/painel', titulo: 'Início', icone: 'casa',
    desc: 'Resumo da sua atividade' },
  { href: '/painel/praticar', titulo: 'Praticar', icone: 'raio',
    desc: 'Resolva problemas na linguagem' },
  { href: '/painel/laboratorio', titulo: 'Laboratório', icone: 'frasco',
    desc: 'Rode DataForge no navegador' },
  { href: '/painel/referencia', titulo: 'Referência', icone: 'livro',
    desc: 'Sintaxe, biblioteca e comandos' },
  { href: '/painel/projetos', titulo: 'Projetos', icone: 'pasta',
    desc: 'Seus projetos em DataForge' },
  { href: '/painel/trechos', titulo: 'Trechos', icone: 'codigo',
    desc: 'Código guardado para reusar' },
  { href: '/painel/exercicios', titulo: 'Exercícios', icone: 'lista',
    desc: 'Seu progresso nos 200' },
  { href: '/painel/anotacoes', titulo: 'Anotações', icone: 'nota',
    desc: 'O que você anotou lendo a doc' },
  { href: '/painel/pacotes', titulo: 'Pacotes', icone: 'caixa',
    desc: 'O registro do DataForge' },
  { href: '/painel/conta', titulo: 'Conta', icone: 'pessoa',
    desc: 'Perfil e sessão' },
];

/** O que só admin e moderador veem. O papel vem do banco, não do cliente. */
export const ROTAS_ADMIN = [
  { href: '/painel/admin', titulo: 'Visão geral', icone: 'grafico',
    desc: 'Métricas da plataforma' },
  { href: '/painel/admin/usuarios', titulo: 'Usuários', icone: 'pessoas',
    desc: 'Quem se registrou' },
  { href: '/painel/admin/problemas', titulo: 'Problemas', icone: 'alvo',
    desc: 'O catálogo de desafios' },
  { href: '/painel/admin/agendamentos', titulo: 'Agendamentos', icone: 'relogio',
    desc: 'O que roda sozinho' },
  { href: '/painel/admin/eventos', titulo: 'Auditoria', icone: 'olho',
    desc: 'Trilha de eventos' },
];

const CAMINHOS: Record<string, string> = {
  casa: 'M3 10.5 12 3l9 7.5M5 9.5V20h14V9.5',
  pasta: 'M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z',
  codigo: 'm8 8-5 4 5 4M16 8l5 4-5 4M13 5l-2 14',
  lista: 'M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01',
  nota: 'M5 3h9l5 5v13H5zM14 3v5h5',
  caixa: 'M21 8 12 3 3 8l9 5zM3 8v8l9 5 9-5V8M12 13v8',
  pessoa: 'M4 21v-2a5 5 0 0 1 5-5h6a5 5 0 0 1 5 5v2M12 3a4 4 0 1 1 0 8 4 4 0 0 1 0-8z',
  sair: 'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9',
  menu: 'M3 6h18M3 12h18M3 18h18',
  fechar: 'M6 6l12 12M18 6L6 18',
  raio: 'M13 2 4 14h7l-1 8 9-12h-7z',
  frasco: 'M9 3h6M10 3v6L5 18a2 2 0 0 0 1.7 3h10.6A2 2 0 0 0 19 18l-5-9V3',
  livro: 'M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2zM19 3v18',
  grafico: 'M3 21h18M6 17V9M11 17V5M16 17v-6M21 17v-9',
  pessoas: 'M16 20v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 3a4 4 0 1 1 0 8 4 4 0 0 1 0-8M21 20v-2a4 4 0 0 0-3-3.9',
  alvo: 'M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18M12 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8M12 12h.01',
  relogio: 'M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18M12 7v5l3 2',
  olho: 'M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7M12 9a3 3 0 1 1 0 6 3 3 0 0 1 0-6',
  chama: 'M12 22a7 7 0 0 0 7-7c0-5-4-6-4-11 0 0-3 2-3 6 0-2-2-3-2-3s-5 3-5 8a7 7 0 0 0 7 7z',
};

export function Icone({ nome, className = 'h-[18px] w-[18px]' }:
                      { nome: string; className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none"
         stroke="currentColor" strokeWidth="1.7"
         strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d={CAMINHOS[nome] ?? CAMINHOS.casa} />
    </svg>
  );
}

export function Casca({ children }: { children: React.ReactNode }) {
  const caminho = usePathname();
  const { usuario, perfil, admin, sair, demonstracao } = useAuth();
  const [menuAberto, setMenuAberto] = useState(false);

  // '/painel' casaria com tudo; a raiz precisa de igualdade exata.
  // '/painel/admin' idem, senão as subpáginas o deixariam sempre ativo.
  const atual = (href: string) => {
    const limpo = caminho?.replace(/\/$/, '') ?? '';
    if (href === '/painel' || href === '/painel/admin') return limpo === href;
    return limpo.startsWith(href);
  };

  const nome = (usuario?.user_metadata?.nome as string)
    ?? usuario?.email?.split('@')[0] ?? 'você';

  return (
    <div className="min-h-screen">
      {demonstracao && (
        <div className="border-b border-accent/25 bg-accent/10 px-4 py-2.5
                        text-center text-[13px]">
          <strong className="text-strong">Modo demonstração.</strong>{' '}
          <span className="text-muted">
            Sem credenciais do Supabase — os dados são de exemplo e somem ao
            recarregar.{' '}
          </span>
          <Link href="/painel/configurar" className="link-quiet underline">
            como ligar
          </Link>
        </div>
      )}

      <div className="flex">
        {/* Barra lateral */}
        <aside className={`fixed inset-y-0 left-0 z-50 w-[248px] shrink-0
                           border-r border-line bg-base transition-transform
                           lg:sticky lg:top-0 lg:h-screen lg:translate-x-0
                           ${menuAberto ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="flex h-full min-h-0 flex-col p-4">
            <Link href="/" className="mb-5 flex items-center gap-2 px-2">
              <Logo size={34} />
            </Link>

            {perfil && (perfil.xp > 0 || perfil.ofensiva > 0) && (
              <div className="mb-4 flex gap-2 px-1">
                <div className="flex-1 rounded-xl border border-line bg-raised/40 px-3 py-2">
                  <p className="text-[10.5px] uppercase tracking-wide text-muted">XP</p>
                  <p className="text-[17px] font-bold tabular-nums text-strong">
                    {perfil.xp}
                  </p>
                </div>
                <div className="flex-1 rounded-xl border border-line bg-raised/40 px-3 py-2">
                  <p className="text-[10.5px] uppercase tracking-wide text-muted">
                    Ofensiva
                  </p>
                  <p className="flex items-center gap-1 text-[17px] font-bold tabular-nums text-strong">
                    {perfil.ofensiva}
                    {perfil.ofensiva > 0 && (
                      <Icone nome="chama" className="h-4 w-4 text-accent" />
                    )}
                  </p>
                </div>
              </div>
            )}

            <nav className="min-h-0 flex-1 space-y-0.5 overflow-y-auto">
              {ROTAS_PAINEL.map((r) => (
                <Link
                  key={r.href}
                  href={r.href}
                  onClick={() => setMenuAberto(false)}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2
                              text-[14px] transition-colors ${
                    atual(r.href)
                      ? 'bg-accent/12 font-semibold text-accent'
                      : 'text-body hover:bg-raised hover:text-strong'}`}
                >
                  <Icone nome={r.icone} />
                  {r.titulo}
                </Link>
              ))}

              {admin && (
                <>
                  <p className="mt-5 px-3 pb-1 text-[10.5px] font-bold uppercase tracking-[1px] text-muted">
                    Administração
                  </p>
                  {ROTAS_ADMIN.map((r) => (
                    <Link
                      key={r.href}
                      href={r.href}
                      onClick={() => setMenuAberto(false)}
                      className={`flex items-center gap-3 rounded-lg px-3 py-2
                                  text-[14px] transition-colors ${
                        atual(r.href)
                          ? 'bg-accent/12 font-semibold text-accent'
                          : 'text-body hover:bg-raised hover:text-strong'}`}
                    >
                      <Icone nome={r.icone} />
                      {r.titulo}
                    </Link>
                  ))}
                </>
              )}
            </nav>

            <div className="mt-4 border-t border-line pt-4">
              <div className="mb-2 px-3">
                <p className="truncate text-[13.5px] font-semibold text-strong">
                  {nome}
                  {admin && (
                    <span className="ml-1.5 rounded-full bg-accent/15 px-1.5 py-px text-[9.5px] font-bold uppercase tracking-wide text-accent">
                      {perfil?.papel}
                    </span>
                  )}
                </p>
                <p className="truncate text-[12px] text-muted">
                  {usuario?.email}
                </p>
              </div>
              <button
                onClick={() => sair()}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2
                           text-[14px] text-muted transition-colors
                           hover:bg-raised hover:text-strong"
              >
                <Icone nome="sair" />
                Sair
              </button>
            </div>
          </div>
        </aside>

        {menuAberto && (
          <button
            className="fixed inset-0 z-40 bg-black/50 lg:hidden"
            onClick={() => setMenuAberto(false)}
            aria-label="Fechar menu"
          />
        )}

        <main className="min-w-0 flex-1">
          <div className="sticky top-0 z-30 flex items-center gap-3
                          border-b border-line bg-base/85 px-4 py-3
                          backdrop-blur lg:hidden">
            <button
              onClick={() => setMenuAberto((v) => !v)}
              className="rounded-lg p-1.5 text-muted hover:text-strong"
              aria-label="Abrir menu"
            >
              <Icone nome={menuAberto ? 'fechar' : 'menu'} />
            </button>
            <span className="font-semibold">Painel</span>
          </div>

          <div className="mx-auto max-w-[1100px] px-5 py-8 lg:px-8 lg:py-10">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

/** Cabeçalho de página do painel. */
export function Cabecalho({ titulo, descricao, acao }: {
  titulo: string; descricao?: string; acao?: React.ReactNode;
}) {
  return (
    <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-[30px] font-extrabold tracking-tight text-strong">
          {titulo}
        </h1>
        {descricao && (
          <p className="mt-1.5 text-[15px] text-muted">{descricao}</p>
        )}
      </div>
      {acao}
    </div>
  );
}

/** Estado vazio, com o que fazer a seguir. */
export function Vazio({ titulo, texto, acao }: {
  titulo: string; texto: string; acao?: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-dashed border-line px-6 py-14
                    text-center">
      <p className="font-semibold text-strong">{titulo}</p>
      <p className="mx-auto mt-1.5 max-w-[46ch] text-[14px] text-muted">
        {texto}
      </p>
      {acao && <div className="mt-5">{acao}</div>}
    </div>
  );
}
