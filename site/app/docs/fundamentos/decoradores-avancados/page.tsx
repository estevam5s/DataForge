import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Decoradores",
  description: "Embrulhar e anotar — e o que os metadados permitem construir.",
};

const blocos: Bloco[] = [
  {"p": "Um decorador faz duas coisas: **embrulha** (troca o comportamento) e **anota** (deixa um metadado que outra parte lê). A segunda é a que permite escrever, na própria linguagem, o tipo de framework que outras escrevem no compilador."},
  {"h2": "A forma"},
  { code: `action logar(f):
    action envolvida(x):
        out "chamando com", x
        resultado := f(x)
        out "devolveu", resultado
        yield resultado
    yield envolvida

@logar
action dobrar(n):
    yield n * 2

out dobrar(21)
// chamando com 21
// devolveu 42
// 42` },
  {"p": "Um decorador é uma **ação que recebe o que decora e devolve o que fica no lugar**. Não há sintaxe especial: `@logar` sobre `dobrar` é `dobrar := logar(dobrar)`."},
  {"h2": "Onde vale"},
  {"table": {"head": ["Alvo", "Exemplo"], "rows": [["`action`", "`@memoizar` numa função cara"], ["`blueprint`", "`@Entidade(\"usuarios\")` numa classe de domínio"], ["`record`", "`@Validar` num dado imutável"], ["**método** dentro de um blueprint", "`@Rota(\"GET\", \"/\")` num controlador"]]}},
  {"p": "O método é onde eles mais servem: as rotas ficam ao lado dos métodos que as atendem, em vez de numa tabela em outro arquivo."},
  {"h2": "Com argumentos, é uma fábrica"},
  { code: `action repetir(vezes):
    action aplicar(f):
        action envolvida(x):
            cycle i from 1 to vezes:
                f(x)
        yield envolvida
    yield aplicar

@repetir(3)
action falar(texto):
    out texto

falar("oi")     // imprime três vezes` },
  {"p": "Sem argumentos, o decorador recebe o alvo direto. Com argumentos, ele recebe **primeiro a configuração** e devolve a ação que recebe o alvo. É a mesma regra do Python e do TypeScript."},
  {"p": "Argumentos nomeados também valem: `@Rota(\"/itens\", metodo: \"POST\")`."},
  {"h2": "Pilha"},
  { code: `@Injetavel
@Cache(60)
@logar
action buscar(id):
    yield banco.achar(id)` },
  {"p": "Aplicam-se **de baixo para cima**: `logar` embrulha primeiro, `Cache` embrulha o resultado, `Injetavel` embrulha o de cima. É a ordem de toda linguagem que tem decoradores."},
  {"h2": "Decorador que só anota"},
  { code: `action Rota(metodo, caminho):
    action aplicar(alvo):
        // não embrulha nada: devolve void
        yield void
    yield aplicar

@Rota("GET", "/itens")
action listar():
    yield itens

out listar()    // funciona normalmente` },
  {"p": "Um decorador que devolve `void` **não substitui** o alvo — a ação segue sendo ela mesma. Sem essa regra, `@Rota(\"/x\")` apagaria a ação que decorou."},
  {"p": "O que ele deixa é o metadado, e é aí que a coisa fica interessante."},
  {"h2": "Ler os metadados"},
  {"p": "O módulo [`Arcane.Meta`](/docs/biblioteca/meta) é a outra metade: o decorador grava, `Meta` lê."},
  { code: `adopt Arcane.Meta as Meta

@Rota("GET", "/itens")
action listar():
    yield 1

out Meta.tem(listar, "Rota")            // yes
out Meta.nomes(listar)                  // [Rota]
out Meta.arg(listar, "Rota", 0)         // GET
out Meta.arg(listar, "Rota", 1)         // /itens
out Meta.opcao(listar, "Rota", "cache") // void (não foi passado)` },
  {"table": {"head": ["Função", "Devolve"], "rows": [["`Meta.tem(alvo, nome)`", "o alvo foi decorado com `@nome`?"], ["`Meta.nomes(alvo)`", "os nomes dos decoradores, em ordem"], ["`Meta.ler(alvo, nome)`", "`{nome, args, kwargs}` do primeiro `@nome`"], ["`Meta.arg(alvo, nome, i, padrao)`", "um argumento posicional"], ["`Meta.opcao(alvo, nome, chave, padrao)`", "um argumento nomeado"], ["`Meta.metodos_com(blueprint, nome)`", "os métodos anotados com `@nome`"], ["`Meta.filtrar(valores, nome)`", "de uma lista, os que têm `@nome`"], ["`Meta.descrever(alvo)`", "tipo, nome, decoradores, métodos, campos"]]}},
  {"h2": "Um framework em 40 linhas"},
  {"p": "O que os metadados permitem: um roteador que **descobre as rotas sozinho**, lendo o que os decoradores deixaram."},
  { code: `adopt Arcane.Meta as Meta

action Controlador(prefixo):
    action aplicar(alvo):
        yield void
    yield aplicar

action Rota(metodo, caminho):
    action aplicar(alvo):
        yield void
    yield aplicar

@Controlador("/usuarios")
blueprint UsuariosController:
    @Rota("GET", "/")
    action listar():
        yield "todos"

    @Rota("GET", "/:id")
    action mostrar():
        yield "um"

    @Rota("POST", "/")
    action criar():
        yield "criado"

// O roteador não sabe nada sobre este controlador — ele descobre.
prefixo := Meta.arg(UsuariosController, "Controlador", 0)
cycle r in Meta.metodos_com(UsuariosController, "Rota"):
    verbo := r["meta"]["args"][0]
    caminho := r["meta"]["args"][1]
    nome := r["nome"]
    out $"{verbo} {prefixo}{caminho}  ->  {nome}()"

// GET /usuarios/      ->  listar()
// GET /usuarios/:id   ->  mostrar()
// POST /usuarios/     ->  criar()` },
  {"p": "Acrescentar uma rota é acrescentar um método com `@Rota`. Nada mais precisa mudar."},
  {"h2": "Injeção de dependência"},
  { code: `adopt Arcane.Meta as Meta

action Injetavel(alvo):
    yield void

blueprint Container:
    instancias: Vault := {}
    registrados: Vault := {}

    action registrar(nome, tipo):
        given not Meta.tem(tipo, "Injetavel"):
            trigger $"{nome} não é @Injetavel"
        self.registrados[nome] := tipo

    action resolver(nome):
        given nome in self.instancias:
            yield self.instancias[nome]
        instancia := spawn self.registrados[nome]()
        self.instancias[nome] := instancia
        yield instancia

@Injetavel
blueprint Repositorio:
    action todos():
        yield ["Ana", "Bia"]

c := spawn Container()
c.registrar("repo", Repositorio)

repo := c.resolver("repo")
out len(repo.todos())              // 2
out c.resolver("repo") is repo     // yes — a mesma instância` },
  {"p": "O contêiner recusa registrar o que não foi anotado. A anotação é o contrato, e ele é verificado em tempo de execução."},
  {"h2": "Decoradores úteis, prontos para copiar"},
  {"h3": "Memoização"},
  { code: `action memoizar(f):
    cache := {}
    action envolvida(x):
        chave := str(x)
        given chave in cache:
            yield cache[chave]
        resultado := f(x)
        cache[chave] := resultado
        yield resultado
    yield envolvida

@memoizar
action fib(n):
    given n smaller 2:
        yield n
    yield fib(n - 1) + fib(n - 2)

out fib(35)     // instantâneo; sem o cache, minutos` },
  {"h3": "Medir o tempo"},
  { code: `adopt Arcane.Time as Time

action cronometrar(f):
    action envolvida(x):
        inicio := Time.monotonic()
        resultado := f(x)
        gasto := round((Time.monotonic() - inicio) * 1000, 2)
        out $"[{gasto} ms]"
        yield resultado
    yield envolvida` },
  {"h3": "Tentar de novo"},
  { code: `action tentar(vezes):
    action aplicar(f):
        action envolvida(x):
            ultima := void
            cycle i from 1 to vezes:
                monitor:
                    yield f(x)
                handle Error as e:
                    ultima := e
                    out $"tentativa {i} falhou"
            propagate ultima
        yield envolvida
    yield aplicar

@tentar(3)
action buscar_remoto(url):
    yield Web.get(url)` },
  {"h2": "Erros que a linguagem pega"},
  {"table": {"head": ["Erro", "O que acontece"], "rows": [["`@NaoExiste`", "erro dizendo que o decorador não existe, com dica de como declarar"], ["`@algo` sobre `x := 1`", "erro: decoradores valem para `action`, `blueprint` e `record`"], ["decorador que devolve o tipo errado", "o valor devolvido fica no lugar do alvo — é o que ele pediu"]]}},
  {"h2": "Comparado ao que você conhece"},
  {"table": {"head": ["", "DataForge", "Python", "TypeScript"], "rows": [["forma", "`@nome`", "`@nome`", "`@nome`"], ["com argumento", "`@nome(a)`", "`@nome(a)`", "`@nome(a)`"], ["em classe", "sim", "sim", "sim"], ["em método", "sim", "sim", "sim"], ["ler metadado", "`Meta.ler(x, \"Nome\")`", "atributo à mão", "`reflect-metadata`"], ["metadado embutido", "**sim**", "não", "não (precisa de biblioteca)"]]}},
  {"p": "A diferença é a última linha: em Python e TypeScript, guardar o metadado é responsabilidade de quem escreve o decorador — e cada framework inventa o seu. Aqui o interpretador grava, e `Arcane.Meta` lê."},
  {"h2": "Onde ver funcionando"},
  {"table": {"head": ["Onde", "O quê"], "rows": [["[Playground](/painel/playground)", "o exemplo \"Decoradores\" roda no navegador e mostra o que foi declarado"], ["`tests/test_decoradores.py`", "20 testes, inclusive um roteador completo"], ["[`Arcane.Meta`](/docs/biblioteca/meta)", "as 12 funções de leitura"]]}},
];

const headings = [{ id: 'a-forma', text: "A forma", level: 2 as const }, { id: 'onde-vale', text: "Onde vale", level: 2 as const }, { id: 'com-argumentos-e-uma-fabrica', text: "Com argumentos, é uma fábrica", level: 2 as const }, { id: 'pilha', text: "Pilha", level: 2 as const }, { id: 'decorador-que-so-anota', text: "Decorador que só anota", level: 2 as const }, { id: 'ler-os-metadados', text: "Ler os metadados", level: 2 as const }, { id: 'um-framework-em-40-linhas', text: "Um framework em 40 linhas", level: 2 as const }, { id: 'injecao-de-dependencia', text: "Injeção de dependência", level: 2 as const }, { id: 'decoradores-uteis-prontos-para-copiar', text: "Decoradores úteis, prontos para copiar", level: 2 as const }, { id: 'memoizacao', text: "Memoização", level: 3 as const }, { id: 'medir-o-tempo', text: "Medir o tempo", level: 3 as const }, { id: 'tentar-de-novo', text: "Tentar de novo", level: 3 as const }, { id: 'erros-que-a-linguagem-pega', text: "Erros que a linguagem pega", level: 2 as const }, { id: 'comparado-ao-que-voce-conhece', text: "Comparado ao que você conhece", level: 2 as const }, { id: 'onde-ver-funcionando', text: "Onde ver funcionando", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Decoradores"}
      description={"Embrulhar e anotar — e o que os metadados permitem construir."}
      href={"/docs/fundamentos/decoradores-avancados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
