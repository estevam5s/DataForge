'use client';

import { Contagem } from './Contagem';
import { Rotulo, Sobe } from './Primitivos';
import { dataCurta, useMundo } from '@/lib/numeros';

const REPO = 'https://github.com/estevam5s/DataForge';
const EXTENSAO =
  'https://marketplace.visualstudio.com/items?itemName=EstevamSouza.dataforge-language';

/**
 * Os números que vivem fora do repositório.
 *
 * Eles chegam em duas etapas — instantâneo do build primeiro, valor de
 * verdade quando o navegador responde — e por isso a caixa não pode
 * mudar de tamanho quando o segundo chega. A `Contagem` reserva a
 * largura do valor final; aqui cada linha tem altura fixa.
 *
 * Nada aqui é enfeite: são os únicos números da página que quem lê não
 * pode conferir sozinho abrindo o repositório.
 */
export function Numeros() {
  const mundo = useMundo();

  return (
    <section className="relative overflow-hidden px-4 py-24 sm:px-10 sm:py-32">
      <div
        className="lp-bleed left-1/2 top-1/2 h-[260px] w-[min(760px,88vw)] -translate-x-1/2 -translate-y-1/2"
        aria-hidden
      />

      <div className="relative mx-auto max-w-[1280px]">
        <div className="grid items-center gap-12 lg:grid-cols-[1fr_auto]">
          <div>
            <Sobe>
              <Rotulo texto="NO AR" />
            </Sobe>
            <h2 className="lp-h2 mt-6 max-w-[20ch] font-medium">
              Em uso, e contado
            </h2>
            <p className="lp-mono mt-6 max-w-[54ch] text-[13.5px] leading-[25px] text-white/60">
              Os quatro números vêm da API do GitHub e da loja do VS Code, lidos
              pelo seu navegador agora. Quando a busca não volta — o GitHub
              limita a 60 pedidos por hora —, fica o valor do último deploy, que
              é verdadeiro e algumas horas mais velho.
            </p>
          </div>

          <dl className="lp-mono grid gap-3 text-[13.5px] lg:min-w-[380px]">
            <Linha rotulo="Estrelas no GitHub" href={REPO}>
              <Contagem valor={mundo.estrelas} />
            </Linha>

            <Linha rotulo="Última versão" href={`${REPO}/releases/latest`}>
              <span className="tabular-nums">
                {dataCurta(mundo.publicado)} / {mundo.versao ?? '—'}
              </span>
            </Linha>

            <Linha rotulo="Downloads do release" href={`${REPO}/releases`}>
              <Contagem valor={mundo.baixados} />
            </Linha>

            <Linha rotulo="Instalações da extensão" href={EXTENSAO}>
              <Contagem valor={mundo.instalacoes} />
            </Linha>
          </dl>
        </div>
      </div>
    </section>
  );
}

function Linha({
  rotulo,
  href,
  children,
}: {
  rotulo: string;
  href: string;
  children: React.ReactNode;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer noopener"
      className="group flex h-[46px] items-center justify-between gap-8 rounded-xl border border-[var(--lp-line)] px-4 transition-colors hover:border-white/25"
    >
      <dt className="text-white/55 transition-colors group-hover:text-white/75">
        {rotulo}
      </dt>
      <dd className="font-medium text-white">{children}</dd>
    </a>
  );
}
