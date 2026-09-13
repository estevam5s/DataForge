// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "25 · Testes com Crucible",
  description: "4 exercícios: suítes, matchers, fixtures e dublês.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 25`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[211](#211-a-primeira-suite)", "**A primeira suite**", "escreva testes que dizem o que quebrou, e nao so que quebrou."], ["[212](#212-isolamento-entre-trials)", "**Isolamento entre trials**", "prove que um teste nao contamina o proximo."], ["[213](#213-os-matchers)", "**Os matchers**", "cobre valores de todas as formas, e leia o que a falha diz."], ["[214](#214-dubles-e-fixtures)", "**Dubles e fixtures**", "teste uma regra de negocio sem tocar no banco."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "211 · A primeira suite"},
  {"p": "**Enunciado.** escreva testes que dizem o que quebrou, e nao so que quebrou."},
  { code: `// 'assert' responde "passou?" e nada mais. Quando falha, ele diz que
// uma expressao deu falso — nao o que se esperava, o que veio, nem
// qual dos quarenta casos era. O Crucible responde as outras perguntas.

adopt Crucible

action somar(a, b):
    yield a + b

action dividir(a, b):
    given b is 0:
        trigger "divisao por zero"
    yield a / b

crucible "Calculadora":

    setup:
        // roda antes de CADA trial, num quadro novo
        base := 10

    trial "soma dois numeros":
        expect somar(2, 2) is 4

    trial "soma com negativo":
        expect somar(5, 0 - 3) is 2

    trial "divide":
        expect dividir(10, 2) is 5.0

    trial "recusa divisao por zero":
        expect(lambda => dividir(1, 0)).to_raise()

    trial "ve o que o setup preparou":
        expect base is 10

    trial "adiado" pending "esperando decidir o arredondamento":
        expect dividir(1, 3) is 0.333

resumo := Crucible.run()
out Crucible.report()

assert resumo["passou"] is 5, "cinco passaram"
assert resumo["pendente"] is 1, "um adiado"
assert resumo["falhou"] is 0, "nenhum falhou"
assert resumo["verde"] is yes, "a suite esta verde"
out "ok"`, lang: 'df', title: `exercicios/25-testes-crucible/211_primeira_suite.df` },
  {"h3": "Conceitos"},
  {"p": "`assert` responde \"passou?\" e nada mais. Quando falha, ele diz que uma expressão deu falso — não o que se esperava, o que veio, nem qual dos quarenta casos era."},
  { code: `crucible "Calculadora":
    setup:
        base := 10

    trial "soma dois números":
        expect somar(2, 2) is 4`, lang: 'df' },
  {"table": {"head": ["Palavra", "Abre"], "rows": [["`crucible`", "uma suíte; suítes aninham"], ["`trial`", "um caso de teste"], ["`expect`", "uma cobrança"], ["`setup` / `teardown`", "o que roda em volta de cada trial"], ["`fixture` / `provide`", "preparo e limpeza no mesmo lugar"], ["`tagged` / `pending` / `bench`", "marcar, adiar, medir"]]}},
  {"p": "Nenhuma delas é reservada: `setup` é o nome do construtor de blueprint, e `expect` e `trial` são nomes bons demais para tirar de quem escreve. Elas só valem dentro de um bloco `crucible`."},
  {"h3": "O que observar"},
  {"p": "**`pending` não roda, e o relatório diz por quê.** É melhor que comentar o teste: um teste comentado some do relatório e é esquecido."},
  {"p": "**A forma curta cobre igualdade e comparação.** Quatro de cada cinco cobranças são igualdade, e `.to_be(...)` em volta delas só acrescenta ruído."},
  {"h3": "Armadilhas"},
  {"list": ["`expect(1 / 0)` já estourou antes de chegar ao matcher. Para testar erro, é"]},
  {"p": "`expect(lambda => 1 / 0).to_raise()`."},
  {"list": ["Um `only` esquecido faz o CI rodar um teste e reportar verde."]},
  {"h3": "Relacionados"},
  {"list": ["[210 — Isolamento](210_isolamento.md)", "[211 — Os matchers](211_matchers.md)"]},
  {"h2": "212 · Isolamento entre trials"},
  {"p": "**Enunciado.** prove que um teste nao contamina o proximo."},
  { code: `// A garantia central do Crucible: cada trial roda no proprio quadro de
// escopo, com o setup refeito. Um teste que passa sozinho e falha na
// suite seria bug do framework, nao do teste.

adopt Crucible

crucible "Isolamento":

    setup:
        contador := 0
        itens := []

    trial "o primeiro soma":
        contador := contador + 1
        itens.append("a")
        expect contador is 1
        expect len(itens) is 1

    trial "o segundo ve o valor original":
        // o que o primeiro escreveu nao existe aqui
        expect contador is 0
        expect len(itens) is 0

    trial "e o terceiro tambem":
        contador := contador + 100
        expect contador is 100

crucible "Ordem nao importa":

    setup:
        estado := "limpo"

    trial "b vem antes de a no alfabeto? nao importa":
        expect estado is "limpo"

    trial "a":
        estado := "sujo"
        expect estado is "sujo"

    trial "c":
        expect estado is "limpo"

resumo := Crucible.run()
out Crucible.report()
assert resumo["verde"] is yes, "todos passam, em qualquer ordem"

// Com ordem aleatoria, o resultado e o mesmo — e um teste que
// dependesse de ordem falharia aqui, e nao seis meses depois
Crucible.reset()

crucible "Aleatorio":
    setup:
        n := 0
    trial "um":
        n := n + 1
        expect n is 1
    trial "dois":
        n := n + 2
        expect n is 2
    trial "tres":
        expect n is 0

aleatorio := Crucible.run({"aleatorio": yes, "semente": 42})
assert aleatorio["verde"] is yes, "a ordem nao muda o resultado"
out "ok"`, lang: 'df', title: `exercicios/25-testes-crucible/212_isolamento.df` },
  {"h3": "Conceitos"},
  {"p": "A garantia central do Crucible: cada trial roda no **próprio quadro de escopo**, com o `setup` refeito. Um teste que passa sozinho e falha na suíte seria bug do framework, não do teste."},
  { code: `crucible "Isolamento":
    setup:
        contador := 0

    trial "o primeiro soma":
        contador := contador + 1
        expect contador is 1

    trial "o segundo vê o valor original":
        expect contador is 0`, lang: 'df' },
  {"p": "Os dois passam."},
  {"h3": "O que observar"},
  {"p": "**A ordem não importa.** `--aleatorio` embaralha, e a semente aparece no relatório para a falha ser reproduzível — uma ordem aleatória que não se repete é impossível de depurar."},
  {"p": "**Um teste que depende de ordem falha ali**, e não seis meses depois, numa madrugada, depois que alguém acrescentou um teste no meio."},
  {"h3": "Armadilhas"},
  {"list": ["Estado **fora** da suíte não é isolado. Um vault declarado no topo do arquivo"]},
  {"p": "é compartilhado; se você precisa dele limpo, declare no `setup`."},
  {"list": ["Recurso externo — arquivo, banco, servidor — também não. Use `fixture` para"]},
  {"p": "garantir a limpeza."},
  {"h3": "Relacionados"},
  {"list": ["[212 — Dublês e fixtures](212_dubles_e_fixtures.md)"]},
  {"h2": "213 · Os matchers"},
  {"p": "**Enunciado.** cobre valores de todas as formas, e leia o que a falha diz."},
  { code: `// Sao 59 matchers. A forma curta cobre igualdade e comparacao; a
// encadeada, o resto. As duas viram a mesma cobranca.

adopt Crucible

record Ponto:
    x: Integer
    y: Integer

crucible "Matchers":

    trial "as duas formas dao no mesmo":
        expect 2 + 2 is 4
        expect(2 + 2).to_be(4)

    trial "encadeando":
        expect(4).to_be_even().to_be_positive().to_be_between(1, 10)

    trial "ponto flutuante nunca por igualdade exata":
        // 0.1 + 0.2 nao da 0.3 em nenhuma linguagem com IEEE 754
        expect(0.1 + 0.2).to_be_close_to(0.3)

    trial "tipos":
        expect(42).to_be_integer().to_be_number()
        expect("a").to_be_text()
        expect([1]).to_be_cluster()
        expect({}).to_be_vault()
        expect(void).to_be_void()

    trial "texto":
        expect("abacate").to_start_with("aba").to_end_with("ate")
        expect("ana@x.com").to_match("^[^@]+@[^@]+$")
        expect("   ").to_be_blank()

    trial "colecoes":
        expect([1, 2, 3]).to_contain(2).to_have_length(3)
        expect([1, 2, 3]).to_be_sorted().to_be_unique()
        expect([3, 1, 2]).to_have_same_items([1, 2, 3])
        expect({"a": 1}).to_have_key("a")

    trial "todos e algum":
        expect([2, 4, 6]).to_all_satisfy(lambda n: n % 2 is 0)
        expect([1, 2, 3]).to_any_satisfy(lambda n: n bigger 2)

    trial "campo, seja vault ou record":
        // o teste nao deveria precisar saber qual dos dois o valor e
        expect({"nome": "Ana"}).to_have_field("nome", "Ana")
        expect(Ponto(1, 2)).to_have_field("x", 1)

    trial "negacao inverte SO o proximo":
        expect([1, 2, 3]).nao().to_contain(9).to_contain(2)

    trial "erro esperado":
        expect(lambda => 1 / 0).to_raise(DivisionByZeroError)
        // a familia tambem serve
        expect(lambda => 1 / 0).to_raise(RuntimeError)

    trial "e o que nao levanta":
        expect(lambda => 1 + 1).to_not_raise()

resumo := Crucible.run()
assert resumo["verde"] is yes, "todos os matchers passam"
assert resumo["passou"] is 11, "onze trials"

// A mensagem de falha mostra a DIFERENCA, nao os dois valores inteiros
Crucible.reset()
crucible "Mensagem":
    trial "vault com diferenca":
        expect {"a": 1, "b": 2, "c": 3} is {"a": 1, "b": 9, "c": 3}

Crucible.run()
resultado := Crucible.results()[0]
out "motivo:", resultado["motivo"]
out "diferenca:", resultado["diferenca"]
assert resultado["estado"] is "falhou", "falhou de proposito"
assert '"b"' in resultado["diferenca"], "aponta a chave que difere"
out "ok"`, lang: 'df', title: `exercicios/25-testes-crucible/213_matchers.df` },
  {"h3": "Conceitos"},
  {"p": "São 59 matchers, em nove grupos: igualdade, verdade, tipos, números, texto, coleções, erros, desempenho e saída. `dataforge crucible --matchers` lista todos."},
  {"p": "Duas formas, e as duas viram a mesma cobrança:"},
  { code: `expect 2 + 2 is 4                 // curta
expect(2 + 2).to_be(4)            // encadeada`, lang: 'df' },
  {"h3": "O que observar"},
  {"p": "**Nunca `to_be` com float.** `0.1 + 0.2` não dá `0.3` em nenhuma linguagem com IEEE 754. Cobrar igualdade exata de ponto flutuante é escrever um teste que falha por motivo errado. `to_be_close_to` existe para isso."},
  {"p": "**A mensagem mostra a diferença, não os dois valores.** Comparar dois vaults de dez chaves lendo os dois inteiros não se faz — o Crucible aponta a chave que difere."},
  {"p": "**`nao()` inverte só o próximo.** Um estado invertido pendurado faria a segunda cobrança da cadeia sair ao contrário."},
  {"p": "**A família serve em `to_raise`.** `to_raise(RuntimeError)` aceita `DivisionByZeroError`, como o `handle` da linguagem."},
  {"h3": "Armadilhas"},
  {"list": ["`to_have_field` serve para vault, record e instância — o teste não deveria"]},
  {"p": "precisar saber qual dos três o valor é."},
  {"list": ["`to_raise` precisa de uma **ação**, não de um valor: `expect(lambda => …)`."]},
  {"h3": "Relacionados"},
  {"list": ["[209 — A primeira suíte](209_primeira_suite.md)"]},
  {"h2": "214 · Dubles e fixtures"},
  {"p": "**Enunciado.** teste uma regra de negocio sem tocar no banco."},
  { code: `// Um servico que constroi a propria conexao exige subir PostgreSQL
// para testar uma validacao de nome. Um que recebe o repositorio por
// parametro se testa com um duble, em microssegundos.

adopt Crucible

trait Repositorio:
    action salvar(nome)
    action contar()

blueprint ServicoDeCadastro:
    action setup(repositorio):
        self.repositorio := repositorio

    action cadastrar(nome):
        given len(nome) smaller 2:
            trigger "nome curto demais"
        yield self.repositorio.salvar(nome)

crucible "Cadastro":

    trial "salva o que passa na validacao":
        repo := Crucible.mock("repositorio")
        repo.quando("salvar").devolve("Ana")

        s := spawn ServicoDeCadastro(repo)
        expect s.cadastrar("Ana") is "Ana"
        expect repo.chamado_com("salvar", "Ana") is yes

    trial "e NAO salva o que nao passa":
        // cobrar o que nao aconteceu e o que so o duble permite
        repo := Crucible.mock("repositorio")
        s := spawn ServicoDeCadastro(repo)

        expect(lambda => s.cadastrar("A")).to_raise()
        expect repo.foi_chamado("salvar") is no

    trial "anota todas as chamadas":
        m := Crucible.mock("api")
        m.buscar(1)
        m.buscar(2)
        m.salvar("x")

        expect m.vezes("buscar") is 2
        expect m.argumentos_de("buscar") is [[1], [2]]
        expect m.foi_chamado("apagar") is no

    trial "respostas em sequencia":
        m := Crucible.mock()
        m.quando("proximo").devolve_em_sequencia([1, 2, 3])
        expect[m.proximo(), m.proximo(), m.proximo()] is [1, 2, 3]

crucible "Fixtures":

    // 'provide' divide a fixture: antes prepara, depois limpa.
    // Escrever as duas juntas e o que impede a limpeza de ser
    // esquecida — o modo mais comum de uma suite virar fragil.
    fixture banco():
        adopt Forge
        db := Forge.conectar(":memory:")
        Forge.executar(db, "create table t (id integer primary key, n integer)")
        provide db
        Forge.fechar(db)

    trial "usa o banco preparado":
        adopt Forge
        db := banco()
        Forge.de(db, "t").inserir({"n": 1})
        expect Forge.de(db, "t").contar() is 1

resumo := Crucible.run()
out Crucible.report()
assert resumo["verde"] is yes, "todos passam"
assert resumo["passou"] is 5, "cinco trials"
out "ok"`, lang: 'df', title: `exercicios/25-testes-crucible/214_dubles_e_fixtures.df` },
  {"h3": "Conceitos"},
  {"p": "Um serviço que constrói a própria conexão exige subir PostgreSQL para testar uma validação de nome. Um que **recebe** o repositório por parâmetro se testa com um dublê, em microssegundos."},
  { code: `repo := Crucible.mock("repositorio")
repo.quando("salvar").devolve("Ana")

s := spawn ServicoDeCadastro(repo)
expect s.cadastrar("Ana") is "Ana"
expect repo.chamado_com("salvar", "Ana") is yes`, lang: 'df' },
  {"p": "É [inversão de dependência](https://dataforge-lang.vercel.app/docs/oop/solid) na prática."},
  {"h3": "O que observar"},
  {"p": "**Cobrar o que NÃO aconteceu.** O segundo trial verifica que o repositório não foi chamado. Sem o dublê, isso exigiria olhar o banco — e um teste que precisa de banco para verificar uma regra de nome está testando a coisa errada."},
  {"p": "**`provide` divide a fixture.** O que vem antes prepara; o que vem depois limpa. Escrever as duas juntas é o que impede a limpeza de ser esquecida — o modo mais comum de uma suíte passar a depender de ordem."},
  {"p": "**A limpeza roda mesmo com falha**, e só para as fixtures que o trial realmente usou."},
  {"h3": "Armadilhas"},
  {"list": ["Um mock que devolve sempre a mesma coisa esconde bug de paginação."]},
  {"p": "`devolve_em_sequencia` cobre isso."},
  {"list": ["Testar o mock em vez do código: se todas as expectativas são sobre chamadas e"]},
  {"p": "nenhuma sobre resultado, o teste não prova nada."},
  {"h3": "Relacionados"},
  {"list": ["[210 — Isolamento](210_isolamento.md)", "[206 — Relações](../24-banco-de-dados/206_relacoes_sem_n_mais_um.md)"]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/25-testes-crucible/211_primeira_suite.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '211-a-primeira-suite', text: "211 · A primeira suite", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '212-isolamento-entre-trials', text: "212 · Isolamento entre trials", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '213-os-matchers', text: "213 · Os matchers", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }, { id: '214-dubles-e-fixtures', text: "214 · Dubles e fixtures", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-observar', text: "O que observar", level: 3 as const }, { id: 'armadilhas', text: "Armadilhas", level: 3 as const }, { id: 'relacionados', text: "Relacionados", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"25 · Testes com Crucible"}
      description={"4 exercícios: suítes, matchers, fixtures e dublês."}
      href={"/docs/exercicios/25-testes-crucible"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
