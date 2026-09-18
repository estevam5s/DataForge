// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/tipos_tuplas.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O sistema de tipos",
  description: "O mapa: tipos internos, anotações, coleções tipadas, tipos nomeados, generics, indexados, opacos e traits — e o que cada camada garante.",
};

const blocos: Bloco[] = [
  {"p": "O DataForge é de tipagem **dinâmica com anotação verificada**: você escreve o tipo onde ele importa, e a linguagem cobra em duas horas diferentes — o `dataforge check` antes de rodar, quando consegue **provar**, e o interpretador na fronteira, sempre."},
  {"h2": "As camadas"},
  {"table": {"head": ["Camada", "Escreve-se", "Quem confere", "Página"], "rows": [["tipos internos", "`Integer`, `String`, `Cluster`, `Vault`, `Set`, `Tuple`, `Frozen`, `Bytes`, `Any`", "execução, na anotação", "[Tipos](/docs/tipos)"], ["anotação", "`x: Integer := 3`, `-> Float`", "as duas", "[Anotações](/docs/fundamentos/anotacoes-de-tipo)"], ["conteúdo de coleção", "`Cluster<Integer>`, `Vault<String, Pedido>`, `Set<T>`", "fronteira, inserção e `check`", "[Anotações](/docs/fundamentos/anotacoes-de-tipo)"], ["tupla", "`Tuple<Integer, String>`", "posição e tamanho", "[Tuplas](/docs/tipos/tuplas)"], ["alias, união, interseção", "`type Json := String \\| Integer`", "as duas", "[Tipos nomeados](/docs/tipos-nomeados)"], ["refinamento", "`type Positivo := Integer where valor bigger 0`", "toda fronteira, e `check` sobre literal", "[Tipos nomeados](/docs/tipos-nomeados)"], ["opaco", "`opaque type Cpf := String where …`", "nominal: só o construtor cria", "[Tipos nomeados](/docs/tipos-nomeados)"], ["generics", "`<T>`, `<T extends Number>`", "limite nas duas metades", "[Generics](/docs/tipos/genericos)"], ["indexado", "`Vetor<3>`", "a regra vê o número", "[Generics](/docs/tipos/genericos)"], ["traits", "`trait`, `extends`, `type Item`, `&`", "declaração e execução", "[Traits](/docs/tipos/traits)"]]}},
  {"h2": "Um exemplo com todas elas"},
  { code: `type Id := Integer
type Email := String where "@" in valor
type Vetor<N> := Cluster<Float> where len(valor) is N
opaque type Cpf := String where len(valor) is 11

trait Auditavel:
    action resumo() -> String

record Cliente<T extends Number>:
    id: Id
    email: Email
    documento: Cpf
    saldo: T
    coordenada: Tuple<Float, Float>

blueprint Carteira extends Auditavel:
    clientes: Cluster<Cliente> := []

    action guardar(c: Cliente):
        self.clientes.append(c)
        yield self

    action resumo() -> String:
        yield $"{len(self.clientes)} cliente(s)"

action distancia(a: Vetor<2>, b: Vetor<2>) -> Float:
    yield ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

c := Cliente(1, "ana@exemplo.com", Cpf("12345678901"), 250.0, (1.0, 2.0))
carteira := spawn Carteira()
carteira.guardar(c)

assert carteira.resumo() is "1 cliente(s)"
assert c.documento.valor is "12345678901"
assert distancia([0.0, 0.0], [3.0, 4.0]) is 5.0`, lang: 'df' },
  {"h2": "Quando cada uma acusa"},
  {"p": "A regra é uma só: **o analisador cala quando não consegue provar**. Um falso alarme ensina a desligar a verificação, e aí ela deixa de valer para tudo."},
  {"table": {"head": ["Situação", "`check`", "Execução"], "rows": [["`x: Integer := \"a\"`", "acusa (`type-mismatch`)", "acusa"], ["`x: Positivo := -1`", "acusa (`tipo-refinado`)", "acusa"], ["`x: Positivo := ler()`", "cala", "acusa se o valor não servir"], ["`xs: Cluster<Integer> := [1, \"a\"]`", "acusa (`tipo-do-conteudo`)", "acusa"], ["`xs.append(\"a\")` num `Cluster<Integer>`", "acusa quando conhece a coleção", "acusa sempre"], ["`f(\"texto\")` num `<T extends Number>`", "acusa (`generic-bound`)", "acusa"], ["`cadastrar(\"123…\")` num `Cpf`", "acusa (`tipo-opaco`)", "acusa"]]}},
  {"h2": "O que o sistema de tipos NÃO faz"},
  {"p": "Vale dizer, para ninguém contar com o que não está aqui."},
  {"table": {"head": ["Não existe", "Por quê"], "rows": [["inferência de tipo para variável sem anotação", "a linguagem é dinâmica: o analisador infere o que consegue para acusar, e não para exigir"], ["monomorfização e especialização", "não há compilação para código de máquina"], ["variância declarada (`in`/`out`)", "ainda não — `Cluster<T>` é conferido item a item"], ["prova formal do refinamento", "o `where` é verificado, não provado: literal no `check`, valor na fronteira"], ["apagamento de tipo, ABI, layout", "assunto de linguagem compilada; aqui a anotação é conferência em execução"]]}},
  {"callout": {"tipo": "nota", "titulo": "Custo", "texto": "Quem não anota nada não paga nada. A conferência acontece onde a anotação existe, e a coleção tipada só guarda quando **nasce** numa declaração tipada — uma lista que já existia é conferida e continua sendo o mesmo objeto."}},
];

const headings = [{ id: 'as-camadas', text: "As camadas", level: 2 as const }, { id: 'um-exemplo-com-todas-elas', text: "Um exemplo com todas elas", level: 2 as const }, { id: 'quando-cada-uma-acusa', text: "Quando cada uma acusa", level: 2 as const }, { id: 'o-que-o-sistema-de-tipos-nao-faz', text: "O que o sistema de tipos NÃO faz", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O sistema de tipos"}
      description={"O mapa: tipos internos, anotações, coleções tipadas, tipos nomeados, generics, indexados, opacos e traits — e o que cada camada garante."}
      href={"/docs/tipos/visao-geral"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
