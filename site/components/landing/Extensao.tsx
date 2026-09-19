'use client';

import Link from 'next/link';
import { Contagem } from './Contagem';
import { Rotulo, Sobe } from './Primitivos';
import { useMundo } from '@/lib/numeros';

/**
 * O identificador na loja.
 *
 * `EstevamSouza`, e não `dataforge`: é o publisher que a conta tem. E
 * o nome de exibição é "DataForge Language" porque "DataForge" já
 * pertence a uma extensão alheia — a loja recusa o rótulo, não o
 * identificador.
 */
const ID = 'EstevamSouza.dataforge-language';
const LOJA = `https://marketplace.visualstudio.com/items?itemName=${ID}`;

/** Editores que instalam do mesmo `.vsix`. */
const EDITORES = ['VS Code', 'VSCodium', 'Cursor', 'Windsurf', 'VS Code Insiders'];

const RECURSOS = [
  {
    t: 'Cores que não envelhecem',
    d: 'A gramática é gerada de tokens.py. Uma palavra nova na linguagem aparece colorida na próxima geração — e o gerador recusa rodar se alguma ficar de fora.',
  },
  {
    t: 'Erros sublinhados ao salvar',
    d: 'O mesmo analisador do dataforge check, servido por um LSP próprio: nome errado, aridade errada, tipo errado, membro que não existe — com sugestão.',
  },
  {
    t: 'Depurador com F5',
    d: 'Breakpoint na margem, pilha, variáveis em árvore e avaliação no quadro escolhido. O adaptador fala o DAP, o mesmo protocolo do resto do editor.',
  },
  {
    t: 'Big-O acima de cada ação',
    d: 'A complexidade estimada aparece como anotação sobre a declaração, e o custo do import ao lado de cada adopt.',
  },
  {
    t: '52 comandos',
    d: 'Rodar com cronômetro, testar, cobertura, formatar, pacotes, Vitrine, DevOps e um painel dos bancos SQLite do projeto.',
  },
  {
    t: 'Ícone dos .df',
    d: 'Um tema de ícone de arquivo próprio, para o explorador distinguir os arquivos da linguagem.',
  },
];

export function Extensao() {
  const mundo = useMundo();

  return (
    <section className="relative overflow-hidden px-4 py-24 sm:px-10 sm:py-32">
      <div
        className="lp-bleed left-[18%] top-[30%] h-[300px] w-[min(700px,80vw)]"
        aria-hidden
      />

      <div className="relative mx-auto max-w-[1280px]">
        <Sobe>
          <Rotulo texto="NO SEU EDITOR" />
        </Sobe>

        <div className="mt-6 flex flex-wrap items-end justify-between gap-6">
          <h2 className="lp-h2 max-w-[20ch] font-medium">
            A extensão está na loja
          </h2>

          <div className="lp-mono flex items-center gap-6 text-[12.5px] text-white/45">
            <span>
              <Contagem valor={mundo.instalacoes} className="text-white" />{' '}
              instalações
            </span>
            <span className="hidden sm:inline">v1.0.0</span>
          </div>
        </div>

        <p className="lp-mono mt-6 max-w-[64ch] text-[13.5px] leading-[25px] text-white/60">
          Identificador <span className="text-white">{ID}</span>. Instala em
          qualquer editor baseado no VS Code, e quem já tem a linguagem no
          terminal pode instalá-la sem internet com{' '}
          <span className="text-white">dataforge editor</span> — é a mesma
          extensão, empacotada dentro do executável.
        </p>

        <div className="mt-9 flex flex-wrap items-center gap-3">
          <a href={LOJA} target="_blank" rel="noreferrer noopener" className="lp-btn">
            Instalar no VS Code
          </a>
          <Link href="/docs/editor" className="lp-btn-ghost">
            O que ela faz
          </Link>
        </div>

        <div className="lp-mono mt-8 flex flex-wrap items-center gap-2 text-[11.5px] text-white/35">
          {EDITORES.map((e) => (
            <span
              key={e}
              className="rounded-full border border-[var(--lp-line)] px-2.5 py-1"
            >
              {e}
            </span>
          ))}
        </div>

        <div className="mt-14 grid gap-px overflow-hidden rounded-2xl border border-[var(--lp-line)] bg-[var(--lp-line)] sm:grid-cols-2 lg:grid-cols-3">
          {RECURSOS.map((r) => (
            <div key={r.t} className="bg-[var(--lp-bg)] px-6 py-7">
              <h3 className="text-[14.5px] font-semibold text-white">{r.t}</h3>
              <p className="lp-mono mt-3 text-[12.5px] leading-[21px] text-white/55">
                {r.d}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-10 rounded-2xl border border-[var(--lp-line)] px-6 py-5">
          <p className="lp-mono text-[12.5px] leading-[21px] text-white/45">
            <span className="text-white/70">Pela linha de comando:</span>{' '}
            <code className="text-white">code --install-extension {ID}</code>
          </p>
        </div>
      </div>
    </section>
  );
}
