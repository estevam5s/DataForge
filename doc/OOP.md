# Orientação a objetos no DataForge

Este é o guia de OOP da linguagem: o modelo de objetos, a sintaxe de cada
recurso, as ferramentas que conferem, e um **mapa** — tópico por tópico —
do que existe, onde está, e o que não existe por decisão.

Tudo o que aparece em bloco `dataforge` aqui roda. A referência formal está
em [REFERENCIA.md §7](REFERENCIA.md#7-blueprints); as páginas com mais
exemplos estão em [/docs/oop](https://dataforge-lang.vercel.app/docs/oop).

---

## 1. O modelo em uma página

| Conceito | DataForge |
|---|---|
| classe | `blueprint` |
| instância | `spawn Nome(…)` (ou `Nome(…)`) |
| construtor | parâmetros do cabeçalho, `setup` / `initiate` / `__init__`, corpo solto |
| destrutor | `teardown` / `__del__` |
| `this` / `super` | `self` / `root` (segue a MRO C3) |
| interface | `contract` (só assinatura) |
| trait / mixin | `trait` (com implementação padrão) |
| classe abstrata | `abstract blueprint` + `abstract action` |
| classe final / selada | `final blueprint` / `sealed blueprint` |
| objeto de valor | `record` (imutável, igualdade estrutural) |
| enum | `enum`, com métodos |
| metaclasse | `meta blueprint` + `using` |
| método de extensão / classe parcial | `augment` |
| anotação | `@Nome(args)` — em ação, blueprint, record, propriedade e campo |
| reflexão | `Arcane.Reflexo` |
| injeção de dependência | `Arcane.Injecao` |

```dataforge
contract Forma:
    action area() -> Float

abstract blueprint Base with Forma:
    readonly nome := ""
    invariant self.area() bigger_eq 0.0, "área negativa"
    action descrever():
        yield $"{self.nome}: {self.area()}"

final blueprint Retangulo(largura: Float, altura: Float) extends Base:
    action setup(largura, altura):
        self.nome := "retângulo"
    override action area() -> Float:
        yield self.largura * self.altura

r := spawn Retangulo(2.0, 3.0)
assert r.descrever() is "retângulo: 6.0"
```

**Identidade × igualdade.** Dois `spawn` são dois objetos: `is` entre
instâncias é identidade, a menos que o blueprint declare `__eq__`. Dois
`record` com os mesmos campos **são** o mesmo valor. A pergunta que decide
entre os dois: *dois destes, com os mesmos valores, são a mesma coisa?*

---

## 2. Encapsulamento

| Modificador | Alcance | Erro |
|---|---|---|
| `private` | o blueprint que declarou | `TypeError` |
| `protected` | o blueprint e os herdeiros | `TypeError` |
| `internal` | o arquivo que declarou | `InternalAccessError` |
| `readonly` | escrita só durante a construção | `ReadOnlyFieldError` |
| `static steady` | constante de classe | `ConstantReassignmentError` |

A visibilidade vale para **leitura, escrita e chamada**, e vale também
através de `Arcane.Reflexo`: reflexão não é porta dos fundos.

Propriedades (`get`/`set`, `lazy get`), descritores (`__get__`/`__set__`/
`__set_name__`) e `slots` completam o controle de atributo.

```dataforge
blueprint Temperatura:
    private celsius := 0.0
    get fahrenheit():
        yield self.celsius * 9 / 5 + 32
    set fahrenheit(f):
        expects f bigger_eq -459.67, "abaixo do zero absoluto"
        self.celsius := (f - 32) * 5 / 9

t := spawn Temperatura()
t.fahrenheit := 212
assert t.fahrenheit is 212.0
```

---

## 3. Herança, polimorfismo e MRO

- Herança simples, multinível e múltipla (`extends A, B`), resolvida por
  **linearização C3**; um diamante ambíguo é recusado.
- `override` promete substituir algo herdado — de mãe, trait ou contrato.
- `final action` impede a substituição; `final blueprint`, a herança;
  `sealed blueprint`, a herança fora do arquivo.
- Todo método é despacho dinâmico (virtual); não há `virtual` para escrever.
- `__init_subclass__` roda quando alguém herda.
- O `check` avisa quando uma sobrescrita aceita **menos** argumentos que a
  mãe (`substituicao-quebrada` — Liskov).

```dataforge
blueprint Notificador:
    action enviar(msg, urgente := no):
        yield "genérico"

blueprint Email extends Notificador:
    override action enviar(msg, urgente := no):
        yield "email: " + msg

blueprint Sms extends Notificador:
    override action enviar(msg, urgente := no):
        yield "sms: " + msg

canais := [spawn Email(), spawn Sms()]
assert [c.enviar("oi") cycle c in canais] is ["email: oi", "sms: oi"]
```

**Sobrecarga** (`overload`) escolhe variante por aridade e tipo; o tipo exato
vence o compatível, e empate é erro. **Operadores** vêm de `operator +` ou dos
métodos mágicos (`__add__`, `__radd__`, `__iadd__`, `__lt__`, `__getitem__`,
`__call__`…), e os de conversão (`__int__`, `__float__`, `__round__`,
`__hash__`, `__format__`) valem nos embutidos e na biblioteca.

---

## 4. Interfaces, abstração e contratos

```dataforge
contract Leitura<T>:
    action buscar(id: Integer) -> T

contract Repositorio<T> extends Leitura:
    action salvar(item: T)
    get total() -> Integer

blueprint Memoria with Repositorio:
    itens := []
    action buscar(id: Integer):
        yield self.itens[id] ?? void
    action salvar(item):
        expects item isnt void
        promises self.total is before(self.total) + 1
        self.itens.append(item)
    get total():
        yield len(self.itens)

m := spawn Memoria()
m.salvar("x")
assert m.buscar(0) is "x"
```

| Cláusula | Culpa | Erro |
|---|---|---|
| `expects` | quem chamou | `PreconditionError` |
| `promises` (com `outcome` e `before`) | a ação | `PostconditionError` |
| `invariant` | a operação pública que acabou de rodar | `InvariantError` |

---

## 5. Metaprogramação

| Recurso | Onde |
|---|---|
| metaclasse, com dez ganchos | `meta blueprint`, `using` — REFERENCIA §7.13 |
| interceptar leitura/escrita/chamada | `on_read`, `on_write`, `on_call`, `__getattribute__`, `__setattr__` |
| resolução dinâmica de atributo | `__getattr__`, `on_missing` |
| instanciação controlada | `on_spawn`, `__new__` |
| registro e validação de classes | `on_forge`, `on_extend` |
| decoradores e anotações | `@Nome`, lidos por `Arcane.Meta` e `Arcane.Reflexo` |
| criar método e tipo em execução | `Reflexo.definir_metodo`, `Reflexo.criar_blueprint`, `augment` |
| introspecção | `Reflexo.campos`, `metodos`, `modificadores`, `mro`, `herdeiros`, `anotacoes` |
| invocação dinâmica | `Reflexo.invocar`, `ler`, `escrever`, `instanciar` |

A regra que atravessa tudo: **metaprogramação passa pelas mesmas regras
que o código escrito**. `criar_blueprint` recusa mãe `final`; `definir_metodo`
recusa substituir; `augment` de outro arquivo não enxerga `private`; um
gancho de metaclasse não dispara outro.

---

## 6. Ciclo de vida, memória e concorrência

`spawn` percorre um caminho só: `on_spawn` → `__new__` → padrões dos campos
→ cabeçalho → `setup` → corpo solto → invariantes → `on_ready`. O objeto
morre quando o último nome o solta (contagem de referências do CPython) e
então roda `teardown`; ciclos esperam o coletor geracional.

- `Arcane.Memoria`: referência fraca, mapa fraco, `ao_descartar`,
  `coletar`, `vivos(Tipo)`, `tamanho(obj)`.
- `exclusive action`: uma thread por vez no objeto (monitor, reentrante).
- `Objetos.congelar`: imutável para sempre — seguro entre threads.
- `slots`: 64% menos memória por objeto.

---

## 7. SOLID, na linguagem e nas ferramentas

| Princípio | O que a linguagem oferece | O que as ferramentas conferem |
|---|---|---|
| **S** — responsabilidade única | blueprints pequenos, `record` para dado | `dataforge oop`: `god-blueprint`, `baixa-coesao` (LCOM), `metodo-longo` |
| **O** — aberto/fechado | contratos, polimorfismo, `augment`, metaclasse | `switch-de-tipo` |
| **L** — substituição | `override`, `invariant` herdada, `promises` | `check`: `substituicao-quebrada`; `oop`: `sobrescrita-que-recusa` |
| **I** — segregação | `contract A extends B` | `contrato-gordo` |
| **D** — inversão | contrato como tipo de parâmetro, `Arcane.Injecao` | `dependencia-concreta` |

`dataforge oop` também mede WMC, DIT, NOC, CBO, RFC, fan-in/fan-out,
instabilidade e índice de manutenibilidade, detecta dependência circular e
desenha o diagrama de classes (`--diagrama`).

---

## 8. Padrões e arquitetura

Os 23 padrões clássicos e onde cada um mora estão em
[/docs/oop/padroes](https://dataforge-lang.vercel.app/docs/oop/padroes).
Em resumo: Template Method, Strategy, Decorator, Iterator e Adapter são a
própria linguagem; Singleton, Pool, Builder, Prototype, Flyweight, Proxy,
Composite, Command, Chain, Specification, State, Memento, Visitor,
Observer e Mediator estão em `Arcane.Padroes`; Repository e o barramento de
comandos (CQRS) também. Arquitetura hexagonal é `contract` como porta,
`blueprint with` como adaptador e `Arcane.Injecao` na borda.

---

## 9. Testes de código orientado a objeto

- `Crucible.mock`, `spy` e `stub` como dublês; um contrato é o tipo que o
  dublê implementa.
- `c.valor(Contrato, duble)` troca a implementação no contêiner.
- `Padroes.repositorio()` é o repositório em memória para testar serviço.
- `Reflexo.cumpre(obj, Contrato)` e `Reflexo.faltando` são teste de contrato.
- `c.conferir()` resolve todas as dependências registradas num teste.

---

## 10. O mapa: tópico por tópico

Os tópicos são os do documento de requisitos de OOP. **✓** existe e é
conferido; **◐** existe em parte; **✗** não existe, com o motivo.

| # | Tópico | Estado | Onde |
|---|---|---|---|
| 1 | fundamentos: estado, identidade, referência, valor × referência | ✓ | `blueprint` × `record`; `is`; `Objetos.identico` |
| 2 | classes: construtores, estáticos, constantes, propriedades, aninhadas, finais, seladas, abstratas, genéricas, imutáveis | ✓ | §7.1–7.8 da referência |
| 2 | classe parcial | ✓ | `augment` |
| 3 | instanciação, cópia rasa/funda, clone, factory, pool, singleton, serialização | ✓ | `Objetos`, `Padroes` |
| 4 | encapsulamento, getters/setters, computed, read-only, invariantes | ✓ | modificadores, `get`/`set`, `lazy`, `invariant` |
| 4 | write-only | ✓ | propriedade só com `set` |
| 4 | `package` como visibilidade | ◐ | `internal` é por arquivo; não há visibilidade por pacote — um pacote do DataForge é uma pasta de arquivos, e o `relay` já define o que ele exporta |
| 5 | abstração, contratos, design por contrato | ✓ | `contract`, `expects`/`promises`/`invariant` |
| 6 | herança simples/multinível, `super`, final, diamante | ✓ | `extends`, `root`, C3 |
| 7 | polimorfismo de inclusão, paramétrico e ad-hoc; dispatch dinâmico | ✓ | sobrescrita, `<T>`, `overload` |
| 7 | covariância/contravariância declaradas | ✗ | a linguagem é de tipagem dinâmica e não tem generics de coleção (`Cluster<T>`); variância só faria sentido com eles |
| 7 | duck typing / structural typing | ✓ | chamada por protocolo; `Reflexo.cumpre` confere forma |
| 8 | interfaces: múltiplas, genéricas, compostas, verificação estática e em execução | ✓ | `contract … extends`, `with A, B`, `check` + declaração |
| 8 | default methods | ✓ | em `trait` (o contrato não tem corpo por decisão) |
| 9 | composição, agregação, delegação, ownership | ✓ | campos tipados; `Padroes.proxy`; `teardown` |
| 10 | public/private/protected/internal/static/abstract/final/sealed/override/readonly/async | ✓ | §7.8 |
| 10 | `virtual` | — | todo método já é virtual |
| 10 | `unsafe` / `native` | ✗ | não há memória manual; o nativo é `adopt Python.x` |
| 11 | métodos de instância, estáticos, de classe, abstratos, finais, assíncronos, genéricos, de extensão, de operador, de conversão; method references | ✓ | `action`, `static action`, `async action`, `augment`, `operator`, mágicos; um método é valor |
| 12 | construtores múltiplos/nomeados, lazy, pós-init, finalização, RAII, resource scopes | ✓ | `overload setup`, `static action`, `lazy get`, `on_ready`, `teardown`, `with`/`defer` |
| 13 | sobrecarga de métodos, construtores e operadores; ambiguidade | ✓ | `overload`, `AmbiguousOverloadError` |
| 13 | conversão implícita na sobrecarga | ◐ | só `Integer` → `Float`, a mesma regra das anotações |
| 14 | operadores em objetos: aritmética, comparação, índice, chamada, conversão, negação | ✓ | `operator`, 95 métodos mágicos |
| 15 | classes abstratas, template method | ✓ | `abstract blueprint` |
| 16 | traits, mixins, requisitos, múltiplos | ✓ | `trait`, `with A, B` |
| 16 | aliases e resolução explícita de conflito entre traits | ◐ | a ordem em `with` decide e o blueprint pode sobrescrever; não há sintaxe de alias |
| 17 | generics: classes, métodos, interfaces, constraints, inferência | ✓ | `<T>`, `<T extends X>` |
| 17 | lower bounds, especialização, generics de coleção | ✗ | ver §7 acima; `Cluster<T>` está no roadmap |
| 18 | nominal e estrutural, narrowing, optional, enums, records, aliases | ✓ | anotações, `?.`/`??`, `match`, `record`, `enum` |
| 18 | union e intersection types | ✗ | a anotação aceita um tipo; `Any` e `match` cobrem os casos |
| 19–20 | SOLID e princípios complementares | ✓ | §7 deste guia; `dataforge oop` |
| 21 | metaprogramação em execução | ✓ | §5 deste guia |
| 21 | macros e metaprogramação em compilação | ✗ | não há fase de compilação separada; metaclasse e decorador rodam na declaração, que é o equivalente |
| 22 | reflexão completa | ✓ | `Arcane.Reflexo` |
| 23–24 | metaclasses e hooks | ✓ | `meta blueprint`, dez ganchos |
| 25 | decorators de classe, método, propriedade, campo; empilhados; metadata | ✓ | `@Nome` |
| 25 | decorator de parâmetro | ✗ | o tipo do parâmetro já carrega o que um `@Inject` carregaria, e é o que o contêiner lê |
| 26 | descriptors, lazy, computed, validation, cached, read-only | ✓ | `__get__`/`__set__`, `lazy get`, `get` sem `set` |
| 27 | dispatch, vtables, callables, single dispatch | ✓ | `_achar_magico` com cache por blueprint; `__call__` |
| 27 | multiple dispatch | ◐ | `overload` despacha pelo tipo de todos os argumentos, no nível da ação |
| 28 | MRO, C3, conflitos | ✓ | `linhagem()` |
| 29 | objetos imutáveis, frozen, value objects | ✓ | `record`, `Objetos.congelar`, `readonly` |
| 30 | igualdade, hash, ordenação, contrato `eq`/`hash` | ✓ | `__eq__`/`__hash__`/`__lt__`/`__cmp__`, `Objetos.igual`/`hash`/`ordenar` |
| 31 | serialização JSON, schema, versão, ciclos, polimórfica, segurança | ✓ | `Objetos.para_vault`/`de_vault`, `$versao`, `on_deserialize` |
| 31 | YAML e binário de objetos | ◐ | `Arcane.Serialization` tem TOML/XML/CSV e pickle de dado; objeto polimórfico é JSON |
| 32–33 | injeção de dependência e IoC | ✓ | `Arcane.Injecao` |
| 34 | DDD: entity, value object, aggregate, repository, domain event, specification | ✓ | `blueprint`, `record`, `invariant`, `Padroes.repositorio`, `Arcane.Eventos`, `Padroes.especificacao` |
| 35–37 | padrões criacionais, estruturais e comportamentais | ✓ | §8 deste guia |
| 38 | padrões arquiteturais | ✓ | portas e adaptadores, CQRS (`Padroes.barramento`), `Kiln` para MVC |
| 38 | event sourcing como biblioteca | ✗ | é um padrão de persistência; `Arcane.Eventos` + `Arcane.Database` o compõem |
| 39 | eventos, observer, prioridade, filtro, cancelamento | ✓ | `Padroes.observavel`, `Arcane.Eventos` |
| 40 | OOP assíncrona, tasks, cancelamento, timeouts, retry | ✓ | `async action`, `await`, `retry`, `Arcane.Malha` |
| 40 | actor model | ◐ | `channel` + `thread` compõem; não há `actor` como palavra |
| 41 | objetos thread-safe, locks, monitor, atomic, imutáveis | ✓ | `exclusive`, `Arcane.Concurrent`, `congelar` |
| 42 | referências fracas/fortes, GC, finalização, pooling | ✓ | `Arcane.Memoria`, `teardown`, `Padroes.pool` |
| 43 | performance: dispatch, flyweight, pooling, profiling | ✓ | caminho rápido de acesso, `Padroes.compartilhado`, `dataforge profile` |
| 43 | escape analysis, inlining, especialização | ✗ | interpretador de árvore com compilação para fechamentos; ver CLAUDE.md "Bytecode" |
| 44 | testes: mocks, stubs, spies, fakes, contract tests, property-based | ✓ | `Crucible` |
| 44 | mutation testing | ✗ | não implementado |
| 45 | SOLID em APIs, CLI, ETL, bancos | ✓ | exemplos em `/docs/oop/padroes` e nos projetos |
| 46 | anti-patterns | ✓ | `dataforge oop` detecta treze |
| 47–48 | coesão, acoplamento, métricas | ✓ | `dataforge oop` |
| 49–52 | lexer, parser, AST, type checker, runtime | ✓ | ver "Onde está no código" |
| 49 | bytecode e VM | ✗ | ver CLAUDE.md |
| 53 | segurança: controle de reflexão, deserialização segura, pollution | ✓ | visibilidade na reflexão, lista de tipos em `de_vault`, `augment` sem porta dos fundos |
| 53 | sandbox de metaprogramação | ◐ | as regras valem para o código gerado; não há isolamento de processo |
| 54 | formatter, linter, analyzer, rename, find references, go to definition/implementation, type hierarchy, debugger, profiler, object inspector | ✓ | `fmt`, `lint`, `check`, LSP, `debug`/`dap`, `profile`, `Reflexo.inspecionar` |
| 54 | extract method / extract class | ✗ | não implementado no LSP |
| 55 | diagrama de classes, herança, dependência; doc de API | ✓ | `dataforge oop --diagrama`, `Reflexo.diagrama`, `dataforge doc` |
| 55 | object, package e architecture diagram | ✗ | não implementado |
| 57 | palavras reservadas | ✓ | treze **contextuais**, nenhuma reservada — cada palavra reservada tira um nome de quem escreve |
| 58 | biblioteca OOP | ✓ | `Arcane.Reflexo`, `Objetos`, `Injecao`, `Padroes`, `Memoria`, `Meta`, `Eventos`, `Concurrent` |

---

## 11. Onde está no código

| Camada | Arquivo |
|---|---|
| palavras contextuais | `dataforge/tokens.py` — `CONTEXTUAIS_BLUEPRINT` |
| sintaxe | `dataforge/parser.py` — `parse_blueprint`, `parse_membro_blueprint`, `parse_contract`, `parse_augment` |
| nós | `dataforge/ast_nodes.py` — `ContractDeclaration`, `AugmentDeclaration`, `InvariantStatement`, `ExpectsStatement`, `PromisesStatement`, `BeforeExpression` |
| execução | `dataforge/interpreter.py` — `exec_BlueprintDeclaration`, `_instanciar`, `_chamada_especial`, `_ler_da_instancia` |
| runtime fora do caminho quente | `dataforge/objetos.py` — sobrecarga, estado por objeto, vigias, ganchos |
| análise estática | `dataforge/typechecker.py` — `_conferir_oop`, `st_ContractDeclaration` |
| métricas | `dataforge/oop_analise.py` — `dataforge oop` |
| editor | `dataforge/lsp.py` — implementação e hierarquia de tipos |
| erros | `dataforge/catalogo_erros.py` — DF0917–DF0928, DF0319 |
| testes | `tests/test_oop_avancada.py`, `tests/test_magicos.py` |
| exercícios | `exercicios/21-oop-avancado/`, `exercicios/37-oop-sistema/` |
