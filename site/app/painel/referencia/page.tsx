'use client';

import { useEffect, useMemo, useState } from 'react';
import { Cabecalho } from '@/components/painel/Casca';

/**
 * Referência da linguagem, servida pela API.
 *
 * Os dados vêm de `/api/*.json`, gerados por `scripts/gerar_api.py` a
 * partir do próprio código: as palavras reservadas saem de `tokens.py`,
 * as funções de `builtins.py`, os módulos da biblioteca e os comandos do
 * `cli.py`. Nada aqui é digitado à mão, então a referência não pode
 * descrever uma linguagem que não existe mais.
 */

type Sintaxe = {
  versao: string;
  reservadas: { palavra: string; descricao: string; equivalente: string }[];
  contextuais: {
    palavra: string; descricao: string; equivalente: string; onde: string;
  }[];
  operadores: { simbolo: string; descricao: string; equivalente: string }[];
  regras: string[];
};

type Modulos = {
  total_modulos: number;
  total_simbolos: number;
  modulos: {
    nome: string;
    apelidos: string[];
    total: number;
    simbolos: { nome: string; assinatura: string; resumo: string }[];
  }[];
};

type Comandos = {
  total: number;
  grupos: {
    grupo: string;
    comandos: {
      nome: string; uso: string; resumo: string; detalhe: string;
      opcoes: { flag: string; descricao: string }[];
      exemplos: { comando: string; nota: string }[];
    }[];
  }[];
};

type Erros = {
  total: number;
  codigos: {
    codigo: string; titulo: string; explicacao: string;
    exemplo: string; solucao: string;
  }[];
};

type Aba = 'sintaxe' | 'biblioteca' | 'cli' | 'erros';

export default function Referencia() {
  const [aba, setAba] = useState<Aba>('sintaxe');
  const [busca, setBusca] = useState('');

  const [sintaxe, setSintaxe] = useState<Sintaxe | null>(null);
  const [modulos, setModulos] = useState<Modulos | null>(null);
  const [comandos, setComandos] = useState<Comandos | null>(null);
  const [erros, setErros] = useState<Erros | null>(null);
  const [falhou, setFalhou] = useState(false);

  useEffect(() => {
    Promise.all([
      fetch('/api/sintaxe.json').then((r) => r.json()),
      fetch('/api/modulos.json').then((r) => r.json()),
      fetch('/api/comandos.json').then((r) => r.json()),
      fetch('/api/erros.json').then((r) => r.json()),
    ])
      .then(([s, m, c, e]) => {
        setSintaxe(s);
        setModulos(m);
        setComandos(c);
        setErros(e);
      })
      .catch(() => setFalhou(true));
  }, []);

  const filtrar = (texto: string) =>
    busca === '' || texto.toLowerCase().includes(busca.toLowerCase());

  const abas: { id: Aba; nome: string; contagem?: number }[] = [
    { id: 'sintaxe', nome: 'Sintaxe', contagem: sintaxe?.reservadas.length },
    { id: 'biblioteca', nome: 'Biblioteca', contagem: modulos?.total_simbolos },
    { id: 'cli', nome: 'Comandos', contagem: comandos?.total },
    { id: 'erros', nome: 'Erros', contagem: erros?.total },
  ];

  if (falhou) {
    return (
      <>
        <Cabecalho titulo="Referência" />
        <div className="rounded-xl border border-accent/40 bg-accent/8 px-4 py-3 text-[14px]">
          <strong className="text-strong">Não consegui carregar a API.</strong>{' '}
          <span className="text-muted">
            Rode <code className="font-mono">python3 scripts/gerar_api.py</code> e
            recarregue.
          </span>
        </div>
      </>
    );
  }

  return (
    <>
      <Cabecalho
        titulo="Referência"
        descricao="Servida pela API da linguagem, gerada do próprio código-fonte."
      />

      <div className="mb-5 flex flex-wrap items-center gap-3">
        <div className="flex flex-wrap gap-1">
          {abas.map((a) => (
            <button
              key={a.id}
              onClick={() => setAba(a.id)}
              className={`flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-[13.5px] font-semibold transition-colors ${
                aba === a.id
                  ? 'bg-accent text-white'
                  : 'bg-raised/40 text-muted hover:text-strong'
              }`}
            >
              {a.nome}
              {a.contagem !== undefined && (
                <span className={aba === a.id ? 'text-white/70' : 'text-muted/70'}>
                  {a.contagem}
                </span>
              )}
            </button>
          ))}
        </div>

        <input
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          placeholder="Filtrar…"
          className="ml-auto w-full max-w-[240px] rounded-xl border border-line bg-raised/40 px-3 py-2 text-[13.5px] outline-none transition-colors placeholder:text-muted focus:border-accent/50"
        />
      </div>

      {aba === 'sintaxe' && sintaxe && (
        <div className="space-y-6">
          <Bloco titulo={`${sintaxe.reservadas.length} palavras reservadas`}>
            <Grade>
              {sintaxe.reservadas
                .filter((r) => filtrar(r.palavra + r.descricao))
                .map((r) => (
                  <Verbete
                    key={r.palavra}
                    termo={r.palavra}
                    descricao={r.descricao}
                    nota={r.equivalente}
                  />
                ))}
            </Grade>
          </Bloco>

          <Bloco
            titulo={`${sintaxe.contextuais.length} palavras contextuais`}
            aviso="Só valem no lugar certo. Fora dali, continuam sendo nomes livres."
          >
            <Grade>
              {sintaxe.contextuais
                .filter((c) => filtrar(c.palavra + c.descricao))
                .map((c) => (
                  <Verbete
                    key={c.palavra}
                    termo={c.palavra}
                    descricao={c.descricao}
                    nota={c.onde}
                  />
                ))}
            </Grade>
          </Bloco>

          <Bloco titulo="Operadores">
            <Grade>
              {sintaxe.operadores
                .filter((o) => filtrar(o.simbolo + o.descricao))
                .map((o) => (
                  <Verbete
                    key={o.simbolo}
                    termo={o.simbolo}
                    descricao={o.descricao}
                    nota={o.equivalente}
                  />
                ))}
            </Grade>
          </Bloco>

          <Bloco titulo="Regras que pegam quem está começando">
            <ul className="space-y-2">
              {sintaxe.regras.map((regra, i) => (
                <li key={i} className="flex gap-2.5 text-[14px] leading-[23px] text-body">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent/70" />
                  {regra}
                </li>
              ))}
            </ul>
          </Bloco>
        </div>
      )}

      {aba === 'biblioteca' && modulos && (
        <div className="space-y-4">
          <p className="text-[13.5px] text-muted">
            {modulos.total_modulos} módulos, {modulos.total_simbolos} símbolos.
          </p>
          {modulos.modulos.map((m) => {
            const simbolos = m.simbolos.filter((s) => filtrar(s.nome + s.resumo));
            if (busca && simbolos.length === 0) return null;
            return (
              <details
                key={m.nome}
                open={Boolean(busca)}
                className="rounded-xl border border-line bg-raised/25"
              >
                <summary className="flex cursor-pointer items-center gap-2.5 px-4 py-3">
                  <span className="font-mono text-[14px] font-semibold text-strong">
                    {m.nome}
                  </span>
                  <span className="text-[12px] text-muted">{m.total} símbolos</span>
                  {m.apelidos.length > 0 && (
                    <span className="text-[11.5px] text-muted/70">
                      também: {m.apelidos.join(', ')}
                    </span>
                  )}
                </summary>
                <div className="border-t border-line/60 px-4 py-3">
                  <Grade>
                    {simbolos.map((s) => (
                      <Verbete
                        key={s.nome}
                        termo={s.nome + (s.assinatura || '')}
                        descricao={s.resumo}
                      />
                    ))}
                  </Grade>
                </div>
              </details>
            );
          })}
        </div>
      )}

      {aba === 'cli' && comandos && (
        <div className="space-y-5">
          {comandos.grupos.map((g) => {
            const lista = g.comandos.filter((c) => filtrar(c.nome + c.resumo));
            if (lista.length === 0) return null;
            return (
              <Bloco key={g.grupo} titulo={g.grupo}>
                <div className="space-y-3">
                  {lista.map((c) => (
                    <div
                      key={c.nome}
                      className="rounded-lg border border-line/60 bg-black/20 p-3.5"
                    >
                      <p className="font-mono text-[13.5px] font-semibold text-accent">
                        {c.uso}
                      </p>
                      <p className="mt-1 text-[13.5px] text-body">{c.resumo}</p>
                      {c.opcoes.length > 0 && (
                        <ul className="mt-2 space-y-0.5">
                          {c.opcoes.map((o) => (
                            <li key={o.flag} className="text-[12.5px] text-muted">
                              <code className="font-mono text-body">{o.flag}</code>{' '}
                              — {o.descricao}
                            </li>
                          ))}
                        </ul>
                      )}
                      {c.exemplos.length > 0 && (
                        <div className="mt-2 space-y-0.5">
                          {c.exemplos.map((e) => (
                            <p key={e.comando} className="font-mono text-[12px] text-muted">
                              $ {e.comando}
                              {e.nota && (
                                <span className="ml-2 text-muted/60"># {e.nota}</span>
                              )}
                            </p>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </Bloco>
            );
          })}
        </div>
      )}

      {aba === 'erros' && erros && (
        <div className="space-y-3">
          {erros.codigos
            .filter((e) => filtrar(e.codigo + e.titulo + e.explicacao))
            .map((e) => (
              <div key={e.codigo} className="rounded-xl border border-line bg-raised/25 p-4">
                <div className="flex flex-wrap items-baseline gap-2.5">
                  <span className="rounded bg-accent/12 px-2 py-0.5 font-mono text-[12px] font-bold text-accent">
                    {e.codigo}
                  </span>
                  <span className="text-[15px] font-semibold text-strong">{e.titulo}</span>
                </div>
                <p className="mt-2 text-[13.5px] leading-[22px] text-body">{e.explicacao}</p>
                {e.exemplo && (
                  <pre className="mt-2.5 overflow-x-auto rounded-lg bg-black/30 p-3 font-mono text-[12px] text-muted">
                    {e.exemplo}
                  </pre>
                )}
                {e.solucao && (
                  <p className="mt-2 text-[13px] text-muted">
                    <span className="font-semibold text-body">Como resolver: </span>
                    {e.solucao}
                  </p>
                )}
              </div>
            ))}
        </div>
      )}

      {!sintaxe && !falhou && (
        <div className="h-40 animate-pulse rounded-xl border border-line bg-raised/25" />
      )}
    </>
  );
}

function Bloco({
  titulo,
  aviso,
  children,
}: {
  titulo: string;
  aviso?: string;
  children: React.ReactNode;
}) {
  return (
    <section>
      <h2 className="mb-1 text-[15px] font-bold text-strong">{titulo}</h2>
      {aviso && <p className="mb-3 text-[13px] text-muted">{aviso}</p>}
      {!aviso && <div className="mb-3" />}
      {children}
    </section>
  );
}

function Grade({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">{children}</div>
  );
}

function Verbete({
  termo,
  descricao,
  nota,
}: {
  termo: string;
  descricao: string;
  nota?: string;
}) {
  return (
    <div className="rounded-lg border border-line/60 bg-black/20 px-3 py-2">
      <p className="break-all font-mono text-[12.5px] font-semibold text-accent">
        {termo}
      </p>
      {descricao && <p className="mt-0.5 text-[12.5px] text-body">{descricao}</p>}
      {nota && <p className="mt-0.5 text-[11.5px] text-muted">{nota}</p>}
    </div>
  );
}
