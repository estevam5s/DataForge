// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Mudanças",
  description: "Escrever pelo Lavra — e as quatro regras que separam uma mudança de um GET com efeito colateral.",
};

const blocos: Bloco[] = [
  {"p": "Uma **busca** pode ser repetida, cacheada e feita em paralelo. Uma **mudança** não: ela é a única parte do Lavra que altera o mundo, e por isso as regras são outras — inclusive a ordem de execução."},
  { code: `adopt Arcane.Lavra as Lavra

record Tarefa:
    id: Integer
    titulo: String
    feita: Boolean

BANCO := {"proximo": 1, "itens": []}

action criar(raiz, args, ctx):
    id := BANCO["proximo"]
    BANCO["proximo"] := id + 1
    t := Tarefa(id, args["titulo"], no)
    BANCO["itens"].append(t)
    yield t

esq := Lavra.esquema("tarefas")
Lavra.tipo(esq, Tarefa)
// Todo esquema precisa de ao menos uma BUSCA — 'conferir' recusa um
// esquema só de mudanças, porque um cliente não teria como ler nada.
Lavra.busca(esq, "tarefas", "[Tarefa!]!",
    resolve := lambda r, a, c => BANCO["itens"])
Lavra.mudanca(esq, "criarTarefa", "Tarefa!",
    args := {"titulo": "String!"}, resolve := criar)
Lavra.conferir(esq)

r := Lavra.executar(esq, """
mudanca:
    criarTarefa(titulo: "comprar café"):
        id
        titulo
        feita
""")
assert r["dados"]["criarTarefa"]["id"] is 1
assert r["dados"]["criarTarefa"]["feita"] is no
out r["dados"]`, lang: 'df' },
  {"h2": "As quatro regras"},
  {"table": {"head": ["Regra", "Sem ela"], "rows": [["as mudanças de uma requisição rodam **em série**", "duas escritas na mesma linha competem, e o resultado depende do escalonador"], ["a mudança **devolve o que mudou**", "o cliente precisa de uma segunda ida à rede para ver o resultado"], ["o argumento de entrada é um **tipo de entrada**", "quinze argumentos soltos, e nenhum lugar para validar o conjunto"], ["a falha de uma mudança é **erro**, não `void` no campo", "o cliente grava um estado que não aconteceu"]]}},
  {"h2": "O tipo de entrada"},
  {"p": "Um formulário de dez campos como dez argumentos é ilegível, e não tem onde declarar o que é obrigatório junto. `Lavra.entrada` dá nome ao conjunto:"},
  { code: `adopt Arcane.Lavra as Lavra

record Cliente:
    id: Integer
    nome: String
    email: String

record NovoCliente:
    nome: String
    email: String

esq := Lavra.esquema("crm")
Lavra.tipo(esq, Cliente)
// Entrada e saída são tipos DIFERENTES de propósito: o 'Cliente' que
// sai tem 'id'; o que entra, não. Usar o mesmo tipo nos dois lados
// obrigaria a marcar metade dos campos como opcionais — e aí nenhum
// deles seria conferido.
Lavra.entrada(esq, NovoCliente)
Lavra.campo(esq, "NovoCliente", "nome", "String!")
Lavra.campo(esq, "NovoCliente", "email", "String!")

action criar(raiz, args, ctx):
    dados := args["dados"]
    given "@" not in dados["email"]:
        trigger Lavra.erro("e-mail inválido", "validacao", {"campo": "email"})
    yield Cliente(1, dados["nome"], dados["email"])

Lavra.busca(esq, "clientes", "[Cliente!]!", resolve := lambda r, a, c => [])
Lavra.mudanca(esq, "criarCliente", "Cliente!",
    args := {"dados": "NovoCliente!"}, resolve := criar)
Lavra.conferir(esq)

r := Lavra.executar(esq, """
mudanca:
    criarCliente(dados: {nome: "Ana", email: "ana@ex.com"}):
        id
        nome
""")
assert r["dados"]["criarCliente"]["nome"] is "Ana"

// e o e-mail errado vira ERRO, com código e campo
ruim := Lavra.executar(esq, """
mudanca:
    criarCliente(dados: {nome: "Ana", email: "sem-arroba"}):
        id
""")
assert len(ruim["erros"]) is 1
out ruim["erros"][0]`, lang: 'df' },
  {"h2": "O erro tem código, e o código é o contrato"},
  {"p": "`\"e-mail inválido\"` é para a pessoa; `\"validacao\"` é para o programa. Um cliente que decide pelo **texto** da mensagem quebra na primeira tradução — e essa é a razão de o erro carregar um código e um vault de extras."},
  { code: `adopt Arcane.Lavra as Lavra

// Os três desfechos que um resolvedor tem, e o que cada um significa:
action nao_achei(r, a, c):
    yield void                                     // ausência

action negado(r, a, c):
    trigger Lavra.recusar("sem permissão")         // autorização

action quebrado(r, a, c):
    trigger Lavra.erro("o banco caiu", "indisponivel")   // falha

esq := Lavra.esquema("x")
Lavra.busca(esq, "vazio", "String", resolve := nao_achei)
Lavra.busca(esq, "negado", "String", resolve := negado)
Lavra.busca(esq, "quebrado", "String", resolve := quebrado)
Lavra.conferir(esq)

assert Lavra.executar(esq, "busca:\\n    vazio")["dados"]["vazio"] is void
assert len(Lavra.executar(esq, "busca:\\n    negado")["erros"]) is 1
assert len(Lavra.executar(esq, "busca:\\n    quebrado")["erros"]) is 1
out "void é ausência; erro é falha — e o cliente trata os dois de formas diferentes"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Idempotência não vem de graça", "texto": "Repetir `criarTarefa` cria duas tarefas — como um POST. Se o cliente pode repetir (e ele pode: rede cai no meio), a mudança precisa de uma **chave de idempotência** vinda do cliente, e o servidor é quem a honra. É a mesma regra da `Arcane.Malha`: quem fabrica idempotência é o outro lado."}},
];

const headings = [{ id: 'as-quatro-regras', text: "As quatro regras", level: 2 as const }, { id: 'o-tipo-de-entrada', text: "O tipo de entrada", level: 2 as const }, { id: 'o-erro-tem-codigo-e-o-codigo-e-o-contrato', text: "O erro tem código, e o código é o contrato", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Mudanças"}
      description={"Escrever pelo Lavra — e as quatro regras que separam uma mudança de um GET com efeito colateral."}
      href={"/docs/lavra/mutacoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
