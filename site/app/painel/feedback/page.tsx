'use client';

import { useEffect, useState } from 'react';
import { Cabecalho, Vazio } from '@/components/painel/Casca';
import { useAuth } from '@/lib/supabase/auth';
import {
  enviarFeedback, meusFeedbacks, TIPOS,
  type Feedback, type TipoDeFeedback,
} from '@/lib/supabase/comunidade';
import { allRoutes } from '@/lib/nav';

const ESTADOS: Record<Feedback['estado'], { rotulo: string; cor: string }> = {
  novo: { rotulo: 'Enviado', cor: 'text-muted' },
  lido: { rotulo: 'Lido', cor: 'text-body' },
  respondido: { rotulo: 'Respondido', cor: 'text-accent' },
  arquivado: { rotulo: 'Arquivado', cor: 'text-muted' },
};

export default function PaginaFeedback() {
  const { usuario, carregando: carregandoAuth } = useAuth();

  const [tipo, setTipo] = useState<TipoDeFeedback>('problema');
  const [assunto, setAssunto] = useState('');
  const [mensagem, setMensagem] = useState('');
  const [pagina, setPagina] = useState('');

  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [enviado, setEnviado] = useState(false);
  const [meus, setMeus] = useState<Feedback[]>([]);

  const recarregar = () => meusFeedbacks().then((r) => setMeus(r.dados));
  useEffect(() => { if (usuario) recarregar(); }, [usuario]);

  const dicaDoTipo = TIPOS.find((t) => t.valor === tipo)?.dica ?? '';

  // O contador aparece só perto do limite. Mostrado desde o primeiro
  // caractere ele vira um cronômetro: a pessoa escreve para o número,
  // e não para quem vai ler.
  const faltam = 4000 - mensagem.length;
  const curto = mensagem.trim().length > 0 && mensagem.trim().length < 10;

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setEnviando(true);
    const falha = await enviarFeedback({
      tipo,
      assunto: assunto.trim(),
      mensagem: mensagem.trim(),
      pagina: pagina || undefined,
      versao: '1.0.0',
    });
    setEnviando(false);
    if (falha) { setErro(falha); return; }
    setAssunto(''); setMensagem(''); setPagina('');
    setEnviado(true);
    recarregar();
  }

  if (carregandoAuth) {
    return <div className="h-40 animate-pulse rounded-xl border border-line bg-raised/25" />;
  }

  if (!usuario) {
    return (
      <>
        <Cabecalho titulo="Feedback" />
        <Vazio
          titulo="Entre para enviar"
          texto="O feedback fica ligado à sua conta para que a resposta chegue até você — e para que ninguém escreva em seu nome."
        />
      </>
    );
  }

  return (
    <>
      <Cabecalho
        titulo="Feedback"
        descricao="O que funcionou, o que não funcionou, e o que falta. Vai direto para quem escreve a linguagem."
      />

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_340px]">
        <form onSubmit={enviar} className="space-y-5">
          {/* ── tipo ── */}
          <fieldset>
            <legend className="mb-2 text-[13px] font-semibold text-strong">
              Do que se trata
            </legend>
            <div className="flex flex-wrap gap-2">
              {TIPOS.map((t) => (
                <button
                  key={t.valor}
                  type="button"
                  onClick={() => setTipo(t.valor)}
                  aria-pressed={tipo === t.valor}
                  className={`rounded-lg border px-3 py-1.5 text-[13.5px] transition-colors ${
                    tipo === t.valor
                      ? 'border-accent/60 bg-accent/10 font-medium text-accent'
                      : 'border-line text-body hover:border-line hover:text-strong'
                  }`}
                >
                  {t.rotulo}
                </button>
              ))}
            </div>
            <p className="mt-2 text-[12.5px] text-muted">{dicaDoTipo}</p>
          </fieldset>

          {/* ── assunto ── */}
          <div>
            <label htmlFor="assunto" className="mb-1.5 block text-[13px] font-semibold text-strong">
              Assunto
            </label>
            <input
              id="assunto"
              value={assunto}
              onChange={(e) => setAssunto(e.target.value)}
              required
              minLength={3}
              maxLength={120}
              placeholder="Em uma linha"
              className="w-full rounded-lg border border-line bg-transparent px-3 py-2
                         text-[14px] text-strong outline-none
                         placeholder:text-muted focus:border-accent/60"
            />
          </div>

          {/* ── mensagem ── */}
          <div>
            <div className="mb-1.5 flex items-baseline justify-between">
              <label htmlFor="mensagem" className="text-[13px] font-semibold text-strong">
                O que aconteceu
              </label>
              {faltam < 400 && (
                <span className="text-[11.5px] tabular-nums text-muted">
                  {faltam} restantes
                </span>
              )}
            </div>
            <textarea
              id="mensagem"
              value={mensagem}
              onChange={(e) => setMensagem(e.target.value)}
              required
              minLength={10}
              maxLength={4000}
              rows={9}
              aria-describedby="ajuda-mensagem"
              placeholder={
                'O que você esperava, o que aconteceu, e como chegar lá de novo.\n\n'
                + 'Um trecho de código que reproduz vale mais que qualquer descrição.'
              }
              className="w-full resize-y rounded-lg border border-line bg-transparent px-3 py-2.5
                         font-mono text-[13px] leading-[1.6] text-strong outline-none
                         placeholder:text-muted focus:border-accent/60"
            />
            <p id="ajuda-mensagem" className="mt-1.5 text-[12.5px] text-muted">
              {curto
                ? 'Pelo menos dez caracteres — um "não funciona" sozinho não dá para agir.'
                : 'Os passos para reproduzir são a parte que mais ajuda.'}
            </p>
          </div>

          {/* ── página ──
              Transforma "está confuso" em "a página X está confusa". Sem
              isso, metade do feedback é impossível de agir. */}
          <div>
            <label htmlFor="pagina" className="mb-1.5 block text-[13px] font-semibold text-strong">
              Sobre qual página <span className="font-normal text-muted">(opcional)</span>
            </label>
            <select
              id="pagina"
              value={pagina}
              onChange={(e) => setPagina(e.target.value)}
              className="w-full rounded-lg border border-line bg-transparent px-3 py-2
                         text-[14px] text-strong outline-none focus:border-accent/60"
            >
              <option value="">Nenhuma em especial</option>
              {allRoutes.map((r) => (
                <option key={r.href} value={r.href}>{r.href}</option>
              ))}
            </select>
          </div>

          {erro && (
            <p
              role="alert"
              className="rounded-lg border border-accent/40 bg-accent/8 px-4 py-2.5
                         text-[13.5px] text-body"
            >
              {erro}
            </p>
          )}

          {enviado && !erro && (
            <p
              role="status"
              className="rounded-lg border border-line bg-raised/40 px-4 py-2.5
                         text-[13.5px] text-body"
            >
              Recebido. Ele aparece na lista ao lado, e você vê aqui quando for respondido.
            </p>
          )}

          <button
            type="submit"
            disabled={enviando || !assunto.trim() || mensagem.trim().length < 10}
            className="rounded-lg bg-accent px-5 py-2.5 text-[14px] font-semibold
                       text-white transition-opacity disabled:opacity-40"
          >
            {enviando ? 'Enviando…' : 'Enviar'}
          </button>
        </form>

        {/* ── o que eu já mandei ── */}
        <aside>
          <h2 className="mb-3 text-[13px] font-semibold uppercase tracking-wide text-muted">
            O que você enviou
          </h2>

          {meus.length === 0 ? (
            <p className="rounded-xl border border-dashed border-line px-4 py-8
                          text-center text-[13.5px] text-muted">
              Nada ainda.
            </p>
          ) : (
            <ul className="space-y-2.5">
              {meus.map((f) => (
                <li key={f.id} className="rounded-xl border border-line px-4 py-3">
                  <div className="flex items-baseline justify-between gap-3">
                    <span className="text-[14px] font-medium text-strong">
                      {f.assunto}
                    </span>
                    <span className={`shrink-0 text-[11.5px] ${ESTADOS[f.estado].cor}`}>
                      {ESTADOS[f.estado].rotulo}
                    </span>
                  </div>
                  <p className="mt-1 line-clamp-2 text-[13px] text-muted">
                    {f.mensagem}
                  </p>
                  {f.resposta && (
                    <p className="mt-2.5 border-l-2 border-accent/50 pl-3 text-[13px] text-body">
                      {f.resposta}
                    </p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </aside>
      </div>
    </>
  );
}
