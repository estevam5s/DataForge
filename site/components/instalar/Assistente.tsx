'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  COMANDOS,
  NOMES,
  type Sistema,
  detectarArquitetura,
  detectarSistema,
} from './Detectar';

/**
 * O assistente de instalação.
 *
 * Um instalador de verdade — o do Windows, o do VS Code — não é uma
 * linha de comando: é uma sequência de decisões, com a licença, o
 * destino, o que instalar junto, e a confirmação. Esta página é isso,
 * e ao final ela **monta o comando** que executa exatamente as
 * escolhas feitas.
 *
 * A escolha central de design: ela não baixa nem executa nada. Uma
 * página web não pode instalar um interpretador, e fingir que pode
 * seria pior que a linha de comando honesta. O que ela entrega é o
 * comando pronto, com as opções que o usuário escolheu, e a
 * explicação do que cada uma faz.
 */

type Passo = 'sistema' | 'licenca' | 'destino' | 'componentes' | 'pronto';

const PASSOS: { id: Passo; titulo: string }[] = [
  { id: 'sistema', titulo: 'Sistema' },
  { id: 'licenca', titulo: 'Licença' },
  { id: 'destino', titulo: 'Destino' },
  { id: 'componentes', titulo: 'Componentes' },
  { id: 'pronto', titulo: 'Instalar' },
];

type Componente = {
  id: string;
  nome: string;
  desc: string;
  tamanho: string;
  /** O que ele acrescenta ao comando. */
  flag?: string;
  /** Componentes que não se podem desmarcar. */
  fixo?: boolean;
};

const COMPONENTES: Componente[] = [
  {
    id: 'interpretador',
    nome: 'Interpretador e biblioteca padrão',
    desc: 'a linguagem, os 34 módulos Arcane, e as 34 ferramentas de linha de comando',
    tamanho: '4,2 MB',
    fixo: true,
  },
  {
    id: 'editor',
    nome: 'Extensão do editor',
    desc: 'cores, 103 snippets, Big-O no editor e o botão de rodar — VS Code, Cursor, Windsurf',
    tamanho: '180 KB',
    flag: '--com-editor',
  },
  {
    id: 'exemplos',
    nome: 'Exemplos e exercícios',
    desc: '43 programas comentados e 216 exercícios com solução',
    tamanho: '1,1 MB',
    flag: '--com-exemplos',
  },
  {
    id: 'path',
    nome: 'Acrescentar ao PATH',
    desc: 'para digitar `dataforge` de qualquer pasta',
    tamanho: '—',
    fixo: true,
  },
  {
    id: 'docs',
    nome: 'Abrir a documentação ao terminar',
    desc: 'o guia de primeiros passos, no navegador',
    tamanho: '—',
    flag: '--abrir-docs',
  },
];

const DESTINOS: Record<Sistema, { padrao: string; alternativo: string }> = {
  macos: { padrao: '~/.dataforge', alternativo: '/usr/local/dataforge' },
  linux: { padrao: '~/.dataforge', alternativo: '/opt/dataforge' },
  windows: {
    padrao: '%USERPROFILE%\\.dataforge',
    alternativo: 'C:\\Program Files\\DataForge',
  },
  desconhecido: { padrao: '~/.dataforge', alternativo: '/opt/dataforge' },
};

export function Assistente() {
  const [passo, setPasso] = useState<Passo>('sistema');
  const [sistema, setSistema] = useState<Sistema>('desconhecido');
  const [detectado, setDetectado] = useState<Sistema>('desconhecido');
  const [arquitetura, setArquitetura] = useState('desconhecida');
  const [aceitou, setAceitou] = useState(false);
  const [destino, setDestino] = useState<'padrao' | 'alternativo' | 'outro'>('padrao');
  const [outroDestino, setOutroDestino] = useState('');
  const [marcados, setMarcados] = useState<Set<string>>(
    () => new Set(['interpretador', 'editor', 'path']),
  );
  const [copiou, setCopiou] = useState(false);

  useEffect(() => {
    const s = detectarSistema();
    setSistema(s);
    setDetectado(s);
    setArquitetura(detectarArquitetura());
  }, []);

  const indice = PASSOS.findIndex((p) => p.id === passo);
  const destinos = DESTINOS[sistema];
  const caminhoFinal =
    destino === 'outro'
      ? outroDestino || destinos.padrao
      : destino === 'alternativo'
        ? destinos.alternativo
        : destinos.padrao;

  const comando = useMemo(() => {
    const base = COMANDOS[sistema];
    const flags = COMPONENTES.filter(
      (c) => c.flag && marcados.has(c.id),
    ).map((c) => c.flag);

    const usaPadrao = destino === 'padrao';

    if (sistema === 'windows') {
      const partes: string[] = [];
      if (!usaPadrao) partes.push(`$env:DATAFORGE_PREFIX="${caminhoFinal}"`);
      const sufixo = flags.length ? `; ${flags.join(' ')}` : '';
      partes.push(
        flags.length
          ? `irm https://dataforge-lang.vercel.app/instalar.ps1 | iex${sufixo ? '' : ''}`
          : base.comando,
      );
      if (flags.length) {
        return [
          ...(usaPadrao ? [] : [`$env:DATAFORGE_PREFIX="${caminhoFinal}"`]),
          `$env:DATAFORGE_EXTRAS="${flags.join(' ')}"`,
          'irm https://dataforge-lang.vercel.app/instalar.ps1 | iex',
        ].join('\n');
      }
      return partes.join('\n');
    }

    const prefixo = usaPadrao ? '' : `DATAFORGE_PREFIX=${caminhoFinal} `;
    if (!flags.length) return `${prefixo}${base.comando}`;
    // Com opções, o script vai para um arquivo primeiro: `| sh` não
    // repassa argumentos, e fingir que repassa daria um comando que
    // não funciona.
    return [
      'curl -fsSL https://dataforge-lang.vercel.app/instalar.sh -o instalar.sh',
      `${prefixo}sh instalar.sh ${flags.join(' ')}`,
    ].join('\n');
  }, [sistema, marcados, destino, caminhoFinal]);

  const alternar = (id: string) =>
    setMarcados((antes) => {
      const proximo = new Set(antes);
      proximo.has(id) ? proximo.delete(id) : proximo.add(id);
      return proximo;
    });

  const copiar = async () => {
    try {
      await navigator.clipboard.writeText(comando);
      setCopiou(true);
      setTimeout(() => setCopiou(false), 2000);
    } catch {
      /* clipboard bloqueado: o usuário seleciona à mão */
    }
  };

  const podeAvancar =
    (passo === 'sistema' && sistema !== 'desconhecido') ||
    (passo === 'licenca' && aceitou) ||
    passo === 'destino' ||
    passo === 'componentes';

  return (
    <div className="overflow-hidden rounded-2xl border border-line bg-surface/60">
      {/* barra de passos */}
      <div className="flex items-center gap-1 border-b border-line/70 bg-raised/40 px-3 py-2.5 sm:px-4">
        {PASSOS.map((p, i) => (
          <div key={p.id} className="flex items-center gap-1">
            <button
              onClick={() => i <= indice && setPasso(p.id)}
              disabled={i > indice}
              className={`flex items-center gap-1.5 rounded-lg px-2 py-1 text-[12px] transition-colors ${
                i === indice
                  ? 'bg-accent/12 font-semibold text-accent'
                  : i < indice
                    ? 'text-muted hover:text-strong'
                    : 'text-muted/40'
              }`}
            >
              <span
                className={`flex h-4 w-4 shrink-0 items-center justify-center rounded-full text-[9px] font-bold ${
                  i < indice
                    ? 'bg-accent text-white'
                    : i === indice
                      ? 'border border-accent text-accent'
                      : 'border border-line text-muted/50'
                }`}
              >
                {i < indice ? '✓' : i + 1}
              </span>
              <span className="hidden sm:inline">{p.titulo}</span>
            </button>
            {i < PASSOS.length - 1 && (
              <span className="text-line" aria-hidden>
                ·
              </span>
            )}
          </div>
        ))}
      </div>

      <div className="min-h-[290px] p-4 sm:p-6">
        {passo === 'sistema' && (
          <Etapa
            titulo="Onde você vai instalar?"
            descricao={
              detectado !== 'desconhecido'
                ? `Detectamos ${NOMES[detectado]}${arquitetura !== 'desconhecida' ? ` (${arquitetura})` : ''}. Se estiver errado, escolha outro — a detecção pelo navegador não é confiável.`
                : 'Não conseguimos detectar. Escolha o seu sistema.'
            }
          >
            <div className="grid gap-2 sm:grid-cols-3">
              {(['macos', 'linux', 'windows'] as Sistema[]).map((s) => (
                <button
                  key={s}
                  onClick={() => setSistema(s)}
                  className={`rounded-xl border p-3 text-left transition-all ${
                    sistema === s
                      ? 'border-accent bg-accent/8'
                      : 'border-line hover:border-line hover:bg-raised'
                  }`}
                >
                  <p className="text-[14px] font-semibold text-strong">
                    {NOMES[s]}
                  </p>
                  <p className="mt-0.5 text-[12px] text-muted">
                    {COMANDOS[s].shell}
                  </p>
                  {detectado === s && (
                    <p className="mt-1.5 text-[11px] font-medium text-accent">
                      detectado
                    </p>
                  )}
                </button>
              ))}
            </div>
            <p className="mt-4 text-[12.5px] leading-[19px] text-muted">
              Requisito: <strong className="text-strong">Python 3.10 ou mais novo</strong>.
              O macOS e a maioria das distribuições Linux já trazem. No Windows,
              o instalador avisa se faltar.
            </p>
          </Etapa>
        )}

        {passo === 'licenca' && (
          <Etapa
            titulo="Licença MIT"
            descricao="Curta e permissiva. Você pode usar em projeto comercial, modificar e redistribuir."
          >
            <div className="max-h-[168px] overflow-y-auto rounded-xl border border-line bg-base/60 p-3.5 font-mono text-[11.5px] leading-[18px] text-muted">
              <p className="mb-2">Copyright (c) 2026 Estevam Souza</p>
              <p className="mb-2">
                Permission is hereby granted, free of charge, to any person
                obtaining a copy of this software and associated documentation
                files (the &quot;Software&quot;), to deal in the Software
                without restriction, including without limitation the rights to
                use, copy, modify, merge, publish, distribute, sublicense,
                and/or sell copies of the Software, and to permit persons to
                whom the Software is furnished to do so, subject to the
                following conditions:
              </p>
              <p className="mb-2">
                The above copyright notice and this permission notice shall be
                included in all copies or substantial portions of the Software.
              </p>
              <p>
                THE SOFTWARE IS PROVIDED &quot;AS IS&quot;, WITHOUT WARRANTY OF
                ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
                WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
                AND NONINFRINGEMENT.
              </p>
            </div>
            <label className="mt-3.5 flex cursor-pointer items-start gap-2.5 text-[13.5px] text-body">
              <input
                type="checkbox"
                checked={aceitou}
                onChange={(e) => setAceitou(e.target.checked)}
                className="mt-0.5 h-4 w-4 shrink-0 accent-accent"
              />
              <span>
                Li e aceito os termos da licença MIT.
              </span>
            </label>
          </Etapa>
        )}

        {passo === 'destino' && (
          <Etapa
            titulo="Onde instalar"
            descricao="O DataForge cria um ambiente próprio e não mexe no Python do sistema. Desinstalar é apagar essa pasta."
          >
            <div className="space-y-2">
              <Opcao
                marcada={destino === 'padrao'}
                onClick={() => setDestino('padrao')}
                titulo={destinos.padrao}
                desc="recomendado — não pede senha de administrador"
              />
              <Opcao
                marcada={destino === 'alternativo'}
                onClick={() => setDestino('alternativo')}
                titulo={destinos.alternativo}
                desc={
                  sistema === 'windows'
                    ? 'para todos os usuários — precisa de PowerShell como administrador'
                    : 'para todos os usuários — precisa de sudo'
                }
              />
              <Opcao
                marcada={destino === 'outro'}
                onClick={() => setDestino('outro')}
                titulo="Outra pasta"
                desc="qualquer caminho onde você possa escrever"
              />
              {destino === 'outro' && (
                <input
                  value={outroDestino}
                  onChange={(e) => setOutroDestino(e.target.value)}
                  placeholder={destinos.padrao}
                  className="mt-1 w-full rounded-lg border border-line bg-base px-3 py-2 font-mono text-[12.5px] text-strong outline-none focus:border-accent"
                />
              )}
            </div>
            <p className="mt-3.5 text-[12.5px] text-muted">
              Espaço necessário:{' '}
              <strong className="text-strong">
                {tamanhoTotal(marcados)}
              </strong>
            </p>
          </Etapa>
        )}

        {passo === 'componentes' && (
          <Etapa
            titulo="O que instalar"
            descricao="O interpretador é obrigatório. O resto você escolhe."
          >
            <div className="space-y-1.5">
              {COMPONENTES.map((c) => {
                const marcado = c.fixo || marcados.has(c.id);
                return (
                  <label
                    key={c.id}
                    className={`flex cursor-pointer items-start gap-2.5 rounded-xl border p-3 transition-colors ${
                      marcado
                        ? 'border-accent/40 bg-accent/5'
                        : 'border-line hover:bg-raised'
                    } ${c.fixo ? 'cursor-default opacity-90' : ''}`}
                  >
                    <input
                      type="checkbox"
                      checked={marcado}
                      disabled={c.fixo}
                      onChange={() => !c.fixo && alternar(c.id)}
                      className="mt-0.5 h-4 w-4 shrink-0 accent-accent"
                    />
                    <span className="min-w-0 flex-1">
                      <span className="flex items-baseline justify-between gap-2">
                        <span className="text-[13.5px] font-semibold text-strong">
                          {c.nome}
                        </span>
                        <span className="shrink-0 font-mono text-[11px] text-muted">
                          {c.tamanho}
                        </span>
                      </span>
                      <span className="mt-0.5 block text-[12.5px] leading-[18px] text-muted">
                        {c.desc}
                      </span>
                      {c.fixo && (
                        <span className="mt-1 block text-[11px] text-muted/70">
                          obrigatório
                        </span>
                      )}
                    </span>
                  </label>
                );
              })}
            </div>
          </Etapa>
        )}

        {passo === 'pronto' && (
          <Etapa
            titulo="Tudo pronto"
            descricao={`Cole no ${COMANDOS[sistema].shell} e pressione Enter.`}
          >
            <div className="rounded-xl border border-line bg-base/80">
              <div className="flex items-center justify-between border-b border-line/60 px-3 py-1.5">
                <span className="font-mono text-[11px] text-muted">
                  {COMANDOS[sistema].shell}
                </span>
                <button
                  onClick={copiar}
                  className="rounded-md px-2 py-0.5 text-[11.5px] font-semibold text-accent transition-colors hover:bg-accent/10"
                >
                  {copiou ? 'copiado' : 'copiar'}
                </button>
              </div>
              <pre className="overflow-x-auto p-3 font-mono text-[12.5px] leading-[20px] text-strong">
                {comando}
              </pre>
            </div>

            <dl className="mt-4 space-y-1.5 text-[12.5px]">
              <Resumo termo="Sistema" valor={NOMES[sistema]} />
              <Resumo termo="Destino" valor={caminhoFinal} mono />
              <Resumo
                termo="Componentes"
                valor={COMPONENTES.filter((c) => c.fixo || marcados.has(c.id))
                  .map((c) => c.nome)
                  .join(', ')}
              />
              <Resumo termo="Espaço" valor={tamanhoTotal(marcados)} />
            </dl>

            <div className="mt-4 rounded-xl border border-line bg-raised/50 p-3">
              <p className="text-[12.5px] font-semibold text-strong">
                Depois de instalar
              </p>
              <p className="mt-1 text-[12.5px] leading-[19px] text-muted">
                Abra um terminal <strong className="text-strong">novo</strong> —
                o PATH só vale a partir daí — e confira com{' '}
                <code className="rounded bg-base px-1 py-0.5 font-mono text-[11.5px] text-strong">
                  dataforge --version
                </code>
                .
              </p>
            </div>
          </Etapa>
        )}
      </div>

      {/* navegação */}
      <div className="flex items-center justify-between gap-3 border-t border-line/70 bg-raised/30 px-4 py-3">
        <button
          onClick={() => indice > 0 && setPasso(PASSOS[indice - 1].id)}
          disabled={indice === 0}
          className="rounded-lg px-3 py-1.5 text-[13px] font-medium text-muted transition-colors hover:text-strong disabled:opacity-35"
        >
          Voltar
        </button>

        {passo === 'pronto' ? (
          <a
            href="/docs/primeiros-passos"
            className="rounded-lg bg-accent px-4 py-1.5 text-[13px] font-semibold text-white transition-colors hover:bg-accent-soft"
          >
            Primeiros passos →
          </a>
        ) : (
          <button
            onClick={() => podeAvancar && setPasso(PASSOS[indice + 1].id)}
            disabled={!podeAvancar}
            className="rounded-lg bg-accent px-4 py-1.5 text-[13px] font-semibold text-white transition-colors hover:bg-accent-soft disabled:cursor-not-allowed disabled:opacity-35"
          >
            {passo === 'licenca' && !aceitou ? 'Aceite para seguir' : 'Continuar'}
          </button>
        )}
      </div>
    </div>
  );
}

function Etapa({
  titulo,
  descricao,
  children,
}: {
  titulo: string;
  descricao: string;
  children: React.ReactNode;
}) {
  return (
    <div className="animate-fade-up">
      <h3 className="text-[17px] font-bold tracking-tight text-strong">
        {titulo}
      </h3>
      <p className="mb-4 mt-1 text-[13px] leading-[20px] text-muted">
        {descricao}
      </p>
      {children}
    </div>
  );
}

function Opcao({
  marcada,
  onClick,
  titulo,
  desc,
}: {
  marcada: boolean;
  onClick: () => void;
  titulo: string;
  desc: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex w-full items-start gap-2.5 rounded-xl border p-3 text-left transition-colors ${
        marcada ? 'border-accent bg-accent/6' : 'border-line hover:bg-raised'
      }`}
    >
      <span
        className={`mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2 ${
          marcada ? 'border-accent' : 'border-line'
        }`}
      >
        {marcada && <span className="h-1.5 w-1.5 rounded-full bg-accent" />}
      </span>
      <span className="min-w-0">
        <span className="block break-all font-mono text-[12.5px] text-strong">
          {titulo}
        </span>
        <span className="mt-0.5 block text-[12px] text-muted">{desc}</span>
      </span>
    </button>
  );
}

function Resumo({
  termo,
  valor,
  mono,
}: {
  termo: string;
  valor: string;
  mono?: boolean;
}) {
  return (
    <div className="flex gap-2">
      <dt className="w-[92px] shrink-0 text-muted">{termo}</dt>
      <dd className={`min-w-0 flex-1 text-strong ${mono ? 'break-all font-mono text-[12px]' : ''}`}>
        {valor}
      </dd>
    </div>
  );
}

function tamanhoTotal(marcados: Set<string>): string {
  const mb = COMPONENTES.filter(
    (c) => (c.fixo || marcados.has(c.id)) && c.tamanho !== '—',
  ).reduce((soma, c) => soma + parseFloat(c.tamanho.replace(',', '.')) *
    (c.tamanho.includes('KB') ? 0.001 : 1), 0);
  return `${mb.toFixed(1).replace('.', ',')} MB`;
}
