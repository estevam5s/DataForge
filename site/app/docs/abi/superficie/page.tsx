// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_e_alvos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A superfície é o contrato",
  description: "O que um módulo exporta, com que aridade e com que tipos — e por que mudá-la é o mesmo problema que quebrar uma ABI.",
};

const blocos: Bloco[] = [
  {"p": "Numa linguagem compilada, quebrar a **ABI** é trocar o layout de uma struct ou a convenção de chamada. O sintoma é cruel: o programa **carrega** e corrompe memória, longe da causa e sem nada denunciar."},
  {"p": "Aqui não há layout binário a quebrar. E existe **exatamente o mesmo problema**, com outro nome."},
  {"table": {"head": ["Na linguagem compilada", "Aqui"], "rows": [["símbolo removido do `.so`", "símbolo tirado do `relay`"], ["assinatura trocada", "aridade, nome ou tipo de parâmetro trocado"], ["layout de struct mudado", "campo acrescentado a um `record`"], ["tipo de retorno trocado", "o mesmo — e ele **atravessa** o `adopt`"], ["`soname` bump", "versão **maior** no `forge.toml`"]]}},
  {"callout": {"tipo": "atencao", "titulo": "O sintoma também é o mesmo", "texto": "**Não é um erro de compilação de quem publicou.** O módulo novo compila perfeitamente, os testes dele passam, o pacote sobe. O erro acontece na máquina de **quem consome**, depois, no dia da atualização — e a pessoa que vai depurar não é a que causou."}},
  {"h2": "O que é contrato, e o que não é"},
  {"p": "A superfície respeita o `relay`. Um módulo que **declara** o que exporta está dizendo que o resto é interno — e o que é interno não é contrato, então mexer nele não quebra ninguém."},
  { code: `action somar(a: Integer, b: Integer) -> Integer:
    yield a + b

action interna():          // nao esta no relay: nao e contrato
    yield 1

record Ponto:
    x: Integer
    y: Integer

relay somar, Ponto`, lang: 'df', title: `lib.df — o relay decide` },
  {"p": "Sem `relay`, tudo o que é de topo é contrato — o que é a escolha certa para um arquivo que não declarou nada, e um bom motivo para declarar."},
  {"h2": "A superfície, como dado"},
  { code: `adopt Arcane.Abi as Abi

// Abi.superficie("lib.df") devolve, por simbolo:
//   especie      acao, record, blueprint, enum, trait, valor
//   minimo       quantos argumentos ele EXIGE
//   maximo       quantos ele ACEITA (void = variadico)
//   parametros   os nomes, na ordem — e eles sao contrato
//   tipos        o tipo declarado de cada um
//   retorno      o tipo de retorno, que atravessa o adopt
//   campos       de um record ou blueprint
//   linha        onde ele foi declarado

assert len(keys(Abi.regras())) bigger_eq 7`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "A conta sai de `superficie.py`", "texto": "O mesmo módulo que o `check` usa para [atravessar arquivos](/docs/tecnicas/analise-estatica). Uma segunda leitura da superfície divergiria da primeira — e aí o `check` e o `abi` passariam a discordar sobre o que um módulo oferece, que é o pior resultado possível para duas ferramentas que respondem a mesma pergunta."}},
];

const headings = [{ id: 'o-que-e-contrato-e-o-que-nao-e', text: "O que é contrato, e o que não é", level: 2 as const }, { id: 'a-superficie-como-dado', text: "A superfície, como dado", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A superfície é o contrato"}
      description={"O que um módulo exporta, com que aridade e com que tipos — e por que mudá-la é o mesmo problema que quebrar uma ABI."}
      href={"/docs/abi/superficie"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
