import Link from 'next/link';

/* Números reais do repositório — os mesmos que a suíte verifica.
 *
 * E ela passou a verificar de verdade: este comentário já estava aqui
 * quando os valores diziam 1246 e 216, e eram 2304 e 230. Um comentário
 * que promete uma trava que não existe é pior que nenhum — quem lê
 * confia e não confere.
 *
 * 'test_a_home_anuncia_os_numeros_reais' cobra os dois. */
const fatos = [
  { rotulo: 'Testes passando', valor: '2304' },
  { rotulo: 'Exercícios verificados', valor: '230' },
  { rotulo: 'Dependências no runtime', valor: 'nenhuma' },
];

export function Heroi() {
  return (
    <header>
      {/* A barra NAO mora aqui. Um 'position: sticky' so gruda dentro
          da caixa do pai: dentro deste <header> ela ia ate o fim do
          hero e sumia no resto da pagina. Ela e irma do hero, filha
          direta de '.lp' — e e por isso que o seletor
          '.lp > .lp-barra' do globals.css existe. */}
      <div className="px-4 pb-4 sm:px-10 sm:pb-10">
        <div className="lp-noise lp-hero-glow relative isolate overflow-hidden rounded-[28px] px-6 pb-14 pt-20 sm:rounded-[40px] sm:px-10 sm:pb-16 sm:pt-28 lg:pb-20 lg:pt-32">
        <div className="relative z-10 mx-auto max-w-[1280px]">
          <h1 className="lp-h1 mx-auto max-w-[15ch] text-center text-white">
            Mais que uma sintaxe diferente
          </h1>

          <p className="lp-mono mx-auto mt-8 max-w-[62ch] text-center text-[14px] leading-[24px] text-white/75 sm:text-[15px] sm:leading-[26px]">
            DataForge é uma linguagem interpretada de propósito geral, com lexer,
            parser, analisador estático e interpretador próprios — escritos em
            Python, sem uma única dependência externa em tempo de execução.
          </p>

          <div className="mt-12 flex flex-col items-center gap-6 lg:mt-20 lg:flex-row lg:items-end lg:justify-between">
            <div className="flex items-center gap-2 sm:gap-4">
              <Link href="/docs/primeiros-passos" className="lp-btn">
                Começar
              </Link>
              <Link href="/docs" className="lp-btn-ghost">
                Documentação
              </Link>
            </div>

            <dl className="lp-mono grid w-full gap-2 text-[13px] sm:w-auto">
              {fatos.map((f) => (
                <div key={f.rotulo} className="flex items-baseline justify-between gap-8 sm:justify-end">
                  <dt className="text-white/55">{f.rotulo}</dt>
                  <dd className="font-medium text-white sm:w-[10ch] sm:text-right">{f.valor}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
        </div>
      </div>
    </header>
  );
}
