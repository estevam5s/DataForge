// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "16 · Módulos e projetos",
  description: "7 exercícios: forge.toml, pacotes e organização.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 16`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[151](#151-modulos-com-adopt-e-relay)", "**Modulos com adopt e relay**", "importe um modulo local e comprove que relay controla o que sai."], ["[152](#152-imports-seletivos-e-apelidos)", "**Imports seletivos e apelidos**", "traga so os simbolos que voce usa, com o nome que preferir."], ["[153](#153-organizando-um-projeto)", "**Organizando um projeto**", "estruture codigo em modulos com responsabilidades separadas."], ["[154](#154-manifesto-e-ferramentas)", "**Manifesto e ferramentas**", "conheca o forge.toml e os comandos de projeto."], ["[155](#155-testes-automatizados)", "**Testes automatizados**", "escreva testes que o dataforge test descobre e executa."], ["[156](#156-projeto-biblioteca-completa)", "**Projeto: biblioteca completa**", "escreva um modulo publicavel com interface, testes e documentacao."], ["[157](#157-o-que-o-check-pega-atraves-do-adopt)", "**O que o 'check' pega ATRAVES do adopt**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "151 · Modulos com adopt e relay"},
  {"p": "**Enunciado.** importe um modulo local e comprove que relay controla o que sai."},
  { code: `// Importa o modulo inteiro sob um nome
adopt geometria as geo

out geo.PI
out $"circulo de raio 2: {round(geo.area_circulo(2), 4)}"
out $"retangulo 3x4: {geo.area_retangulo(3, 4)}"

assert round(geo.area_circulo(1), 5) is 3.14159, "area do circulo"
assert geo.area_retangulo(3, 4) is 12, "area do retangulo"

// O que nao esta no relay nao atravessa
escondido := no
monitor:
    out geo._arredondar(1.23456)
handle e:
    escondido := yes
    out $"bloqueado: {e.message}"

assert escondido is yes, "_arredondar nao foi exportado"

// Modulo inexistente dispara ImportError, nao devolve vazio
falhou := no
monitor:
    adopt Arcane.NaoExiste as x
    out x
handle e:
    falhou := yes
    out $"erro: {e.type}"

assert falhou is yes, "modulo inexistente dispara"

// A stdlib se importa do mesmo jeito
adopt Arcane.Math as Math
out $"sqrt(144) = {Math.sqrt(144)}"
assert Math.sqrt(144) is 12.0, "stdlib"`, lang: 'df', title: `exercicios/16-modulos-e-projetos/151_adopt_e_relay.df` },
  {"h3": "Conceitos"},
  {"p": "**Importar**"},
  { code: `adopt geometria as geo          // arquivo geometria.df ao lado
adopt Arcane.Math as Math       // biblioteca padrão`, lang: 'df' },
  {"p": "A resolução segue esta ordem:"},
  {"p": "1. módulos já carregados (cache — um arquivo só executa uma vez) 2. biblioteca padrão (`Arcane.*` e os nomes curtos) 3. arquivo `.df` **ao lado do arquivo que importa**"},
  {"p": "O terceiro ponto importa: o caminho é relativo ao arquivo, não ao diretório de onde você rodou o comando. Isso faz um projeto funcionar igual sendo executado da raiz ou de dentro de uma subpasta."},
  {"p": "**Exportar**"},
  { code: `relay PI, area_circulo, perimetro_circulo, area_retangulo`, lang: 'df' },
  {"p": "A regra tem dois casos:"},
  {"table": {"head": ["No módulo", "Exporta"], "rows": [["nenhum `relay`", "tudo do nível superior"], ["pelo menos um `relay`", "só o que foi listado"]]}},
  {"p": "Sem `relay`, você tem a conveniência de um script. Com `relay`, tem uma **interface pública** — e o que ficou de fora é detalhe de implementação que você pode reescrever sem quebrar ninguém."},
  {"h3": "Por que isso vale a pena"},
  {"p": "Em `geometria.df` existe uma ação `_arredondar` que não está no `relay`. Tentar usá-la falha:"},
  { code: `bloqueado: Vault has no key '_arredondar'`, lang: 'text' },
  {"p": "Essa é a diferença entre \"por convenção não use isso\" (o `_` do Python) e \"isso não está acessível\". A segunda é verificável."},
  {"h3": "Módulo inexistente"},
  { code: `adopt Arcane.NaoExiste as x
// ImportError_: Module 'Arcane.NaoExiste' not found. Available: ...`, lang: 'df' },
  {"p": "A mensagem lista o que existe. Antes do 4.0 isso devolvia um dicionário vazio e o erro só aparecia páginas adiante, como `NameError` — um dos bugs corrigidos nesta versão."},
  {"h3": "Saída esperada"},
  { code: `3.14159265
circulo de raio 2: 12.5664
retangulo 3x4: 12
bloqueado: Vault has no key '_arredondar'
erro: ImportError
sqrt(144) = 12.0`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Remova a linha `relay` de `geometria.df` e veja `_arredondar` ficar acessível.", "Crie `circulo.df` que importa `geometria` e reexporta só a parte de círculos."]},
  {"h2": "152 · Imports seletivos e apelidos"},
  {"p": "**Enunciado.** traga so os simbolos que voce usa, com o nome que preferir."},
  { code: `// Forma compacta: Modulo.{nomes}
adopt geometria.{area_circulo, PI}

out $"PI = {PI}"
out $"area = {round(area_circulo(1), 4)}"
assert round(area_circulo(1), 4) is 3.1416, "usado sem prefixo"

// Forma explicita, com apelido
adopt {realcar as destacar, linha} from textos

out destacar("titulo")
out linha("=", 24)
assert destacar("x") is "[x]", "apelido funciona"
assert linha("*", 3) is "***", "importado direto"

// Tambem vale para a stdlib
adopt Arcane.Math.{sqrt, factorial}
out $"sqrt(81) = {sqrt(81)}  5! = {factorial(5)}"
assert sqrt(81) is 9.0, "sqrt sem prefixo"
assert factorial(5) is 120, "factorial sem prefixo"

// Pedir um simbolo que o modulo nao exporta e erro claro
erro := ""
monitor:
    adopt geometria.{nao_existe}
handle e:
    erro := e.message
    out $"erro: {erro}"

assert "does not export" in erro, "a mensagem explica"
assert "area_circulo" in erro, "e lista o que existe"

// O modulo inteiro e o seletivo convivem
adopt geometria as geo
assert geo.PI is PI, "mesmo valor pelos dois caminhos"
out "os dois estilos coexistem"`, lang: 'df', title: `exercicios/16-modulos-e-projetos/152_imports_seletivos.df` },
  {"h3": "Conceitos"},
  {"p": "Três formas de importar, todas equivalentes em poder:"},
  { code: `adopt geometria as geo                        // o módulo inteiro
adopt geometria.{area_circulo, PI}            // seletivo, forma compacta
adopt {realcar as destacar} from textos       // seletivo, com apelido`, lang: 'df' },
  {"h3": "Quando usar cada uma"},
  {"table": {"head": ["Forma", "Boa para"], "rows": [["`as geo`", "módulo com muitos símbolos; o prefixo documenta a origem"], ["`.{a, b}`", "dois ou três símbolos usados o tempo todo"], ["`{a as b} from`", "resolver conflito de nomes"]]}},
  {"p": "O prefixo não é burocracia: `Math.sqrt(x)` diz de onde `sqrt` veio. Num arquivo que importa cinco módulos, isso é o que evita a pergunta \"onde é que isso está definido?\"."},
  {"p": "Use o seletivo quando a origem é óbvia pelo contexto e o prefixo só atrapalha."},
  {"h3": "Apelidos resolvem colisões"},
  { code: `adopt {realcar as destacar, linha} from textos`, lang: 'df' },
  {"p": "Se dois módulos exportam `formatar`, você não precisa renomear nada na origem — resolve no ponto de importação:"},
  { code: `adopt {formatar as formatar_data} from datas
adopt {formatar as formatar_moeda} from dinheiro`, lang: 'df' },
  {"h3": "Erro que ajuda"},
  {"p": "Pedir algo que o módulo não exporta:"},
  { code: `Module 'geometria' does not export: nao_existe.
It exports: PI, area_circulo, perimetro_circulo, area_retangulo`, lang: 'text' },
  {"p": "A mensagem lista o que existe. Quase sempre o problema é um nome digitado errado, e ver a lista resolve na hora — sem abrir o outro arquivo."},
  {"h3": "As formas convivem"},
  {"p": "Importar o módulo inteiro **e** símbolos soltos do mesmo módulo funciona. O arquivo só é executado uma vez (fica em cache), então `geo.PI` e `PI` são literalmente o mesmo valor."},
  {"h3": "Saída esperada"},
  { code: `PI = 3.14159265
area = 3.1416
[titulo]
========================
sqrt(81) = 9.0  5! = 120
erro: Module 'geometria' does not export: nao_existe. It exports: PI, area_circulo, perimetro_circulo, area_retangulo
os dois estilos coexistem`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Importe `sqrt` de `Arcane.Math` com o apelido `raiz`.", "Crie dois módulos que exportam o mesmo nome e resolva o conflito com apelidos."]},
  {"h2": "153 · Organizando um projeto"},
  {"p": "**Enunciado.** estruture codigo em modulos com responsabilidades separadas."},
  { code: `// Este exercicio demonstra a organizacao em camadas dentro de um so arquivo,
// para ser autocontido. Num projeto real cada secao seria um modulo.

// ═══ CAMADA 1: modelo — os dados e suas regras ═══

record Produto:
    codigo: String
    nome: String
    preco: Number
    estoque: Integer

    action valor_em_estoque():
        yield self.preco * self.estoque

    action disponivel():
        yield self.estoque bigger 0

enum Situacao:
    EmFalta
    Critico
    Normal

// ═══ CAMADA 2: regras de negocio — decisoes puras ═══

steady LIMITE_CRITICO := 5

action situacao_de(p: Produto) -> Situacao:
    given p.estoque is 0:
        yield Situacao.EmFalta
    orif p.estoque smaller LIMITE_CRITICO:
        yield Situacao.Critico
    yield Situacao.Normal

action precisa_repor(p: Produto) -> Boolean:
    yield situacao_de(p) isnt Situacao.Normal

// ═══ CAMADA 3: apresentacao — como isso vira texto ═══

action formatar_produto(p: Produto) -> String:
    marca := "!" given precisa_repor(p) otherwise " "
    yield $"{marca} {p.codigo.pad_end(6)}{p.nome.pad_end(14)}{str(p.estoque).pad_start(4)}  R$ {p.valor_em_estoque()}"

action cabecalho(titulo: String) -> String:
    yield $"{titulo}\\n{"-".repeat(len(titulo))}"

// ═══ CAMADA 4: aplicacao — junta tudo ═══

estoque := [
    Produto("P01", "Mouse", 80.0, 15),
    Produto("P02", "Teclado", 200.0, 3),
    Produto("P03", "Monitor", 1200.0, 0),
    Produto("P04", "Cabo", 25.0, 60)
]

out cabecalho("Inventario")
cycle p in estoque:
    out formatar_produto(p)

repor := estoque >> sift p: precisa_repor(p)
out ""
out cabecalho("Repor")
cycle p in repor:
    out $"  {p.nome}: {situacao_de(p).name}"

patrimonio := estoque >> morph p: p.valor_em_estoque() >> distill acc, v: acc + v 0
out ""
out $"patrimonio: R$ {patrimonio}"

assert len(repor) is 2, "teclado e monitor"
assert situacao_de(estoque[2]) is Situacao.EmFalta, "monitor esta zerado"
assert situacao_de(estoque[0]) is Situacao.Normal, "mouse ok"
assert patrimonio is 3300.0, "1200 + 600 + 0 + 1500"`, lang: 'df', title: `exercicios/16-modulos-e-projetos/153_organizacao_projeto.df` },
  {"h3": "As quatro camadas"},
  {"table": {"head": ["Camada", "Contém", "Depende de"], "rows": [["**Modelo**", "records, enums, invariantes", "nada"], ["**Regras**", "decisões de negócio", "modelo"], ["**Apresentação**", "como virar texto", "modelo, regras"], ["**Aplicação**", "orquestra o fluxo", "todas"]]}},
  {"p": "As setas apontam sempre para baixo. O modelo não sabe que existe apresentação; as regras não sabem se o resultado vira terminal, HTTP ou CSV."},
  {"h3": "Num projeto real"},
  {"p": "Cada camada é um módulo:"},
  { code: `src/
  modelo.df          record Produto, enum Situacao
  regras.df          situacao_de, precisa_repor
  apresentacao.df    formatar_produto, cabecalho
  main.df            junta tudo
tests/
  regras_test.df
forge.toml`, lang: 'text' },
  {"p": "E cada módulo declara sua interface:"},
  { code: `// regras.df
relay LIMITE_CRITICO, situacao_de, precisa_repor`, lang: 'df' },
  {"h3": "Por que separar"},
  {"p": "O critério prático é **o que muda junto**."},
  {"list": ["Trocar o limite de estoque crítico → mexe só em `regras.df`", "Trocar o terminal por uma página web → mexe só em `apresentacao.df`", "Acrescentar um campo ao produto → mexe em `modelo.df` e em quem usa o campo"]},
  {"p": "Quando tudo está num arquivo, qualquer mudança arrisca qualquer coisa."},
  {"h3": "Regras puras são testáveis"},
  { code: `action situacao_de(p: Produto) -> Situacao:
    given p.estoque is 0:
        yield Situacao.EmFalta
    ...`, lang: 'df' },
  {"p": "Essa ação não imprime, não lê arquivo, não consulta banco. O teste é uma linha:"},
  { code: `assert situacao_de(Produto("X", "Y", 1, 0)) is Situacao.EmFalta`, lang: 'df' },
  {"p": "Se ela também formatasse a saída, testá-la exigiria comparar strings — e mudar o formato quebraria o teste da regra."},
  {"h3": "O detalhe do ternário"},
  { code: `marca := "!" given precisa_repor(p) otherwise " "`, lang: 'df' },
  {"p": "Uma linha em vez de um `given`/`otherwise` de quatro. Vale para valores simples como este; para lógica maior, o bloco continua mais legível."},
  {"h3": "Saída esperada"},
  { code: `Inventario
----------
  P01   Mouse           15  R$ 1200.0
! P02   Teclado          3  R$ 600.0
! P03   Monitor          0  R$ 0.0
  P04   Cabo            60  R$ 1500.0

Repor
-----
  Teclado: Critico
  Monitor: EmFalta

patrimonio: R$ 3300.0`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Separe de verdade em quatro arquivos com `relay` e `adopt`.", "Acrescente uma camada de persistência com `Arcane.Database`.", "Escreva `tests/regras_test.df` cobrindo as três situações."]},
  {"h2": "154 · Manifesto e ferramentas"},
  {"p": "**Enunciado.** conheca o forge.toml e os comandos de projeto."},
  { code: `adopt Arcane.Serialization as Serde

// O forge.toml e o manifesto do projeto. Este exercicio monta um
// em memoria para mostrar sua estrutura.

manifesto := {
    "project": {
        "name": "meu-app",
        "version": "0.1.0",
        "description": "Exemplo de manifesto",
        "authors":["voce"],
        "license": "MIT",
        "entry": "src/main.df",
        "dataforge": ">=4.0"
    },
    "scripts": {
        "start": "run src/main.df",
        "test": "test tests/",
        "check": "check ."
    },
    "lint": {
        "strict": no,
        "ignore":["magic-number"]
    }
}

out Serde.to_toml(manifesto)

// Ler de volta preserva a estrutura
lido := Serde.from_toml(Serde.to_toml(manifesto))
assert lido["project"]["name"] is "meu-app", "roundtrip do nome"
assert lido["project"]["entry"] is "src/main.df", "roundtrip da entrada"

// Acesso por caminho pontuado
out ""
out $"nome:    {Serde.json_path(manifesto, "project.name")}"
out $"entrada: {Serde.json_path(manifesto, "project.entry")}"
out $"script:  {Serde.json_path(manifesto, "scripts.test")}"
out $"ausente: {Serde.json_path(manifesto, "project.homepage", "nao definido")}"

assert Serde.json_path(manifesto, "project.name") is "meu-app", "caminho"
assert Serde.json_path(manifesto, "x.y", "padrao") is "padrao", "fallback"

// Validar o manifesto antes de usar
action validar_manifesto(m):
    problemas := []
    given "project" not in m:
        problemas.append("falta a secao [project]")
        yield problemas
    projeto := m["project"]
    cycle campo in ["name", "version", "entry"]:
        given campo not in projeto:
            problemas.append($"falta project.{campo}")
    yield problemas

out ""
out $"validacao: {validar_manifesto(manifesto)}"
out $"incompleto: {validar_manifesto({"project": {"name": "x"}})}"

assert len(validar_manifesto(manifesto)) is 0, "manifesto completo"
assert len(validar_manifesto({"project": {"name": "x"}})) is 2, "faltam dois campos"`, lang: 'df', title: `exercicios/16-modulos-e-projetos/154_forge_toml.df` },
  {"h3": "O manifesto"},
  {"p": "`forge.toml` fica na raiz do projeto e descreve o que ele é:"},
  { code: `[project]
name = "meu-app"
version = "0.1.0"
entry = "src/main.df"
dataforge = ">=4.0"

[scripts]
start = "run src/main.df"
test = "test tests/"

[lint]
strict = false
ignore = ["magic-number"]`, lang: 'toml' },
  {"h3": "Criar e inspecionar"},
  { code: `dataforge init          # cria forge.toml, src/ e tests/
dataforge info          # mostra o manifesto e checa a versão`, lang: 'bash' },
  {"p": "O `info` avisa se o `dataforge = \">=4.0\"` não bate com a versão instalada — antes de você descobrir isso por um erro de sintaxe estranho."},
  {"h3": "O que o manifesto habilita"},
  {"p": "**Entrada padrão**"},
  { code: `dataforge run           # sem argumento: usa project.entry`, lang: 'bash' },
  {"p": "**Scripts nomeados**"},
  {"p": "Qualquer chave em `[scripts]` vira um comando:"},
  { code: `dataforge start         # roda "run src/main.df"
dataforge test          # roda "test tests/"`, lang: 'bash' },
  {"p": "Isso guarda o comando certo no repositório, em vez de num README que ninguém lê."},
  {"p": "**Raiz do projeto**"},
  {"p": "Comandos rodam a partir da pasta do `forge.toml`, não de onde você está. Rodar `dataforge test` de dentro de `src/` funciona igual."},
  {"h3": "O ciclo completo"},
  { code: `dataforge init                # começar
dataforge check src/          # nomes, tipos, aridade
dataforge lint src/           # estilo e higiene
dataforge fmt src/            # formatar
dataforge test tests/ -v      # testes
dataforge doc src/ --out=doc/API.md
dataforge run                 # executar`, lang: 'bash' },
  {"p": "Numa integração contínua, o conjunto vira:"},
  { code: `dataforge fmt . --check && dataforge check . && dataforge test`, lang: 'bash' },
  {"p": "Cada um sai com código diferente de zero em caso de falha."},
  {"h3": "TOML no seu próprio código"},
  {"p": "`Arcane.Serialization` lê e escreve TOML, útil para configuração da sua aplicação:"},
  { code: `config := Serde.from_toml(IO.read("config.toml"))
porta := Serde.json_path(config, "servidor.porta", 8080)`, lang: 'df' },
  {"p": "O terceiro argumento de `json_path` é o padrão quando o caminho não existe — mais direto que encadear `given` para cada nível."},
  {"h3": "Saída esperada"},
  { code: `name = "meu-app"
version = "0.1.0"
...

nome:    meu-app
entrada: src/main.df
script:  test tests/
ausente: nao definido

validacao: []
incompleto: [falta project.version, falta project.entry]`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Rode `dataforge init` numa pasta vazia e explore o que foi gerado.", "Adicione um script `fmt` e rode `dataforge fmt`.", "Escreva um validador de manifesto que também confere o formato da versão."]},
  {"h2": "155 · Testes automatizados"},
  {"p": "**Enunciado.** escreva testes que o dataforge test descobre e executa."},
  { code: `// Um arquivo cujo nome termina em _test.df, ou dentro de tests/, e descoberto
// automaticamente. Cada acao 'test_*' vira um caso.

// ── codigo sob teste ──

action fatorial(n: Integer) -> Integer:
    guard n bigger_eq 0, "fatorial exige n >= 0"
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)

action eh_primo(n: Integer) -> Boolean:
    given n smaller 2:
        yield no
    i := 2
    persist i * i smaller_eq n:
        given n % i is 0:
            yield no
        i += 1
    yield yes

record Conta:
    titular: String
    saldo: Number

action sacar(c: Conta, valor: Number) -> Conta:
    guard valor bigger 0, "valor precisa ser positivo"
    guard valor smaller_eq c.saldo, "saldo insuficiente"
    yield c with {"saldo": c.saldo - valor}

// ── casos de teste ──

action test_fatorial_casos_base():
    assert fatorial(0) is 1, "fatorial de 0"
    assert fatorial(1) is 1, "fatorial de 1"

action test_fatorial_cresce():
    assert fatorial(5) is 120, "fatorial de 5"
    assert fatorial(6) is 720, "fatorial de 6"

action test_fatorial_recusa_negativo():
    disparou := no
    monitor:
        fatorial(-1)
    handle e:
        disparou := yes
    assert disparou is yes, "negativo deve disparar"

action test_primos_conhecidos():
    cycle n in [2, 3, 5, 7, 11, 13]:
        assert eh_primo(n) is yes, $"{n} e primo"

action test_nao_primos():
    cycle n in [0, 1, 4, 9, 15, 100]:
        assert eh_primo(n) is no, $"{n} nao e primo"

action test_saque_reduz_saldo():
    c := Conta("Ana", 1000)
    depois := sacar(c, 300)
    assert depois.saldo is 700, "saldo apos saque"
    assert c.saldo is 1000, "o original nao muda"

action test_saque_acima_do_saldo():
    erro := ""
    monitor:
        sacar(Conta("Ana", 100), 500)
    handle e:
        erro := e.message
    assert erro is "saldo insuficiente", "mensagem do guard"

// ── executando manualmente, para este exercicio ser autocontido ──

casos := [
    ["fatorial_casos_base", test_fatorial_casos_base],
    ["fatorial_cresce", test_fatorial_cresce],
    ["fatorial_recusa_negativo", test_fatorial_recusa_negativo],
    ["primos_conhecidos", test_primos_conhecidos],
    ["nao_primos", test_nao_primos],
    ["saque_reduz_saldo", test_saque_reduz_saldo],
    ["saque_acima_do_saldo", test_saque_acima_do_saldo]
]

passaram := 0
falharam := 0
cycle caso in casos:
    nome, acao := caso
    monitor:
        acao()
        passaram += 1
        out $"  ok    {nome}"
    handle e:
        falharam += 1
        out $"  FALHA {nome}: {e.message}"

out ""
out $"{passaram} passaram, {falharam} falharam"
assert falharam is 0, "a suite deve estar verde"`, lang: 'df', title: `exercicios/16-modulos-e-projetos/155_testes_automatizados.df` },
  {"h3": "Descoberta automática"},
  {"p": "O runner encontra testes por convenção:"},
  {"table": {"head": ["Padrão", "Exemplo"], "rows": [["`*_test.df`", "`matematica_test.df`"], ["`test_*.df`", "`test_matematica.df`"], ["qualquer `.df` em `tests/`", "`tests/regras.df`"]]}},
  {"p": "Dentro do arquivo, **toda ação `test_*` é um caso**:"},
  { code: `action test_fatorial_casos_base():
    assert fatorial(0) is 1, "fatorial de 0"`, lang: 'df' },
  { code: `dataforge test              # tudo
dataforge test tests/ -v    # mostra cada caso
dataforge test --filter=primo
dataforge test --fail-fast`, lang: 'bash' },
  {"h3": "Ganchos opcionais"},
  {"table": {"head": ["Ação", "Roda"], "rows": [["`setup_all`", "uma vez, antes de tudo"], ["`setup`", "antes de cada caso"], ["`teardown`", "depois de cada caso"], ["`teardown_all`", "uma vez, no fim"]]}},
  {"h3": "Anatomia de um bom teste"},
  {"p": "**Nome que descreve o comportamento**, não a implementação:"},
  { code: `action test_saque_acima_do_saldo():        // bom
action test_sacar_2():                     // ruim`, lang: 'df' },
  {"p": "**Mensagem em cada assert.** Quando falha, é ela que você lê:"},
  { code: `assert depois.saldo is 700, "saldo apos saque"`, lang: 'df' },
  {"p": "**Um comportamento por caso.** Se um `test_tudo` falha, você não sabe qual das oito verificações quebrou."},
  {"h3": "Testando erros"},
  {"p": "O erro esperado é parte do contrato, e merece teste:"},
  { code: `action test_saque_acima_do_saldo():
    erro := ""
    monitor:
        sacar(Conta("Ana", 100), 500)
    handle e:
        erro := e.message
    assert erro is "saldo insuficiente", "mensagem do guard"`, lang: 'df' },
  {"p": "Note que o `assert` verifica a **mensagem**, não só que algo falhou. Isso pega o caso em que a ação falha pelo motivo errado."},
  {"h3": "Testando imutabilidade"},
  { code: `action test_saque_reduz_saldo():
    c := Conta("Ana", 1000)
    depois := sacar(c, 300)
    assert depois.saldo is 700, "saldo apos saque"
    assert c.saldo is 1000, "o original nao muda"`, lang: 'df' },
  {"p": "O segundo `assert` é o que garante que `sacar` não tem efeito colateral. Sem ele, uma implementação que mutasse o original passaria."},
  {"h3": "Cobrindo faixas"},
  { code: `action test_primos_conhecidos():
    cycle n in [2, 3, 5, 7, 11, 13]:
        assert eh_primo(n) is yes, $"{n} e primo"`, lang: 'df' },
  {"p": "Um laço dentro do teste cobre vários valores. A mensagem interpolada diz **qual** falhou."},
  {"h3": "Saída esperada"},
  { code: `  ok    fatorial_casos_base
  ok    fatorial_cresce
  ok    fatorial_recusa_negativo
  ok    primos_conhecidos
  ok    nao_primos
  ok    saque_reduz_saldo
  ok    saque_acima_do_saldo

7 passaram, 0 falharam`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Copie os casos para `tests/matematica_test.df` e rode `dataforge test`.", "Quebre `eh_primo` de propósito e veja o relatório com a linha da falha.", "Acrescente `setup` que prepara uma conta reaproveitada pelos casos."]},
  {"h2": "156 · Projeto: biblioteca completa"},
  {"p": "**Enunciado.** escreva um modulo publicavel com interface, testes e documentacao."},
  { code: `adopt Arcane.Text as Text

// ═══════════════════════════════════════════════════════════
//  VALIDADORES BR — uma biblioteca pequena e completa
//
//  Interface publica: validar_cpf, formatar_cpf, validar_cnpj,
//                     validar_email, validar_telefone
// ═══════════════════════════════════════════════════════════

// Guarda o resultado de uma validacao, com o motivo quando falha.
record Resultado:
    valido: Boolean
    motivo: String := ""

// Remove tudo que nao for digito.
action _so_digitos(texto: String) -> String:
    yield [c cycle c in texto given c.isdigit()].join("")

// Calcula um digito verificador de CPF.
action _digito_cpf(digitos: Cluster, peso_inicial: Integer) -> Integer:
    soma := 0
    peso := peso_inicial
    cycle d in digitos:
        soma += d * peso
        peso -= 1
    resto := (soma * 10) % 11
    yield 0 given resto is 10 otherwise resto

// Valida um CPF, com ou sem pontuacao.
action validar_cpf(cpf: String) -> Resultado:
    limpo := _so_digitos(cpf)
    given len(limpo) isnt 11:
        yield Resultado(no, $"esperava 11 digitos, veio {len(limpo)}")
    numeros := [cast c as Integer cycle c in limpo]
    given len(unique(numeros)) is 1:
        yield Resultado(no, "todos os digitos iguais")
    primeiro := _digito_cpf(numeros.slice(0, 9), 10)
    given primeiro isnt numeros[9]:
        yield Resultado(no, "primeiro digito verificador nao confere")
    segundo := _digito_cpf(numeros.slice(0, 10), 11)
    given segundo isnt numeros[10]:
        yield Resultado(no, "segundo digito verificador nao confere")
    yield Resultado(yes)

// Formata um CPF valido como 000.000.000-00.
action formatar_cpf(cpf: String) -> String:
    limpo := _so_digitos(cpf)
    guard len(limpo) is 11, "CPF precisa de 11 digitos"
    yield $"{limpo.slice(0, 3)}.{limpo.slice(3, 6)}.{limpo.slice(6, 9)}-{limpo.slice(9, 11)}"

// Valida um e-mail pela estrutura basica.
action validar_email(email: String) -> Resultado:
    texto := email.trim()
    given "@" not in texto:
        yield Resultado(no, "falta o @")
    partes := texto.split("@")
    given len(partes) isnt 2:
        yield Resultado(no, "mais de um @")
    given len(partes[0]) is 0:
        yield Resultado(no, "falta o usuario antes do @")
    given "." not in partes[1]:
        yield Resultado(no, "dominio sem ponto")
    yield Resultado(yes)

// Valida um telefone brasileiro (10 ou 11 digitos).
action validar_telefone(tel: String) -> Resultado:
    limpo := _so_digitos(tel)
    given len(limpo) smaller 10 or len(limpo) bigger 11:
        yield Resultado(no, $"esperava 10 ou 11 digitos, veio {len(limpo)}")
    given len(limpo) is 11 and limpo[2] isnt "9":
        yield Resultado(no, "celular deve comecar com 9 apos o DDD")
    yield Resultado(yes)

relay Resultado, validar_cpf, formatar_cpf, validar_email, validar_telefone

// ═══════════════════════════════════════════════════════════
//  DEMONSTRACAO
// ═══════════════════════════════════════════════════════════

out Text.box("Validadores BR")

out ""
out "── CPF ──"
cycle cpf in ["529.982.247-25", "52998224725", "111.111.111-11", "123", "529.982.247-26"]:
    r := validar_cpf(cpf)
    marca := "ok " given r.valido otherwise "nao"
    detalhe := formatar_cpf(cpf) given r.valido otherwise r.motivo
    out $"  {marca} {cpf.pad_end(16)} {detalhe}"

out ""
out "── e-mail ──"
cycle email in ["ana@exemplo.com", "sem-arroba", "@x.com", "a@b@c.com", "a@semponto"]:
    r := validar_email(email)
    out $"  {"ok " given r.valido otherwise "nao"} {email.pad_end(18)} {r.motivo}"

out ""
out "── telefone ──"
cycle tel in ["(48) 99999-1234", "4833334444", "(48) 8888-1234 5", "123"]:
    r := validar_telefone(tel)
    out $"  {"ok " given r.valido otherwise "nao"} {tel.pad_end(18)} {r.motivo}"

// ═══════════════════════════════════════════════════════════
//  TESTES
// ═══════════════════════════════════════════════════════════

action test_cpf_valido():
    assert validar_cpf("529.982.247-25").valido is yes, "com pontuacao"
    assert validar_cpf("52998224725").valido is yes, "sem pontuacao"

action test_cpf_invalido():
    assert validar_cpf("111.111.111-11").valido is no, "digitos repetidos"
    assert validar_cpf("529.982.247-26").valido is no, "verificador errado"
    assert validar_cpf("123").valido is no, "curto demais"

action test_cpf_explica_o_motivo():
    assert validar_cpf("123").motivo is "esperava 11 digitos, veio 3", "motivo"

action test_formatar():
    assert formatar_cpf("52998224725") is "529.982.247-25", "formatacao"

action test_email():
    assert validar_email("ana@exemplo.com").valido is yes, "valido"
    assert validar_email("sem-arroba").motivo is "falta o @", "sem arroba"
    assert validar_email("a@semponto").motivo is "dominio sem ponto", "dominio"

action test_telefone():
    assert validar_telefone("(48) 99999-1234").valido is yes, "celular"
    assert validar_telefone("4833334444").valido is yes, "fixo"
    assert validar_telefone("123").valido is no, "curto"

out ""
out Text.box("Testes")
casos := [
    ["cpf_valido", test_cpf_valido],
    ["cpf_invalido", test_cpf_invalido],
    ["cpf_explica_o_motivo", test_cpf_explica_o_motivo],
    ["formatar", test_formatar],
    ["email", test_email],
    ["telefone", test_telefone]
]
falhas := 0
cycle caso in casos:
    nome, acao := caso
    monitor:
        acao()
        out $"  ok    {nome}"
    handle e:
        falhas += 1
        out $"  FALHA {nome}: {e.message}"

out ""
out $"{len(casos) - falhas}/{len(casos)} testes passaram"
assert falhas is 0, "a biblioteca deve estar verde"`, lang: 'df', title: `exercicios/16-modulos-e-projetos/156_projeto_biblioteca.df` },
  {"h3": "A anatomia de uma biblioteca"},
  {"p": "Quatro partes, nesta ordem:"},
  {"p": "1. **Cabeçalho** — o que é e o que expõe 2. **Tipos** — os dados que atravessam a interface 3. **Implementação** — o interno (`_`) e o público 4. **`relay`** — a fronteira"},
  { code: `relay Resultado, validar_cpf, formatar_cpf, validar_email, validar_telefone`, lang: 'df' },
  {"p": "Tudo que não está nessa linha — `_so_digitos`, `_digito_cpf` — é detalhe de implementação. Você pode reescrevê-los amanhã sem quebrar ninguém."},
  {"h3": "Devolver o motivo, não só `no`"},
  {"p": "Esta é a decisão de desenho mais importante do exercício:"},
  { code: `record Resultado:
    valido: Boolean
    motivo: String := ""`, lang: 'df' },
  {"p": "Compare as duas interfaces:"},
  { code: `validar_cpf("123")           // no
validar_cpf("123")           // Resultado(no, "esperava 11 digitos, veio 3")`, lang: 'df' },
  {"p": "A primeira obriga quem chama a adivinhar o que está errado. A segunda pode ser mostrada ao usuário direto. O custo é um record; o ganho é toda a mensagem de erro que você não precisa escrever de novo em cada tela."},
  {"p": "O campo `motivo` tem valor padrão `\"\"`, então o caso de sucesso continua sendo `Resultado(yes)`."},
  {"h3": "Validar antes de formatar"},
  { code: `action formatar_cpf(cpf: String) -> String:
    limpo := _so_digitos(cpf)
    guard len(limpo) is 11, "CPF precisa de 11 digitos"
    yield $"{limpo.slice(0, 3)}.{...}"`, lang: 'df' },
  {"p": "O `guard` na entrada garante que a formatação nunca produz lixo. Uma função que formata dado inválido espalha o problema em vez de contê-lo."},
  {"h3": "Testes que cobrem os dois lados"},
  { code: `action test_cpf_valido():        // o que deve passar
action test_cpf_invalido():      // o que deve falhar
action test_cpf_explica_o_motivo():   // e por quê`, lang: 'df' },
  {"p": "O terceiro é o que muita suíte esquece: testar a **mensagem**. Sem ele, uma mudança que faz o validador rejeitar pelo motivo errado passa despercebida."},
  {"h3": "Publicando"},
  { code: `dataforge check validadores.df     # nomes e tipos
dataforge lint validadores.df      # estilo
dataforge test tests/              # suíte
dataforge doc validadores.df --out=doc/API.md`, lang: 'bash' },
  {"p": "O `doc` extrai os comentários acima de cada declaração — por isso vale escrevê-los como frases completas."},
  {"h3": "Saída esperada"},
  { code: `┌────────────────┐
│ Validadores BR │
└────────────────┘

── CPF ──
  ok  529.982.247-25   529.982.247-25
  ok  52998224725      529.982.247-25
  nao 111.111.111-11   todos os digitos iguais
  nao 123              esperava 11 digitos, veio 3
  nao 529.982.247-26   primeiro digito verificador nao confere
...
6/6 testes passaram`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente `validar_cnpj` seguindo o mesmo desenho.", "Separe em `validadores.df` e `tests/validadores_test.df` de verdade.", "Rode `dataforge doc` e veja a documentação que os comentários geraram."]},
  {"h2": "157 · O que o 'check' pega ATRAVES do adopt"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 157 — O que o 'check' pega ATRAVES do adopt
//
//  Num arquivo de 40 linhas, um erro aparece na primeira execucao.
//  Num sistema de 200 arquivos, a maioria das chamadas atravessa
//  modulo — e e ali que um erro sobrevive ate producao.
//
//  Este exercicio prova o que o analisador consegue provar antes de
//  rodar, e o que o faz calar. As duas metades importam: um falso
//  alarme ensina a ignorar mensagens.
// ════════════════════════════════════════════════════════════

adopt Arcane.OS as OS
adopt Arcane.IO as IO
adopt Arcane.Process as Proc

// ── Um projeto de dois modulos, escrito em disco ─────────────

// Uma subpasta PROPRIA, com nome unico.
//
// 'OS.temp_dir()' devolve a pasta temporaria do SISTEMA — compartilhada
// com todo processo da maquina. Escrever direto nela deixa lixo, e
// apaga-la no fim (a primeira versao deste exercicio fazia isso) seria
// destruir o temporario de todos os outros programas.
pasta := $"{OS.temp_dir()}/df-157-{randint(100000, 999999)}"
IO.mkdir(pasta)
IO.mkdir($"{pasta}/src")

IO.write($"{pasta}/src/loja.df", """record Produto:
    sku: String
    nome: String
    preco: Float

action criar(sku: String, nome: String) -> Produto:
    yield Produto(sku, nome, 0.0)

action com_preco(p: Produto, v: Float) -> Produto:
    yield p with {"preco": v}

action quantos() -> Integer:
    yield 0

action sem_tipo(x):
    yield x

relay Produto, criar, com_preco, quantos, sem_tipo
""")

// As mensagens saem em portugues: e o idioma padrao do runtime e do
// analisador. 'DF_IDIOMA=en' devolve o texto original, que e a forma que
// aparece nas buscas na internet.
action conferir(codigo):
    IO.write($"{pasta}/src/main.df", codigo)
    r := Proc.run(["dataforge", "check", $"{pasta}/src/main.df"])
    yield r["stdout"] + r["stderr"]

// ── 1. O campo errado, vindo de OUTRO arquivo ───────────────
//
// Isto depende do '-> Produto'. Uma acao que declara o retorno leva o
// tipo ATRAVES da fronteira, e o campo errado e acusado com sugestao.

saida := conferir("""adopt ./loja as L

p := L.criar("CAF", "Cafe")
out p.nomee
""")

assert "não tem o campo" in saida
assert "nomee" in saida
assert "quis dizer 'nome'" in saida

// ── 2. Aridade ──────────────────────────────────────────────

saida := conferir("""adopt ./loja as L

L.criar("CAF")
""")

assert "recebe 2 argumento" in saida
// E diz ONDE a acao foi declarada — no outro arquivo.
assert "loja.df" in saida

// ── 3. Simbolo que o modulo nao exporta ─────────────────────

saida := conferir("""adopt ./loja as L

L.apagar("CAF")
""")

assert "não tem 'apagar'" in saida
// A mensagem lista o que EXISTE: sem isso, a pessoa adivinha.
assert "criar" in saida

// ── 4. Tipo do argumento ────────────────────────────────────
//
// A aridade era conferida e o tipo nao: a superficie sabia QUANTOS
// argumentos, e nao O QUE cada um devia ser.

saida := conferir("""adopt ./loja as L

L.criar("CAF", 42)
""")

assert "espera String" in saida
assert "recebeu Integer" in saida

// ── 5. E DENTRO de uma acao, que e onde o codigo vive ───────
//
// A inferencia usa o escopo de QUEM CHAMA. Usar o escopo global fazia
// 'L.criar(sku, nome)' dentro de 'action f(sku, nome)' virar
// "Undefined name 'sku'" — 649 falsos alarmes num projeto de 252
// arquivos, um por cada uso de parametro numa chamada entre modulos.
//
// E os testes passavam: eles chamavam no nivel de topo, onde o escopo
// global e o certo.

saida := conferir("""adopt ./loja as L

action fazer(codigo: String, titulo: String):
    yield L.criar(codigo, titulo)

cycle i from 1 to 3:
    rotulo := $"item {i}"
    out L.criar(rotulo, rotulo).nome
""")

assert "sem erros" in saida

// E o erro de verdade, dentro da acao, continua sendo pego
saida := conferir("""adopt ./loja as L

action fazer(n: Integer):
    yield L.criar(n, "Cafe")
""")

assert "espera String" in saida
assert "recebeu Integer" in saida

// ── 6. O que o faz CALAR — e isto importa igual ─────────────
//
// Sem declaracao de tipo, nao ha o que provar. Inventar um tipo aqui
// daria o falso alarme que a politica proibe.

saida := conferir("""adopt ./loja as L

x := L.sem_tipo("qualquer coisa")
out x.campo_que_nao_existe
out L.sem_tipo(1), L.sem_tipo([1, 2])
""")

// 'sem erros' contem a palavra 'erro': conferir a ausencia dela
// contradiz a linha de baixo. O que importa e a AUSENCIA de
// diagnostico, e a saida do 'check' limpo diz "sem erros".
assert "sem erros" in saida

// ── 7. O codigo certo nao gera alarme nenhum ────────────────

saida := conferir("""adopt ./loja as L

p := L.criar("CAF", "Cafe")
out p.sku, p.nome, p.preco

q := L.com_preco(p, 29.9)
out q.preco

// um Integer serve onde se espera Float, como em toda a linguagem
r := L.com_preco(p, 30)
out r.preco

out L.quantos() + 1
""")

assert "sem erros" in saida

// ── 8. E um erro dentro do modulo IMPORTADO faz o check calar ─
//
// Um arquivo que nao compila e problema DELE, e o 'check' sobre ele
// vai dizer isso. Acusar o uso de um simbolo porque o outro arquivo
// esta quebrado seria culpar o inocente.

IO.write($"{pasta}/src/quebrado.df", "action f(:\\n")
saida := conferir("""adopt ./quebrado as Q

Q.qualquer_coisa(1, 2, 3)
""")

// Nao acusa a chamada: a superficie de um arquivo que nao compila
// fica ABERTA, e o analisador volta a calar.
assert "não tem" not in saida

IO.remove_tree(pasta)
out "157 ok — o check atravessa o adopt"`, lang: 'df', title: `exercicios/16-modulos-e-projetos/157_check_entre_modulos.df` },
  {"h3": "Por que isto é o que mais importa em escala"},
  {"p": "Num arquivo de 40 linhas, um erro aparece na primeira execução. Num sistema de 200 arquivos, **a maioria das chamadas atravessa módulo** — e é ali que um erro sobrevive até produção."},
  {"p": "O `check` lê o outro `.df` com o lexer e o parser, e **nunca o executa**: analisar não pode ter efeito colateral."},
  {"h3": "As quatro coisas que ele prova"},
  { code: `adopt ./loja as L

p := L.criar("CAF", "Cafe")

out p.nomee              // has no field 'nomee' — Did you mean 'nome'?
L.criar("CAF")           // takes 2 argument(s), got 1
L.apagar("CAF")          // module 'L' has no 'apagar'
L.criar("CAF", 42)       // 'nome' expects String but got Integer`, lang: 'df' },
  {"p": "O primeiro e o quarto **dependem das declarações de tipo**:"},
  {"table": {"head": ["No módulo importado", "Dá ao analisador"], "rows": [["`action criar(…) -> Produto`", "o tipo do valor que volta, e com ele os campos"], ["`action criar(sku: String, …)`", "o que cada argumento deve ser"]]}},
  {"p": "Sem elas, o analisador cala — ele só acusa o que consegue **provar**."},
  {"p": "É isso que torna a anotação de tipo valer a pena. Num arquivo só, ela documenta. Atravessando módulo, ela é a diferença entre um erro achado em 0,4 s e um erro achado em produção."},
  {"h3": "Dentro de uma ação — onde o código vive"},
  {"p": "A inferência de tipo usa o escopo de **quem chama**. Usar o escopo global fazia `L.criar(sku, nome)` dentro de `action f(sku, nome)` virar **\"Undefined name 'sku'\"** — 649 falsos alarmes num projeto gerado de 252 arquivos, um por cada uso de parâmetro numa chamada entre módulos."},
  {"p": "E os testes passavam: eles chamavam no **nível de topo**, onde o escopo global é o certo. O bug só aparecia dentro de uma ação."},
  {"p": "Quem pegou foi rodar o `check` no projeto grande. É a mesma lição de sempre: comparar contra uma fonte de verdade, não reler o código."},
  {"h3": "O que o faz calar, e por que isso importa igual"},
  { code: `x := L.sem_tipo("qualquer coisa")   // 'action sem_tipo(x)' — sem tipo
out x.campo_que_nao_existe          // passa, e está certo passar`, lang: 'df' },
  {"p": "Um falso alarme ensina a ignorar mensagens — e aí os verdadeiros também são ignorados. A calibragem atual é **zero erros** em 333 arquivos conhecidamente bons do repositório."},
  {"p": "Ele também cala **inteiro** quando a superfície do outro arquivo não é confiável:"},
  {"table": {"head": ["Cala quando", "Porque"], "rows": [["o outro arquivo **não compila**", "é problema dele, e o `check` sobre ele vai dizer isso"], ["há **ciclo de import**", "seguir entraria em laço"], ["a profundidade (4 níveis) acaba", "o custo cresce e o ganho não"], ["o `relay` nomeia algo calculado", "o conteúdo só existe em execução"]]}},
  {"p": "O item 7 do exercício prova o primeiro: um `adopt` de um arquivo quebrado, seguido de uma chamada inventada, **não é acusado**. Acusar ali seria culpar o inocente."},
  {"h3": "A armadilha de `OS.temp_dir()`"},
  {"p": "Este exercício escreve arquivos para conferir o `check`, e a primeira versão fazia isto:"},
  { code: `pasta := OS.temp_dir()      // a pasta do SISTEMA
…
IO.remove_tree(pasta)       // apaga o temporário de TODOS os processos`, lang: 'df' },
  {"p": "`OS.temp_dir()` devolve `/var/folders/…/T` — compartilhada com toda a máquina. Escrever direto nela deixa lixo; apagá-la no fim destrói o temporário dos outros programas. O certo é uma subpasta com nome único:"},
  { code: `pasta := $"{OS.temp_dir()}/df-157-{randint(100000, 999999)}"
IO.mkdir(pasta)`, lang: 'df' },
  {"h3": "Rodar o `check` de dentro de um `.df`"},
  { code: `adopt Arcane.Process as Proc

r := Proc.run(["dataforge", "check", caminho])
saida := r["stdout"] + r["stderr"]`, lang: 'df' },
  {"p": "`Proc.run` devolve um vault com `stdout`, `stderr` e `code`. Note que `\"sem erros\"` **contém** a palavra `erro` — conferir a ausência dela contradiz a conferência do sucesso, e foi o que a primeira versão deste exercício fez."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/16-modulos-e-projetos/151_adopt_e_relay.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '151-modulos-com-adopt-e-relay', text: "151 · Modulos com adopt e relay", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'por-que-isso-vale-a-pena', text: "Por que isso vale a pena", level: 3 as const }, { id: 'modulo-inexistente', text: "Módulo inexistente", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '152-imports-seletivos-e-apelidos', text: "152 · Imports seletivos e apelidos", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'quando-usar-cada-uma', text: "Quando usar cada uma", level: 3 as const }, { id: 'apelidos-resolvem-colisoes', text: "Apelidos resolvem colisões", level: 3 as const }, { id: 'erro-que-ajuda', text: "Erro que ajuda", level: 3 as const }, { id: 'as-formas-convivem', text: "As formas convivem", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '153-organizando-um-projeto', text: "153 · Organizando um projeto", level: 2 as const }, { id: 'as-quatro-camadas', text: "As quatro camadas", level: 3 as const }, { id: 'num-projeto-real', text: "Num projeto real", level: 3 as const }, { id: 'por-que-separar', text: "Por que separar", level: 3 as const }, { id: 'regras-puras-sao-testaveis', text: "Regras puras são testáveis", level: 3 as const }, { id: 'o-detalhe-do-ternario', text: "O detalhe do ternário", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '154-manifesto-e-ferramentas', text: "154 · Manifesto e ferramentas", level: 2 as const }, { id: 'o-manifesto', text: "O manifesto", level: 3 as const }, { id: 'criar-e-inspecionar', text: "Criar e inspecionar", level: 3 as const }, { id: 'o-que-o-manifesto-habilita', text: "O que o manifesto habilita", level: 3 as const }, { id: 'o-ciclo-completo', text: "O ciclo completo", level: 3 as const }, { id: 'toml-no-seu-proprio-codigo', text: "TOML no seu próprio código", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '155-testes-automatizados', text: "155 · Testes automatizados", level: 2 as const }, { id: 'descoberta-automatica', text: "Descoberta automática", level: 3 as const }, { id: 'ganchos-opcionais', text: "Ganchos opcionais", level: 3 as const }, { id: 'anatomia-de-um-bom-teste', text: "Anatomia de um bom teste", level: 3 as const }, { id: 'testando-erros', text: "Testando erros", level: 3 as const }, { id: 'testando-imutabilidade', text: "Testando imutabilidade", level: 3 as const }, { id: 'cobrindo-faixas', text: "Cobrindo faixas", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '156-projeto-biblioteca-completa', text: "156 · Projeto: biblioteca completa", level: 2 as const }, { id: 'a-anatomia-de-uma-biblioteca', text: "A anatomia de uma biblioteca", level: 3 as const }, { id: 'devolver-o-motivo-nao-so-no', text: "Devolver o motivo, não só `no`", level: 3 as const }, { id: 'validar-antes-de-formatar', text: "Validar antes de formatar", level: 3 as const }, { id: 'testes-que-cobrem-os-dois-lados', text: "Testes que cobrem os dois lados", level: 3 as const }, { id: 'publicando', text: "Publicando", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '157-o-que-o-check-pega-atraves-do-adopt', text: "157 · O que o 'check' pega ATRAVES do adopt", level: 2 as const }, { id: 'por-que-isto-e-o-que-mais-importa-em-escala', text: "Por que isto é o que mais importa em escala", level: 3 as const }, { id: 'as-quatro-coisas-que-ele-prova', text: "As quatro coisas que ele prova", level: 3 as const }, { id: 'dentro-de-uma-acao-onde-o-codigo-vive', text: "Dentro de uma ação — onde o código vive", level: 3 as const }, { id: 'o-que-o-faz-calar-e-por-que-isso-importa-igual', text: "O que o faz calar, e por que isso importa igual", level: 3 as const }, { id: 'a-armadilha-de-ostempdir', text: "A armadilha de `OS.temp_dir()`", level: 3 as const }, { id: 'rodar-o-check-de-dentro-de-um-df', text: "Rodar o `check` de dentro de um `.df`", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"16 · Módulos e projetos"}
      description={"7 exercícios: forge.toml, pacotes e organização."}
      href={"/docs/exercicios/16-modulos-e-projetos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
