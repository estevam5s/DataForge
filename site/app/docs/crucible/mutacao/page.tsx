// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/crucible_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Contratos e mutação",
  description: "O mesmo teste valendo para duas implementações, e a pergunta que a cobertura não responde.",
};

const blocos: Bloco[] = [
  {"h2": "Contrato: um trait, muitas implementações"},
  {"p": "Duas implementações do mesmo trait costumam ter **dois** conjuntos de testes, escritos em épocas diferentes, cobrindo coisas diferentes. A segunda passa nos testes dela e quebra no uso — porque o que ela não cumpre é justamente o que só o teste da primeira cobria."},
  { code: `action guarda_e_le(a):
    a.guardar("x", 1)
    expect(a.ler("x")).to_be(1)

action apaga(a):
    a.guardar("x", 1)
    a.apagar("x")
    expect(a.ler("x")).to_be_void()

provas := Crucible.contrato("Armazem", [
    {"nome": "guarda e le", "prova": guarda_e_le},
    {"nome": "apaga", "prova": apaga}
])

provas.para("em memoria", lambda => spawn EmMemoria())
provas.para("em disco", lambda => spawn EmDisco("/tmp/x"))
provas.cobrar()`, lang: 'df' },
  {"p": "`cobrar()` levanta nomeando **qual implementação** falhou em **qual caso**. A alternativa — um resumo dizendo \"2 falhas\" — manda procurar em dois lugares."},
  {"h2": "Mutação: o teste testa mesmo?"},
  {"p": "Cobertura responde *\"esta linha rodou?\"*. Ela não responde *\"se esta linha estivesse errada, alguém reclamaria?\"* — e as duas divergem justamente onde importa: um teste que chama a função e **não confere o resultado** dá 100% de cobertura e zero de proteção."},
  {"p": "A mutação responde a segunda pergunta: troca um operador no código, roda a suíte, e vê se ela falha. Se a suíte **passar**, aquele teste não testava aquilo. O mutante é chamado de *sobrevivente*, e cada sobrevivente é um buraco com endereço."},
  { code: `r := Crucible.mutar("src/calculo.df",
                    lambda => Crucible.run()["falhas"] bigger 0)

out Crucible.relatorio_de_mutacao(r)
expect(r["sobreviventes"]).to_be_empty()`, lang: 'df' },
  { code: `  src/calculo.df
  7/9 mutantes pegos (78%)

  sobreviveram — ninguém reclamou destas trocas:
    linha 12: bigger_eq → bigger  (afrouxa um limite: '>=' vira '>')
      yield idade bigger_eq 18
    linha 27: * → /  (troca a operação)
      yield valor * desconto`, lang: 'text' },
  {"p": "A primeira sobrevivente diz que nenhum teste passa exatamente 18 — o caso de borda. A segunda, que ninguém confere o valor com desconto."},
  {"table": {"head": ["Decisão", "Por quê"], "rows": [["**uma** troca por mutante", "com duas, um teste que pega a primeira esconde a segunda"], ["fronteira de palavra", "`bigger` é pedaço de `bigger_eq`; sem ela o relatório descreveria uma troca e faria outra"], ["comentário e texto não mutam", "mudar um literal ali não muda comportamento, e o mutante sobreviveria sempre"], ["suíte que **estoura** conta como pego", "o código quebrado não passou despercebido, que é a única pergunta"], ["o arquivo volta num `finally`", "um código-fonte silenciosamente alterado é o pior desfecho de uma ferramenta de teste"]]}},
  {"callout": {"tipo": "atencao", "titulo": "O custo, dito de frente", "texto": "Cada mutante roda a suíte inteira. Com quarenta mutantes e uma suíte de dois segundos, são oitenta segundos — por isso o `limite` existe e por isso isto **não** roda no CI de cada commit. É uma ferramenta de auditoria, e não um portão."}},
  {"h2": "As onze trocas"},
  {"p": "Cada uma é uma mudança que um humano faria por engano, e que um teste de verdade pegaria. Trocas que quase sempre produzem erro de sintaxe ou laço infinito ficam de fora: elas gastam uma rodada da suíte para não dizer nada."},
  {"table": {"head": ["Troca", "O que ela simula"], "rows": [["`bigger_eq` → `bigger`", "afrouxa um limite — o caso de borda"], ["`smaller_eq` → `smaller`", "o mesmo, do outro lado"], ["`bigger` ↔ `smaller`", "inverte a comparação"], ["`is not` → `is`", "inverte a igualdade"], ["`and` ↔ `or`", "troca o conectivo"], ["`+` ↔ `-` · `*` → `/`", "troca a operação"], ["`yes` → `no`", "inverte um literal lógico"]]}},
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/crucible/cenarios", "title": "Cenários", "desc": "Concorrência, relógio e um HTTP que você controla."}, {"href": "/docs/crucible/matchers", "title": "Os matchers", "desc": "As 79 cobranças, por família."}, {"href": "/docs/tecnicas/cobertura", "title": "Cobertura", "desc": "O que a cobertura mede — e o que ela não mede."}, {"href": "/docs/crucible/relatorios", "title": "Relatórios e CI", "desc": "JUnit, JSON, TAP e benchmark."}]},
];

const headings = [{ id: 'contrato-um-trait-muitas-implementacoes', text: "Contrato: um trait, muitas implementações", level: 2 as const }, { id: 'mutacao-o-teste-testa-mesmo', text: "Mutação: o teste testa mesmo?", level: 2 as const }, { id: 'as-onze-trocas', text: "As onze trocas", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Contratos e mutação"}
      description={"O mesmo teste valendo para duas implementações, e a pergunta que a cobertura não responde."}
      href={"/docs/crucible/mutacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
