'use client';

import { useEffect, useState } from 'react';
import { Cabecalho, Vazio } from '@/components/painel/Casca';
import { CodeBlock } from '@/components/CodeBlock';
import { useAuth } from '@/lib/supabase/auth';
import {
  criarToken, listarTokens, revogarToken, type TokenDePublicacao,
} from '@/lib/supabase/comunidade';

export default function PaginaTokens() {
  const { usuario, carregando } = useAuth();
  const [lista, setLista] = useState<TokenDePublicacao[]>([]);
  const [nome, setNome] = useState('');
  const [criado, setCriado] = useState<string | null>(null);
  const [copiado, setCopiado] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  const recarregar = () => listarTokens().then((r) => {
    setLista(r.dados);
    setErro(r.erro);
  });

  useEffect(() => { if (usuario) recarregar(); }, [usuario]);

  async function criar(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    const r = await criarToken(nome.trim());
    if (r.erro) { setErro(r.erro); return; }
    setCriado(r.token);
    setCopiado(false);
    setNome('');
    recarregar();
  }

  async function revogar(t: TokenDePublicacao) {
    if (!confirm(
      `Revogar "${t.nome}"?\n\nQualquer máquina que o use para de publicar `
      + 'na hora. Isso não pode ser desfeito — crie outro se precisar.')) return;
    const falha = await revogarToken(t.id);
    if (falha) setErro(falha); else recarregar();
  }

  if (carregando) {
    return <div className="h-40 animate-pulse rounded-xl border border-line bg-raised/25" />;
  }
  if (!usuario) {
    return (
      <>
        <Cabecalho titulo="Tokens de publicação" />
        <Vazio titulo="Entre para criar um token"
               texto="O token publica pacotes em seu nome, e por isso fica ligado à sua conta." />
      </>
    );
  }

  const ativos = lista.filter((t) => !t.revogado_em);

  return (
    <>
      <Cabecalho
        titulo="Tokens de publicação"
        descricao="Para publicar pelo terminal, com dataforge login e dataforge publish --remoto."
      />

      {erro && (
        <p role="alert" className="mb-5 rounded-lg border border-accent/40
                                   bg-accent/8 px-4 py-2.5 text-[13.5px] text-body">
          {erro}
        </p>
      )}

      {/* ── o token recém-criado ──
          Ele aparece aqui e em lugar nenhum mais: o banco guarda só o
          sha256. Poder relê-lo depois faria do banco um cofre de
          credenciais ativas — exatamente o que guardar o hash evita. */}
      {criado && (
        <section className="mb-8 rounded-xl border border-accent/50 bg-accent/8 px-5 py-4">
          <h2 className="text-[14px] font-semibold text-strong">
            Copie agora — ele não aparece de novo
          </h2>
          <p className="mt-1 text-[13px] text-body">
            O banco guarda só o <code>sha256</code> dele. Não há como
            recuperá-lo depois; se o perder, revogue e crie outro.
          </p>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <code className="min-w-0 flex-1 overflow-x-auto rounded-lg border
                             border-line bg-surface px-3 py-2 font-mono
                             text-[13px] text-strong">
              {criado}
            </code>
            <button
              onClick={() => {
                void navigator.clipboard?.writeText(criado);
                setCopiado(true);
              }}
              className="shrink-0 rounded-lg bg-accent px-4 py-2 text-[13px]
                         font-semibold text-white"
            >
              {copiado ? 'Copiado' : 'Copiar'}
            </button>
          </div>
          <div className="mt-4">
            <CodeBlock lang="bash" code={`dataforge login ${criado}`} />
          </div>
          <button
            onClick={() => setCriado(null)}
            className="mt-3 text-[12.5px] text-muted underline"
          >
            já guardei
          </button>
        </section>
      )}

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div>
          {/* ── criar ── */}
          <form onSubmit={criar} className="mb-8 flex flex-wrap items-end gap-3">
            <div className="min-w-[220px] flex-1">
              <label htmlFor="nome" className="mb-1.5 block text-[13px]
                                               font-semibold text-strong">
                Onde ele vai ser usado
              </label>
              <input
                id="nome"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                required
                maxLength={60}
                placeholder="notebook, CI do projeto X"
                className="w-full rounded-lg border border-line bg-transparent
                           px-3 py-2 text-[14px] text-strong outline-none
                           placeholder:text-muted focus:border-accent/60"
              />
              <p className="mt-1.5 text-[12.5px] text-muted">
                É por este nome que você vai saber qual revogar depois.
              </p>
            </div>
            <button
              type="submit"
              disabled={!nome.trim() || ativos.length >= 10}
              className="rounded-lg bg-accent px-5 py-2.5 text-[14px]
                         font-semibold text-white disabled:opacity-40"
            >
              Criar token
            </button>
          </form>

          {ativos.length >= 10 && (
            <p className="mb-6 text-[13px] text-muted">
              Dez tokens ativos é o limite. Revogue os que não usa.
            </p>
          )}

          {/* ── a lista ── */}
          {lista.length === 0 ? (
            <Vazio
              titulo="Nenhum token ainda"
              texto="Crie um acima para publicar pelo terminal em vez do formulário."
            />
          ) : (
            <ul className="space-y-2.5">
              {lista.map((t) => (
                <li key={t.id}
                    className={`rounded-xl border px-4 py-3 ${
                      t.revogado_em ? 'border-line opacity-55' : 'border-line'
                    }`}>
                  <div className="flex flex-wrap items-baseline justify-between gap-3">
                    <div>
                      <span className="text-[14px] font-medium text-strong">
                        {t.nome}
                      </span>
                      <code className="ml-2.5 text-[12.5px] text-muted">
                        {t.prefixo}…
                      </code>
                      {t.revogado_em && (
                        <span className="ml-2 text-[11.5px] text-muted">
                          revogado
                        </span>
                      )}
                    </div>
                    {!t.revogado_em && (
                      <button
                        onClick={() => revogar(t)}
                        className="shrink-0 rounded-lg border border-line px-3
                                   py-1 text-[12.5px] text-body
                                   hover:border-accent/50 hover:text-strong"
                      >
                        Revogar
                      </button>
                    )}
                  </div>
                  <p className="mt-1 text-[12.5px] text-muted">
                    {t.usos} uso{t.usos === 1 ? '' : 's'}
                    {t.ultimo_uso
                      ? ` · último em ${new Date(t.ultimo_uso).toLocaleDateString('pt-BR')}`
                      : ' · nunca usado'}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* ── como usar ── */}
        <aside>
          <h2 className="mb-3 text-[13px] font-semibold uppercase tracking-wide text-muted">
            Publicar pelo terminal
          </h2>
          <CodeBlock
            lang="bash"
            code={`# uma vez, por máquina
dataforge login

# a cada versão
dataforge pack
dataforge publish --remoto \\
  --tarball=https://.../meu-{versao}.tar.gz

dataforge whoami   # qual token está em uso
dataforge logout   # esquece nesta máquina`}
          />
          <p className="mt-3 text-[12.5px] text-muted">
            O token fica em <code>~/.dataforge/credenciais.json</code>, com
            permissão 600. Na CI, use a variável{' '}
            <code>DATAFORGE_TOKEN</code> — ela vence o arquivo e não deixa
            rastro em disco.
          </p>
          <p className="mt-3 text-[12.5px] text-muted">
            <a href="/docs/pacotes/publicar" className="text-accent hover:underline">
              A documentação completa →
            </a>
          </p>
        </aside>
      </div>
    </>
  );
}
