// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/testes_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "TDD — vermelho, verde, refatorar",
  description: "O ciclo, passo a passo, construindo um carrinho de compras — e o que cada fase protege.",
};

const blocos: Bloco[] = [
  {"p": "TDD não é escrever teste antes. É escrever **um** teste, vê-lo falhar pelo motivo certo, fazer o mínimo para ele passar, e só então melhorar o código — com o teste segurando o comportamento enquanto a forma muda."},
  {"table": {"head": ["Fase", "O que se faz", "O que ela protege"], "rows": [["**vermelho**", "um teste que falha", "que o teste consegue falhar — um teste que nunca falhou não prova nada"], ["**verde**", "o mínimo para passar", "que o código existe por causa de um comportamento pedido"], ["**refatorar**", "melhorar a forma, sem mudar o comportamento", "que a limpeza não quebrou nada"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Veja o vermelho pelo motivo certo", "texto": "Um teste que falha com *“'total' não está definido”* não está vermelho: está quebrado. O vermelho útil é o que falha com *“devia ser 30, e veio 0”* — é ele que prova que o teste mede o que você acha que ele mede."}},
  {"h2": "1. Vermelho: o primeiro comportamento"},
  { code: `// O teste vem primeiro, e a acao existe so o bastante para compilar.
action total(itens):
    yield 0

assert total([]) is 0
// O proximo teste e o que vai falhar:
//   assert total([{"preco": 10, "qtd": 3}]) is 30
out "passo 1: o caso vazio passa; o proximo vai falhar pelo motivo certo"`, lang: 'df' },
  {"h2": "2. Verde: o mínimo"},
  { code: `action total(itens):
    soma := 0
    cycle i in itens:
        soma += i["preco"] * i["qtd"]
    yield soma

assert total([]) is 0
assert total([{"preco": 10, "qtd": 3}]) is 30
assert total([{"preco": 10, "qtd": 3}, {"preco": 5, "qtd": 2}]) is 40
out "passo 2: verde"`, lang: 'df' },
  {"h2": "3. O próximo comportamento puxa o próximo teste"},
  {"p": "A regra nova — *cupom de 10% acima de 100* — entra do mesmo jeito: primeiro o teste, depois o código."},
  { code: `action subtotal(itens):
    yield sum(itens >> morph i: i["preco"] * i["qtd"])

action total(itens, cupom := ""):
    s := subtotal(itens)
    given cupom is "DEZ" and s bigger 100:
        yield round(s * 0.9, 2)
    yield s

// Os testes antigos continuam — e sao eles que autorizam a refatoracao.
assert total([]) is 0
assert total([{"preco": 10, "qtd": 3}]) is 30
assert total([{"preco": 60, "qtd": 2}], "DEZ") is 108.0
assert total([{"preco": 60, "qtd": 1}], "DEZ") is 60
out "passo 3: a regra nova, e as antigas seguraram a mudanca"`, lang: 'df' },
  {"h2": "Refatorar: o que pode e o que não pode"},
  {"table": {"head": ["Pode", "Não pode"], "rows": [["extrair `subtotal` de `total`", "mudar o que `total` devolve"], ["trocar o laço por pipeline", "acrescentar comportamento *“já que estou aqui”*"], ["renomear o que é interno", "mudar teste e código no mesmo passo"]]}},
  {"callout": {"tipo": "dica", "titulo": "Passos pequenos", "texto": "Se o verde demora mais de alguns minutos, o teste pediu demais. Volte, escreva um teste menor. O TDD funciona porque cada passo é pequeno o bastante para que, quando algo quebra, só haja um lugar onde procurar."}},
  {"p": "Continue em [Testes unitários](/docs/testes/unitarios) e [Regressão](/docs/testes/regressao)."},
];

const headings = [{ id: '1-vermelho-o-primeiro-comportamento', text: "1. Vermelho: o primeiro comportamento", level: 2 as const }, { id: '2-verde-o-minimo', text: "2. Verde: o mínimo", level: 2 as const }, { id: '3-o-proximo-comportamento-puxa-o-proximo-teste', text: "3. O próximo comportamento puxa o próximo teste", level: 2 as const }, { id: 'refatorar-o-que-pode-e-o-que-nao-pode', text: "Refatorar: o que pode e o que não pode", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"TDD — vermelho, verde, refatorar"}
      description={"O ciclo, passo a passo, construindo um carrinho de compras — e o que cada fase protege."}
      href={"/docs/testes/tdd"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
