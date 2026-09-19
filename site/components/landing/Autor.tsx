import Image from 'next/image';
import Link from 'next/link';
import dados from '@/lib/dados-gerados.json';
import { Rotulo, Sobe } from './Primitivos';

const AUTOR = {
  nome: 'Estevam Souza',
  papel: 'Autor da linguagem',
  // A foto é ARQUIVO DO REPOSITÓRIO, e não o endereço do LinkedIn.
  // Aquela URL é assinada e expira (`e=1838812800`): num dia qualquer
  // a página passaria a mostrar um buraco, sem nada explicando.
  foto: '/marca/estevam.jpg',
  github: 'https://github.com/estevam5s',
  linkedin: 'https://www.linkedin.com/in/estevam-souza',
  x: 'https://x.com/estevam5s',
  site: 'https://estevamsouza.com.br',
};

const contagem = (dados as unknown as {
  contagem: { testes: number; arquivosDf: number };
}).contagem;

const modulos = Object.keys(dados.modulos as Record<string, unknown>).length;
const simbolos = Object.values(
  dados.modulos as Record<string, { funcoes: unknown[] }>,
).reduce((n, m) => n + m.funcoes.length, 0);

/** O que uma pessoa só escreveu, em números que dá para conferir. */
const OBRA = [
  ['Lexer, parser e AST', 'tokens, INDENT/DEDENT, interpolação, 81 palavras'],
  ['Interpretador de árvore', 'e um compilador para fechamentos, 1,5× a 1,8×'],
  ['Analisador estático', 'nomes, aridade, tipos e membros — atravessando arquivos'],
  ['Dois frameworks web', 'Kiln (rotas, WebSocket, SSE) e Vitrine (dashboards)'],
  ['Gerenciador de pacotes', 'semver, lockfile, registro estático, integridade'],
  ['Servidor de linguagem e depurador', 'LSP e DAP, falados por stdio'],
];

export function Autor() {
  return (
    <section className="relative overflow-hidden px-4 py-24 sm:px-10 sm:py-32">
      <div
        className="lp-bleed right-[12%] top-[35%] h-[280px] w-[min(640px,80vw)]"
        aria-hidden
      />

      <div className="relative mx-auto max-w-[1280px]">
        <Sobe>
          <Rotulo texto="QUEM ESCREVEU" />
        </Sobe>

        <div className="mt-8 grid gap-12 lg:grid-cols-[auto_1fr] lg:gap-16">
          <div className="flex items-start gap-5 lg:block">
            <Image
              src={AUTOR.foto}
              alt={`Retrato de ${AUTOR.nome}`}
              width={168}
              height={168}
              className="h-[96px] w-[96px] shrink-0 rounded-2xl object-cover ring-1 ring-white/10 sm:h-[168px] sm:w-[168px]"
              priority={false}
            />
            <div className="lg:mt-6">
              <h2 className="text-[22px] font-semibold tracking-tight text-white sm:text-[26px]">
                {AUTOR.nome}
              </h2>
              <p className="lp-mono mt-2 text-[11.5px] tracking-[1.2px] text-white/40">
                {AUTOR.papel.toUpperCase()}
              </p>
            </div>
          </div>

          <div>
            <p className="lp-mono max-w-[62ch] text-[13.5px] leading-[25px] text-white/65">
              DataForge é obra de uma pessoa. São{' '}
              <span className="text-white">{contagem.arquivosDf}</span> arquivos{' '}
              <span className="text-white">.df</span>,{' '}
              <span className="text-white">{modulos}</span> módulos de biblioteca
              com <span className="text-white">{simbolos}</span> símbolos e{' '}
              <span className="text-white">{contagem.testes}</span> funções de
              teste — em Python, e sem uma única dependência em tempo de
              execução.
            </p>

            <dl className="mt-9 grid gap-px overflow-hidden rounded-2xl border border-[var(--lp-line)] bg-[var(--lp-line)] sm:grid-cols-2">
              {OBRA.map(([t, d]) => (
                <div key={t} className="bg-[var(--lp-bg)] px-5 py-5">
                  <dt className="text-[13.5px] font-semibold text-white">{t}</dt>
                  <dd className="lp-mono mt-2 text-[12px] leading-[20px] text-white/50">
                    {d}
                  </dd>
                </div>
              ))}
            </dl>

            <div className="mt-9 flex flex-wrap items-center gap-3">
              <a href={AUTOR.github} target="_blank" rel="noreferrer noopener" className="lp-btn-ghost">
                GitHub
              </a>
              <a href={AUTOR.linkedin} target="_blank" rel="noreferrer noopener" className="lp-btn-ghost">
                LinkedIn
              </a>
              <a href={AUTOR.x} target="_blank" rel="noreferrer noopener" className="lp-btn-ghost">
                X
              </a>
              <a href={AUTOR.site} target="_blank" rel="noreferrer noopener" className="lp-btn-ghost">
                estevamsouza.com.br
              </a>
            </div>

            <p className="lp-mono mt-8 text-[11.5px] leading-[20px] text-white/30">
              Licença MIT. O{' '}
              <Link href="/docs/contribuir" className="text-white/50 underline-offset-2 hover:underline">
                guia de contribuição
              </Link>{' '}
              diz em quais dos cinco lugares cada recurso da linguagem encosta.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
