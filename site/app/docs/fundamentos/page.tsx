// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fundamentos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Fundamentos",
  description: "O que vem depois dos primeiros passos: tipos, coleções, padrões, ações de ordem superior, recursão e o sistema de tipos — o mapa da seção.",
};

const blocos: Bloco[] = [
  {"p": "Os [primeiros passos](/docs/primeiros-passos) ensinam a escrever um programa. Os fundamentos ensinam a escrever **o programa certo**: qual coleção escolher, quando um valor pode mudar, o que `is` compara, onde mora a ausência, como uma ação recebe outra."},
  {"p": "Não há ordem obrigatória. Cada página se sustenta sozinha, e todo bloco de código roda — foi conferido executando."},
  {"h2": "A linguagem por dentro"},
  {"cards": [{"href": "/docs/fundamentos/anotacoes-de-tipo", "title": "Anotações de tipo", "desc": "Tipos opcionais em variáveis, parâmetros e retorno — verificados em execução e por análise estática."}, {"href": "/docs/fundamentos/records", "title": "Records", "desc": "Dados imutáveis com igualdade estrutural, valores padrão, métodos e o operador with."}, {"href": "/docs/fundamentos/enums", "title": "Enums", "desc": "Conjuntos fechados de valores nomeados, com valores associados e integração com match."}, {"href": "/docs/fundamentos/pattern-matching", "title": "Pattern matching", "desc": "match estrutural: literais, tipos, sequências, records, vaults, enums, alternativas e guardas."}, {"href": "/docs/fundamentos/desestruturacao", "title": "Desestruturação", "desc": "Extrair vários valores de uma vez, por posição ou por nome."}, {"href": "/docs/fundamentos/spread", "title": "Spread e rest", "desc": "O operador ... expandindo coleções e coletando o que sobra."}, {"href": "/docs/fundamentos/compreensoes", "title": "Compreensões", "desc": "Construir listas e vaults numa expressão, transformando e filtrando."}, {"href": "/docs/fundamentos/interpolacao", "title": "Interpolação", "desc": "Strings com $ que embutem expressões, e como formatar saída legível."}, {"href": "/docs/fundamentos/generators", "title": "Generators", "desc": "stream action e emit: sequências produzidas sob demanda, inclusive infinitas."}, {"href": "/docs/fundamentos/closures", "title": "Closures e lambdas", "desc": "Ações como valores: alta ordem, closures, lambdas e composição."}, {"href": "/docs/fundamentos/decoradores", "title": "Decoradores", "desc": "mark @nome — envolver uma ação sem alterar seu corpo."}, {"href": "/docs/fundamentos/decoradores-avancados", "title": "Decoradores avançados", "desc": "Embrulhar e anotar — e o que os metadados permitem construir."}, {"href": "/docs/fundamentos/traits", "title": "Traits", "desc": "Contratos de interface compostos com with."}, {"href": "/docs/fundamentos/generics", "title": "Generics", "desc": "Uma estrutura que serve para qualquer tipo."}, {"href": "/docs/fundamentos/escopo", "title": "Escopo", "desc": "Como os nomes são resolvidos, e o que shadow faz."}, {"href": "/docs/fundamentos/modulos", "title": "Módulos", "desc": "adopt, relay, imports seletivos e detecção de ciclos."}]},
  {"h2": "Valores, coleções e ações"},
  {"p": "Conjuntos, números exatos, ausência, conversões, igualdade, imutabilidade, texto, ordem superior e recursão — com as armadilhas que cada um esconde."},
  {"cards": [{"href": "/docs/fundamentos/conjuntos", "title": "Conjuntos", "desc": "O tipo Set: o literal {1, 2}, set(xs), a compreensão, as operações — e por que um Cluster não entra nele."}, {"href": "/docs/fundamentos/numeros", "title": "Números", "desc": "Integer, Float e Decimal — a divisão, o arredondamento, e o 0,1 + 0,2."}, {"href": "/docs/fundamentos/ausencia", "title": "Verdade e ausência", "desc": "void, o que é verdadeiro, ?? e ?. — e por que 'não sei' não é zero."}, {"href": "/docs/fundamentos/conversoes", "title": "Conversões", "desc": "int, float, str, cast e typeof — e o que acontece quando o valor não converte."}, {"href": "/docs/fundamentos/igualdade", "title": "Igualdade e comparação", "desc": "is compara pelo valor, por estrutura — e as três formas de comparar coleções e objetos."}, {"href": "/docs/fundamentos/imutabilidade", "title": "Imutabilidade", "desc": "steady, record, freeze e tupla — o que muda, o que não muda, e por que isso importa."}, {"href": "/docs/fundamentos/textos-avancados", "title": "Texto a fundo", "desc": "Fatiar, procurar, trocar, dividir, juntar e formatar — e o texto de várias linhas."}, {"href": "/docs/fundamentos/ordem-superior", "title": "Ações como valores", "desc": "Passar uma ação para outra, devolver uma ação, lambda — e o pipeline como a forma idiomática."}, {"href": "/docs/fundamentos/recursao", "title": "Recursão", "desc": "Uma ação que chama a si mesma, o caso base, o teto de mil quadros — e as duas saídas."}]},
  {"h2": "O sistema de tipos"},
  {"cards": [{"href": "/docs/tipos/visao-geral", "title": "Sistema de tipos: visão geral", "desc": "O mapa: tipos internos, anotações, coleções tipadas, tipos nomeados, generics, indexados, opacos e traits — e o que cada camada garante."}, {"href": "/docs/tipos-nomeados", "title": "Tipos nomeados", "desc": "type e opaque type: alias, união, interseção, refinamento e tipo opaco — o que cada um promete, quem confere e quando o analisador cala."}, {"href": "/docs/tipos/tuplas", "title": "Tuplas", "desc": "(1, \\"}, {"href": "/docs/tipos/resultado", "title": "Resultado e Talvez", "desc": "A falha como valor: ok/falha com mapear, entao e recuperar; e Talvez para onde void é ambíguo — as três formas de lidar com o que dá errado."}, {"href": "/docs/tipos/reflexao", "title": "Reflexão de tipos", "desc": "Arcane.Tipos: os metadados de um type declarado, conferir sem levantar, a forma estrutural de um valor e os campos de um record com o tipo de cada um."}, {"href": "/docs/tipos/mapa", "title": "Fundamentos e tipos: o mapa", "desc": "Item por item das partes 1 e 2 da referência Deep Tech, cruzado com o DataForge: o que existe e onde está, o que tem outro nome, e o que não existe por decisão."}, {"href": "/docs/tipos/genericos", "title": "Generics: o sistema de tipos", "desc": "<T> e <T extends X> em ação, blueprint, record, enum e trait: o que o parâmetro documenta, o que o limite cobra, e onde o argumento chega ao conteúdo."}, {"href": "/docs/tipos/traits", "title": "Sistema de traits", "desc": "Traits com implementação padrão, herança entre traits, tipos e constantes associados, interseção, despacho dinâmico e o que a linguagem cobra de quem implementa."}]},
];

const headings = [{ id: 'a-linguagem-por-dentro', text: "A linguagem por dentro", level: 2 as const }, { id: 'valores-colecoes-e-acoes', text: "Valores, coleções e ações", level: 2 as const }, { id: 'o-sistema-de-tipos', text: "O sistema de tipos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Fundamentos"}
      description={"O que vem depois dos primeiros passos: tipos, coleções, padrões, ações de ordem superior, recursão e o sistema de tipos — o mapa da seção."}
      href={"/docs/fundamentos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
