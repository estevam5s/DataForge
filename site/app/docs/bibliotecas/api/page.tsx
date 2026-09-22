// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Desenhar a API pública",
  description: "Sete decisões de assinatura — e a que decide se alguém consegue usar a sua biblioteca sem abrir o código.",
};

const blocos: Bloco[] = [
  {"p": "A API é o que a pessoa lê. Tudo o mais — a implementação, os testes, a documentação — existe para sustentá-la, e nenhum deles a conserta depois de publicada."},
  {"h2": "O nome diz o que devolve"},
  {"table": {"head": ["Nome", "O que ele promete", "Devolve"], "rows": [["`buscar`", "procura, pode não achar", "o valor ou `void`"], ["`exigir`", "procura, e **falha** se não achar", "o valor, sempre"], ["`tem`", "uma pergunta", "`yes`/`no`"], ["`de`", "constrói a partir de", "o objeto novo"], ["`para`", "converte para", "a outra forma"], ["`com`", "uma cópia mudada", "objeto **novo**"], ["`definir`", "muda no lugar", "nada útil"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Um par que devolve coisas diferentes tem de ter nomes diferentes", "texto": "`remove` e `pop` fazem quase a mesma coisa nas coleções da linguagem, e os nomes separam o que importa: `remove` apaga **no lugar** e é silencioso quando não acha; `pop` devolve o valor e por isso **levanta**. Devolver `void` calado esconderia a diferença entre *“a chave valia `void`”* e *“a chave não estava lá”* — e `omit` devolve **cópia** sem mexer no original. Três verbos, três promessas."}},
  {"h2": "Posicional até três; depois, opções"},
  { code: `// Tres posicionais ainda se leem.
//   Tabela.montar(linhas, colunas, titulo)
//
// Cinco nao:
//   Tabela.montar(linhas, colunas, titulo, yes, no, 3, "—")
//                                          ?    ?  ?   ?
//
// A partir dai, o que varia vira um vault de opcoes.

action montar(linhas, colunas, opcoes := {}):
    o := {"titulo": "", "totais": no, "largura": 0, "vazio": "—"}
    cycle chave in opcoes.keys():
        given chave not in o:
            trigger $"'{chave}' nao e uma opcao de montar"
        o[chave] := opcoes[chave]
    yield $"{len(linhas)}x{len(colunas)}, vazio='{o['vazio']}'"

out montar([1, 2], ["a"], {"vazio": "-"})
assert montar([1], ["a"]) is "1x1, vazio='—'"`, lang: 'df' },
  {"h2": "Aceitar as três formas de “um campo”"},
  {"p": "Uma função que recebe *“o campo pelo qual ordenar”* precisa funcionar com **vault, record e instância**. Este foi um bug real da própria biblioteca: `sort_by_field` devolvia `void` para todos os records, calada."},
  { code: `adopt Arcane.Reflexo as R

action campo_de(item, nome):
    given typeof(item) is "Vault":
        yield item[nome] ?? void
    yield R.ler(item, nome)

record Pessoa:
    nome: String
    idade: Integer

assert campo_de({"idade": 30}, "idade") is 30
assert campo_de(Pessoa("Ana", 41), "idade") is 41`, lang: 'df' },
  {"h2": "O que nunca entra numa assinatura pública"},
  {"table": {"head": ["Não", "Porque"], "rows": [["um booleano sem nome", "`montar(l, c, yes, no)` é ilegível na chamada; vire opção"], ["um índice mágico (`-1` = todos)", "o dia em que `-1` for legítimo não tem saída"], ["um tipo do Python vazando", "`list` e `dict` não existem nesta linguagem"], ["ordem de argumentos que muda", "é a quebra mais barata de cometer e a mais cara de achar"], ["um parâmetro que só faz sentido junto de outro", "dois parâmetros com uma regra entre eles são um objeto"]]}},
  {"p": "Continue em [O vault de opções](/docs/bibliotecas/opcoes) e [Os erros da sua biblioteca](/docs/bibliotecas/erros)."},
];

const headings = [{ id: 'o-nome-diz-o-que-devolve', text: "O nome diz o que devolve", level: 2 as const }, { id: 'posicional-ate-tres-depois-opcoes', text: "Posicional até três; depois, opções", level: 2 as const }, { id: 'aceitar-as-tres-formas-de-um-campo', text: "Aceitar as três formas de “um campo”", level: 2 as const }, { id: 'o-que-nunca-entra-numa-assinatura-publica', text: "O que nunca entra numa assinatura pública", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Desenhar a API pública"}
      description={"Sete decisões de assinatura — e a que decide se alguém consegue usar a sua biblioteca sem abrir o código."}
      href={"/docs/bibliotecas/api"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
