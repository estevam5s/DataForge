'use client';

import { useAuth } from '@/lib/supabase/auth';
import Link from 'next/link';

/**
 * Porta do painel administrativo.
 *
 * Esconder a tela no cliente **não é** o controle de acesso: o cliente é
 * do usuário e ele pode contornar qualquer verificação em JavaScript. O
 * controle real é a RLS do banco, que devolve zero linhas para quem não
 * tem papel. Isto aqui existe para não mostrar uma tela vazia e confusa
 * a quem não deveria estar nela.
 */
export function SoAdmin({ children }: { children: React.ReactNode }) {
  const { admin, carregando, usuario } = useAuth();

  if (carregando) {
    return <div className="h-40 animate-pulse rounded-xl border border-line bg-raised/25" />;
  }

  if (!usuario) {
    return (
      <div className="rounded-xl border border-line bg-raised/25 px-6 py-12 text-center">
        <p className="font-semibold text-strong">Entre para continuar</p>
        <Link href="/painel" className="mt-3 inline-block text-[14px] text-accent">
          ir para o painel
        </Link>
      </div>
    );
  }

  if (!admin) {
    return (
      <div className="rounded-xl border border-line bg-raised/25 px-6 py-12 text-center">
        <p className="font-semibold text-strong">Esta área é da administração.</p>
        <p className="mx-auto mt-1.5 max-w-[44ch] text-[14px] text-muted">
          Sua conta não tem esse papel. Se você deveria ter, peça a alguém que já é
          admin — a promoção acontece no banco, não por aqui.
        </p>
        <Link href="/painel" className="mt-4 inline-block text-[14px] text-accent">
          voltar ao painel
        </Link>
      </div>
    );
  }

  return <>{children}</>;
}

/** Cartão de número, com variação em relação ao período anterior. */
export function Numero({
  rotulo,
  valor,
  nota,
  destaque = false,
}: {
  rotulo: string;
  valor: string | number;
  nota?: string;
  destaque?: boolean;
}) {
  return (
    <div
      className={`rounded-xl border p-4 ${
        destaque ? 'border-accent/40 bg-accent/8' : 'border-line bg-raised/25'
      }`}
    >
      <p className="text-[11px] font-bold uppercase tracking-wide text-muted">{rotulo}</p>
      <p
        className={`mt-1 text-[26px] font-extrabold tabular-nums ${
          destaque ? 'text-accent' : 'text-strong'
        }`}
      >
        {valor}
      </p>
      {nota && <p className="mt-0.5 text-[12px] text-muted">{nota}</p>}
    </div>
  );
}

/**
 * Gráfico de barras em SVG.
 *
 * Uma biblioteca de gráficos custaria 100 KB para desenhar retângulos.
 * Quando a necessidade crescer além disso, aí vale a dependência.
 */
export function Barras({
  dados,
  rotulo,
}: {
  dados: { chave: string; valor: number }[];
  rotulo: string;
}) {
  const maior = Math.max(...dados.map((d) => d.valor), 1);

  return (
    <div className="rounded-xl border border-line bg-raised/25 p-4">
      <p className="mb-4 text-[11px] font-bold uppercase tracking-wide text-muted">
        {rotulo}
      </p>
      <div className="flex h-[140px] items-end gap-1">
        {dados.map((d) => (
          <div key={d.chave} className="group relative flex-1">
            <div
              className="rounded-t bg-accent/70 transition-all duration-500 group-hover:bg-accent"
              style={{ height: `${Math.max((d.valor / maior) * 130, 2)}px` }}
            />
            {/* O rótulo só aparece no hover: com 30 barras, todos juntos
                viram uma mancha ilegível. */}
            <span className="pointer-events-none absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap rounded bg-black/85 px-1.5 py-0.5 text-[10.5px] text-white opacity-0 transition-opacity group-hover:opacity-100">
              {d.chave}: {d.valor}
            </span>
          </div>
        ))}
      </div>
      {dados.length > 0 && (
        <div className="mt-2 flex justify-between text-[11px] text-muted">
          <span>{dados[0].chave}</span>
          <span>{dados[dados.length - 1].chave}</span>
        </div>
      )}
    </div>
  );
}

/** Tabela simples, com cabeçalho fixo. */
export function Tabela({
  cabecalho,
  children,
}: {
  cabecalho: string[];
  children: React.ReactNode;
}) {
  return (
    <div className="overflow-x-auto rounded-xl border border-line">
      <table className="w-full text-[13.5px]">
        <thead className="bg-raised/40">
          <tr>
            {cabecalho.map((c) => (
              <th
                key={c}
                className="whitespace-nowrap px-4 py-2.5 text-left text-[11px] font-bold uppercase tracking-wide text-muted"
              >
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-line/60">{children}</tbody>
      </table>
    </div>
  );
}
