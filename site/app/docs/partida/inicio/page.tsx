// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_e_seguranca.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Antes da primeira linha",
  description: "As sete fases que rodam antes da sua primeira instrução — e quanto cada adopt custou na partida.",
};

const blocos: Bloco[] = [
  {"p": "Um programa não começa na primeira linha. Antes dela o [`comptime`](/docs/metaprogramacao/comptime) rodou numa caixa sem E/S, os `adopt` carregaram módulos e as declarações de topo foram içadas."},
  {"p": "Nada disso era **visível** — e \"por que a partida demora 400 ms?\" não tinha como ser respondido sem cronometrar à mão."},
  { code: `adopt Arcane.Inicio as I

fases := I.fases()
assert [f["fase"] cycle f in fases] is
       ["lexer", "parser", "comptime", "hoisting", "adopt", "programa", "defer"]`, lang: 'df' },
  {"table": {"head": ["Fase", "O que acontece"], "rows": [["`lexer`", "o texto vira tokens, com linha e coluna em cada um"], ["`parser`", "os tokens viram a árvore; um erro de sintaxe para aqui"], ["`comptime`", "os blocos rodam numa **caixa sem E/S**, e o que decidem vira constante antes de o programa existir"], ["`hoisting`", "as declarações de topo são içadas: uma ação pode ser chamada antes da linha em que foi escrita"], ["`adopt`", "cada módulo é resolvido e carregado, na ordem do arquivo — **é aqui que a partida costuma ser gasta**"], ["`programa`", "a primeira instrução de topo finalmente roda"], ["`defer`", "os `defer` de topo rodam no fim, na ordem inversa"]]}},
  {"h2": "Onde a partida foi gasta"},
  { code: `adopt Arcane.Inicio as I
adopt Arcane.Math as M

// cada adopt e cronometrado — e a pergunta aparece quando alguem
// NAO desconfiava, entao a medida e sempre ligada
assert len(I.adocoes()) bigger_eq 2
assert I.relatorio()["adocoes"] bigger_eq 2
assert "mais_caro" in I.relatorio()`, lang: 'df' },
  { code: `  4 modulo(s) carregado(s) em 38.42 ms

   Arcane.Cortex                  24.108 ms   62.7%
   Arcane.Database                 9.902 ms   25.8%
   Arcane.Math                     2.914 ms    7.6%
   Arcane.Text                     1.496 ms    3.9%`, lang: 'text', title: `I.texto_do_relatorio()` },
  {"callout": {"tipo": "nota", "titulo": "Por que a medida é sempre ligada", "texto": "São dois floats por import, num lugar que roda **uma vez**. Ligá-la por opção faria a medida existir só para quem já desconfiava — e a pergunta \"por que demora a começar?\" aparece justamente quando ninguém desconfiava."}},
  {"h2": "Globais, e a ordem"},
  {"p": "`steady` declara constante; a ordem de inicialização é a do **arquivo**, e os `adopt` acontecem onde estão escritos. O [ciclo de import é erro do `check`](/docs/modulos/carga), e não estouro em execução — a busca é em largura, para achar o ciclo mais curto."},
  {"p": "E a destruição existe: um `defer` no nível de topo roda no **fim do programa**, na ordem inversa. É como se fecha um arquivo ou uma conexão sem depender de ninguém lembrar."},
];

const headings = [{ id: 'onde-a-partida-foi-gasta', text: "Onde a partida foi gasta", level: 2 as const }, { id: 'globais-e-a-ordem', text: "Globais, e a ordem", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Antes da primeira linha"}
      description={"As sete fases que rodam antes da sua primeira instrução — e quanto cada adopt custou na partida."}
      href={"/docs/partida/inicio"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
