import Link from 'next/link';
import { Rotulo, Sobe } from './Primitivos';

/** O identificador da extensão na loja do VS Code.
 *
 * `EstevamSouza`, e não `dataforge`: é o publisher que a conta da loja
 * realmente tem. E o nome de exibição é "DataForge Language" porque
 * "DataForge" já pertence a uma extensão alheia — a loja recusa o
 * nome, não o identificador.
 */
const EXTENSAO =
  'https://marketplace.visualstudio.com/items?itemName=EstevamSouza.dataforge-language';

const AUTOR = {
  nome: 'Estevam Souza',
  papel: 'Autor da linguagem',
  github: 'https://github.com/estevam5s',
  x: 'https://x.com/estevam5s',
  site: 'https://estevamsouza.com.br',
};

/** Editores que instalam do mesmo `.vsix`. */
const EDITORES = ['VS Code', 'VSCodium', 'Cursor', 'Windsurf'];

export function Autor() {
  return (
    <section className="relative overflow-hidden px-4 py-28 sm:px-10 sm:py-36">
      <div
        className="lp-bleed left-1/2 top-[40%] h-[280px] w-[min(820px,88vw)] -translate-x-1/2"
        aria-hidden
      />

      <div className="relative mx-auto max-w-[1280px]">
        <div className="grid gap-px overflow-hidden rounded-3xl border border-[var(--lp-line)] bg-[var(--lp-line)] lg:grid-cols-2">
          {/* ── A extensão ── */}
          <div className="bg-[var(--lp-bg)] px-6 py-12 sm:px-10 sm:py-14">
            <Sobe>
              <Rotulo texto="NO SEU EDITOR" />
            </Sobe>

            <h2 className="lp-h2 mt-6 max-w-[18ch] font-medium">
              A extensão está na loja
            </h2>

            <p className="lp-mono mt-6 max-w-[52ch] text-[13.5px] leading-[25px] text-white/65">
              Cores, <span className="text-white">snippets</span>, erros sublinhados ao
              salvar, servidor de linguagem próprio, depurador com{' '}
              <span className="text-white">F5</span>, e o Big-O acima de cada ação. A
              gramática é <span className="text-white">gerada</span> de{' '}
              <span className="text-white">tokens.py</span> — ela não pode ficar atrás
              da linguagem.
            </p>

            <div className="mt-9 flex flex-wrap items-center gap-3">
              <a
                href={EXTENSAO}
                target="_blank"
                rel="noreferrer noopener"
                className="lp-btn"
              >
                Instalar no VS Code
              </a>
              <Link href="/docs/editor" className="lp-btn-ghost">
                O que ela faz
              </Link>
            </div>

            <div className="lp-mono mt-9 flex flex-wrap items-center gap-x-3 gap-y-2 text-[11.5px] text-white/35">
              {EDITORES.map((e) => (
                <span key={e} className="rounded-full border border-[var(--lp-line)] px-2.5 py-1">
                  {e}
                </span>
              ))}
            </div>

            <p className="lp-mono mt-6 text-[11.5px] leading-[20px] text-white/30">
              Sem editor à mão? <span className="text-white/50">dataforge editor</span>{' '}
              instala a mesma extensão do pacote, sem internet.
            </p>
          </div>

          {/* ── Quem escreveu ── */}
          <div className="bg-[var(--lp-bg)] px-6 py-12 sm:px-10 sm:py-14">
            <Sobe>
              <Rotulo texto="QUEM ESCREVEU" />
            </Sobe>

            <h2 className="lp-h2 mt-6 max-w-[16ch] font-medium">{AUTOR.nome}</h2>

            <p className="lp-mono mt-3 text-[12px] tracking-[1.2px] text-white/40">
              {AUTOR.papel.toUpperCase()}
            </p>

            <p className="lp-mono mt-6 max-w-[52ch] text-[13.5px] leading-[25px] text-white/65">
              DataForge é obra de uma pessoa: lexer, parser, analisador estático,
              interpretador, dois frameworks web, o gerenciador de pacotes, o servidor
              de linguagem, o depurador e a documentação. Em Python, e{' '}
              <span className="text-white">sem dependência de runtime</span>.
            </p>

            <div className="mt-9 flex flex-wrap items-center gap-3">
              <a
                href={AUTOR.github}
                target="_blank"
                rel="noreferrer noopener"
                className="lp-btn-ghost"
              >
                GitHub
              </a>
              <a
                href={AUTOR.x}
                target="_blank"
                rel="noreferrer noopener"
                className="lp-btn-ghost"
              >
                X
              </a>
              <a
                href={AUTOR.site}
                target="_blank"
                rel="noreferrer noopener"
                className="lp-btn-ghost"
              >
                estevamsouza.com.br
              </a>
            </div>

            <p className="lp-mono mt-9 text-[11.5px] leading-[20px] text-white/30">
              Licença MIT. Contribuições pelo repositório — e o{' '}
              <Link href="/docs/contribuir" className="text-white/50 underline-offset-2 hover:underline">
                guia de contribuição
              </Link>{' '}
              diz onde cada recurso encosta na linguagem.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
