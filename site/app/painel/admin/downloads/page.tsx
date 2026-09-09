'use client';

import { useEffect, useState } from 'react';
import { Cabecalho } from '@/components/painel/Casca';
import { Barras, Numero, SoAdmin, Tabela } from '@/components/painel/Admin';
import {
  carregarDownloads,
  type PainelDownloads,
} from '@/lib/supabase/admin';

export default function Downloads() {
  return (
    <SoAdmin>
      <Painel />
    </SoAdmin>
  );
}

const PERIODOS = [
  { dias: 7, rotulo: '7 dias' },
  { dias: 30, rotulo: '30 dias' },
  { dias: 90, rotulo: '90 dias' },
  { dias: 365, rotulo: '1 ano' },
];

/** O nome legível de cada origem, e a ordem em que elas aparecem. */
const ORIGENS: Record<string, { nome: string; desc: string }> = {
  script: { nome: 'Script (curl)', desc: 'macOS e Linux' },
  powershell: { nome: 'PowerShell', desc: 'Windows' },
  pip: { nome: 'pip', desc: 'ambiente Python próprio' },
  tarball: { nome: 'Tarball', desc: 'baixou o .tar.gz direto' },
  docker: { nome: 'Docker', desc: 'imagem do Docker Hub' },
  vsix: { nome: 'Extensão', desc: 'VS Code' },
  site: { nome: 'Site', desc: 'pela página de instalação' },
};

function Painel() {
  const [dados, setDados] = useState<PainelDownloads | null>(null);
  const [dias, setDias] = useState(30);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    setCarregando(true);
    carregarDownloads(dias).then((r) => {
      setDados(r.dados);
      setErro(r.erro);
      setCarregando(false);
    });
  }, [dias]);

  const dia = (iso: string) => iso.slice(8, 10) + '/' + iso.slice(5, 7);

  // A média diária é o número que diz se está crescendo — o total
  // sozinho só cresce, sempre, e nunca informa nada.
  const media = dados && dados.por_dia.length
    ? Math.round(dados.total_periodo / dados.por_dia.length)
    : 0;

  const origens = dados
    ? Object.entries(dados.por_origem).sort((a, b) => b[1] - a[1])
    : [];
  const sistemas = dados
    ? Object.entries(dados.por_sistema).sort((a, b) => b[1] - a[1])
    : [];
  const versoes = dados
    ? Object.entries(dados.por_versao).sort((a, b) => b[1] - a[1])
    : [];

  return (
    <>
      <Cabecalho
        titulo="Downloads"
        descricao="Quantas pessoas instalaram a linguagem, por onde e de onde."
      />

      <div className="mb-5 flex flex-wrap items-center gap-1.5">
        {PERIODOS.map((p) => (
          <button
            key={p.dias}
            onClick={() => setDias(p.dias)}
            className={`rounded-lg px-3 py-1.5 text-[12.5px] font-medium transition-colors ${
              dias === p.dias
                ? 'bg-accent text-white'
                : 'border border-line text-muted hover:bg-raised hover:text-strong'
            }`}
          >
            {p.rotulo}
          </button>
        ))}
        {carregando && (
          <span className="ml-2 text-[12px] text-muted">carregando…</span>
        )}
      </div>

      {erro && (
        <div className="mb-5 rounded-xl border border-red-500/40 bg-red-500/8 p-3 text-[13px] text-red-400">
          {erro}
        </div>
      )}

      <div className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Numero
          rotulo="Total"
          valor={(dados?.total ?? 0).toLocaleString('pt-BR')}
          nota="desde o lançamento"
          destaque
        />
        <Numero
          rotulo={`Últimos ${dias} dias`}
          valor={(dados?.total_periodo ?? 0).toLocaleString('pt-BR')}
          nota={`${media}/dia em média`}
        />
        <Numero
          rotulo="Máquinas distintas"
          valor={(dados?.unicos_periodo ?? 0).toLocaleString('pt-BR')}
          nota="no período, sem repetir"
        />
        <Numero
          rotulo="Hoje"
          valor={(dados?.hoje ?? 0).toLocaleString('pt-BR')}
          nota="até agora"
        />
      </div>

      {dados && dados.por_dia.length > 0 && (
        <div className="mb-5">
          <Barras
            rotulo={`Instalações por dia — ${dias} dias`}
            dados={dados.por_dia.map((d) => ({
              chave: dia(d.dia),
              valor: d.total,
            }))}
          />
        </div>
      )}

      <div className="mb-5 grid gap-4 lg:grid-cols-2">
        <Fatia
          titulo="Por onde instalaram"
          itens={origens.map(([chave, n]) => ({
            nome: ORIGENS[chave]?.nome ?? chave,
            nota: ORIGENS[chave]?.desc,
            valor: n,
          }))}
          total={dados?.total_periodo ?? 0}
          vazio="nenhuma instalação no período"
        />
        <Fatia
          titulo="Sistema operacional"
          itens={sistemas.map(([chave, n]) => ({
            nome: chave === 'desconhecido' ? 'não informado' : chave,
            valor: n,
          }))}
          total={dados?.total_periodo ?? 0}
          vazio="sem dados de sistema"
        />
      </div>

      <div className="mb-5 grid gap-4 lg:grid-cols-2">
        <Fatia
          titulo="Versão instalada"
          itens={versoes.map(([chave, n]) => ({ nome: chave, valor: n }))}
          total={dados?.total_periodo ?? 0}
          vazio="sem dados de versão"
        />
        <Fatia
          titulo="País"
          itens={(dados?.por_pais ?? []).map((p) => ({
            nome: p.pais,
            valor: p.total,
          }))}
          total={dados?.total_periodo ?? 0}
          vazio="sem dados de origem"
        />
      </div>

      <div className="rounded-xl border border-line bg-raised/25 p-4">
        <p className="mb-3 text-[11px] font-bold uppercase tracking-wide text-muted">
          Últimas instalações
        </p>
        {dados && dados.ultimos.length > 0 ? (
          <Tabela cabecalho={['Quando', 'Origem', 'Sistema', 'Versão', 'País']}>
            {dados.ultimos.map((u, i) => (
              <tr key={i} className="border-t border-line/40">
                <td className="py-1.5 pr-3 text-[12.5px] tabular-nums text-muted">
                  {new Date(u.quando).toLocaleString('pt-BR', {
                    day: '2-digit', month: '2-digit',
                    hour: '2-digit', minute: '2-digit',
                  })}
                </td>
                <td className="py-1.5 pr-3 text-[12.5px] text-strong">
                  {ORIGENS[u.origem]?.nome ?? u.origem}
                </td>
                <td className="py-1.5 pr-3 text-[12.5px] text-body">
                  {u.sistema ?? '—'}
                </td>
                <td className="py-1.5 pr-3 font-mono text-[12px] text-body">
                  {u.versao}
                </td>
                <td className="py-1.5 text-[12.5px] text-body">
                  {u.pais ?? '—'}
                </td>
              </tr>
            ))}
          </Tabela>
        ) : (
          <p className="text-[13px] text-muted">
            Nenhuma instalação registrada ainda.
          </p>
        )}
      </div>

      <div className="mt-5 rounded-xl border border-line bg-surface/40 p-4">
        <p className="text-[12.5px] font-semibold text-strong">
          O que é contado, e o que não é
        </p>
        <p className="mt-1.5 text-[12.5px] leading-[20px] text-muted">
          Cada instalação envia a origem, a versão, o sistema e a
          arquitetura. <strong className="text-strong">O endereço IP não é
          guardado</strong> — o que fica é um hash com um sal que gira
          todo dia, o suficiente para contar máquinas distintas em 24 h e
          nada além disso. Quem instala pode desligar o envio com{' '}
          <code className="rounded bg-base px-1 py-0.5 font-mono text-[11.5px] text-strong">
            DATAFORGE_SEM_TELEMETRIA=1
          </code>
          .
        </p>
      </div>
    </>
  );
}

/** Uma lista com barra proporcional — mais legível que pizza. */
function Fatia({
  titulo,
  itens,
  total,
  vazio,
}: {
  titulo: string;
  itens: { nome: string; nota?: string; valor: number }[];
  total: number;
  vazio: string;
}) {
  const maior = Math.max(...itens.map((i) => i.valor), 1);

  return (
    <div className="rounded-xl border border-line bg-raised/25 p-4">
      <p className="mb-3 text-[11px] font-bold uppercase tracking-wide text-muted">
        {titulo}
      </p>
      {itens.length === 0 ? (
        <p className="text-[13px] text-muted">{vazio}</p>
      ) : (
        <div className="space-y-2.5">
          {itens.map((i) => (
            <div key={i.nome}>
              <div className="mb-1 flex items-baseline justify-between gap-2">
                <span className="text-[13px] text-strong">
                  {i.nome}
                  {i.nota && (
                    <span className="ml-1.5 text-[11.5px] text-muted">
                      {i.nota}
                    </span>
                  )}
                </span>
                <span className="shrink-0 text-[12.5px] tabular-nums text-muted">
                  {i.valor.toLocaleString('pt-BR')}
                  {total > 0 && (
                    <span className="ml-1 text-[11px]">
                      ({Math.round((i.valor / total) * 100)}%)
                    </span>
                  )}
                </span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-line/50">
                <div
                  className="h-full rounded-full bg-accent transition-all duration-500"
                  style={{ width: `${(i.valor / maior) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
