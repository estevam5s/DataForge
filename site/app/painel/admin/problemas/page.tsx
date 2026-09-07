'use client';

import { useEffect, useState } from 'react';
import { Cabecalho } from '@/components/painel/Casca';
import { SoAdmin, Tabela } from '@/components/painel/Admin';
import {
  listarProblemasAdmin, publicarProblema, type ProblemaAdmin,
} from '@/lib/supabase/admin';

export default function Problemas() {
  return (
    <SoAdmin>
      <Catalogo />
    </SoAdmin>
  );
}

function Catalogo() {
  const [lista, setLista] = useState<ProblemaAdmin[]>([]);
  const [erro, setErro] = useState<string | null>(null);

  const recarregar = () =>
    listarProblemasAdmin().then((r) => {
      setLista(r.dados);
      setErro(r.erro);
    });

  useEffect(() => {
    recarregar();
  }, []);

  const alternar = async (p: ProblemaAdmin) => {
    const falha = await publicarProblema(p.id, !p.publicado);
    if (falha) setErro(falha);
    else await recarregar();
  };

  const publicados = lista.filter((p) => p.publicado).length;

  return (
    <>
      <Cabecalho
        titulo="Problemas"
        descricao={`${publicados} de ${lista.length} publicados. Despublicar tira o problema da prática sem apagar o histórico de quem já resolveu.`}
      />

      {erro && (
        <p className="mb-4 rounded-lg border border-accent/40 bg-accent/8 px-4 py-2.5 text-[13.5px] text-body">
          {erro}
        </p>
      )}

      <Tabela cabecalho={['#', 'Título', 'Dificuldade', 'Categoria', 'Estado', '']}>
        {lista.map((p) => (
          <tr key={p.id} className="hover:bg-raised/30">
            <td className="px-4 py-2.5 tabular-nums text-muted">{p.ordem + 1}</td>
            <td className="px-4 py-2.5">
              <span className="font-medium text-strong">{p.titulo}</span>
              <span className="ml-2 font-mono text-[11.5px] text-muted">{p.slug}</span>
            </td>
            <td className="px-4 py-2.5 text-body">{p.dificuldade}</td>
            <td className="px-4 py-2.5 text-muted">{p.categoria}</td>
            <td className="px-4 py-2.5">
              <span
                className={`rounded px-1.5 py-px text-[10.5px] font-bold uppercase ${
                  p.publicado
                    ? 'bg-emerald-400/12 text-emerald-400'
                    : 'bg-muted/12 text-muted'
                }`}
              >
                {p.publicado ? 'publicado' : 'oculto'}
              </span>
            </td>
            <td className="px-4 py-2.5 text-right">
              <button
                onClick={() => alternar(p)}
                className="rounded-lg border border-line px-2.5 py-1 text-[12px] text-muted transition-colors hover:text-strong"
              >
                {p.publicado ? 'ocultar' : 'publicar'}
              </button>
            </td>
          </tr>
        ))}
      </Tabela>

      <p className="mt-4 text-[13px] leading-[21px] text-muted">
        O catálogo vem de <code className="font-mono">problemas/catalogo.py</code>, e
        cada solução de referência é verificada contra todos os casos antes de
        subir — <code className="font-mono">python3 scripts/gerar_problemas.py</code>.
        Um problema cuja própria solução não passa nunca chega aqui.
      </p>
    </>
  );
}
