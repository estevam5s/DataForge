// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "11 · Tipos e checagem",
  description: "6 exercícios: anotações, o analisador estático e generics.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 11`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[121](#121-anotacoes-de-tipo)", "**Anotacoes de tipo**", "declare variaveis com tipo e comprove que o valor errado e recusado."], ["[122](#122-acoes-com-tipos)", "**Acoes com tipos**", "anote parametros e retorno, e veja o erro apontar o parametro exato."], ["[123](#123-typeof-e-conversao)", "**typeof e conversao**", "descubra o tipo de qualquer valor e converta entre tipos com seguranca."], ["[124](#124-analise-estatica)", "**Analise estatica**", "escreva erros de proposito e confirme que o dataforge check os encontra."], ["[125](#125-tipos-dentro-de-colecoes)", "**Tipos dentro de colecoes**", "combine anotacoes com listas e dicionarios, e valide o conteudo."], ["[126](#126-tipagem-gradual-com-any)", "**Tipagem gradual com Any**", "use Any quando o tipo depende do uso, e estreite depois com typeof."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "121 · Anotacoes de tipo"},
  {"p": "**Enunciado.** declare variaveis com tipo e comprove que o valor errado e recusado."},
  { code: `// Tipos simples
idade: Integer := 30
nome: String := "Ana"
altura: Float := 1.72
ativo: Boolean := yes
notas: Cluster := [8, 9, 10]
config: Vault := {"tema": "escuro"}

out idade, nome, altura, ativo
out notas, config

// Integer serve onde se espera Float — a conversao e segura
media: Float := 8

// O contrario nao vale
recusou := no
monitor:
    quantidade: Integer := 3.5
handle e:
    recusou := yes
    out "recusado:", e.message

assert recusou is yes, "Float nao entra onde se espera Integer"
assert media is 8, "Integer entra onde se espera Float"
assert typeof(idade) is "Integer", "tipo de idade"
assert typeof(config) is "Vault", "tipo de config"`, lang: 'df', title: `exercicios/11-tipos-e-checagem/121_anotacoes_basicas.df` },
  {"h3": "Conceitos"},
  {"p": "Uma anotação em DataForge tem a forma `nome: Tipo := valor`. Ela é **opcional** — o código funciona sem ela — mas quando presente é **verificada**: tanto pelo analisador estático (`dataforge check`) quanto no momento da atribuição."},
  {"table": {"head": ["Tipo", "Aceita"], "rows": [["`Integer`", "inteiros"], ["`Float`", "decimais **e** inteiros"], ["`Number`", "inteiros ou decimais"], ["`String`", "textos"], ["`Boolean`", "`yes` / `no`"], ["`Cluster`", "listas"], ["`Vault`", "dicionários"], ["`Void`", "apenas `void`"], ["`Any`", "qualquer coisa (desliga a checagem)"], ["*nome de record/blueprint/enum*", "instâncias daquele tipo"]]}},
  {"h3": "A regra de conversão"},
  {"p": "Há uma única flexibilização, e ela existe porque é matematicamente segura:"},
  { code: `media: Float := 8        // ok: todo inteiro é um decimal válido
quantidade: Integer := 3.5   // erro: 3.5 não é inteiro`, lang: 'df' },
  {"p": "Um `Integer` entra onde se espera `Float`. O contrário perderia informação, e por isso é recusado."},
  {"h3": "Passo a passo"},
  {"p": "1. Cada declaração associa um tipo ao nome. 2. `media: Float := 8` passa pela regra de alargamento acima. 3. O bloco `monitor` captura a violação para que o programa siga. 4. Os `assert` confirmam o comportamento nos dois sentidos."},
  {"h3": "Saída esperada"},
  { code: `30 Ana 1.72 yes
[8, 9, 10] {tema: escuro}
recusado: variable 'quantidade' declared as Integer but got Float`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Troque `notas: Cluster := [8, 9, 10]` por `notas: Vault := [8, 9, 10]`.", "Rode `dataforge check` neste arquivo: o erro aparece **antes** de executar.", "Anote com `Any` e veja a checagem desaparecer."]},
  {"h2": "122 · Acoes com tipos"},
  {"p": "**Enunciado.** anote parametros e retorno, e veja o erro apontar o parametro exato."},
  { code: `action area_retangulo(largura: Number, altura: Number) -> Float:
    yield largura * altura * 1.0

action saudar(nome: String, vezes: Integer := 1) -> String:
    yield(nome + " ").repeat(vezes).trim()

action primeiro_item(itens: Cluster) -> Any:
    given len(itens) is 0:
        yield void
    yield itens[0]

out area_retangulo(3, 4)
out saudar("oi", 3)
out primeiro_item([10, 20]), primeiro_item([])

// O erro nomeia o parametro
erro := ""
monitor:
    area_retangulo("tres", 4)
handle e:
    erro := e.message
    out erro

assert area_retangulo(3, 4) is 12.0, "area"
assert saudar("oi", 2) is "oi oi", "repeticao"
assert primeiro_item([]) is void, "lista vazia devolve void"
assert "largura" in erro, "a mensagem nomeia o parametro errado"`, lang: 'df', title: `exercicios/11-tipos-e-checagem/122_acoes_tipadas.df` },
  {"h3": "Conceitos"},
  {"p": "A forma completa de uma ação tipada:"},
  { code: `action nome(param: Tipo, outro: Tipo := padrao) -> TipoDeRetorno:
    yield valor`, lang: 'df' },
  {"p": "Três coisas passam a ser verificadas:"},
  {"p": "1. **Cada parâmetro** é checado no momento da chamada. 2. **O valor devolvido** é checado no `yield`. 3. **O analisador estático** avisa se a ação declara um retorno mas pode terminar sem `yield`."},
  {"h3": "Por que a mensagem importa"},
  {"p": "Compare as duas formas de errar:"},
  { code: `TypeError_: unsupported operand type(s) for *: 'str' and 'int'`, lang: 'text' },
  {"p": "contra o que o DataForge diz:"},
  { code: `parameter 'largura' of action 'area_retangulo' declared as Number but got String`, lang: 'text' },
  {"p": "A segunda diz **onde** e **o quê**. É por isso que a checagem acontece na fronteira da ação, e não lá dentro quando a conta explode."},
  {"h3": "O tipo `Any`"},
  {"p": "`primeiro_item(itens: Cluster) -> Any` declara honestamente que o retorno depende do conteúdo da lista. Usar `Any` é melhor que mentir um tipo específico."},
  {"h3": "Saída esperada"},
  { code: `12.0
oi oi oi
10 void
parameter 'largura' of action 'area_retangulo' declared as Number but got String`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Mude o retorno para `-> Integer` e veja o erro no `yield`.", "Remova o `yield void` do caminho da lista vazia e rode `dataforge check`."]},
  {"h2": "123 · typeof e conversao"},
  {"p": "**Enunciado.** descubra o tipo de qualquer valor e converta entre tipos com seguranca."},
  { code: `record Ponto:
    x: Integer
    y: Integer

enum Cor:
    Vermelho
    Verde

stream action contador():
    emit 1

valores := [42, 3.14, "texto", yes, void, [1], {"k":1}, Ponto(1, 2), Cor.Verde]

cycle v in valores:
    out $"{typeof(v)}"

assert typeof(42) is "Integer", "Integer"
assert typeof(3.14) is "Float", "Float"
assert typeof("texto") is "String", "String"
assert typeof(yes) is "Boolean", "Boolean"
assert typeof(void) is "Void", "Void"
assert typeof([1]) is "Cluster", "Cluster"
assert typeof({"k": 1}) is "Vault", "Vault"
assert typeof(Ponto(1, 2)) is "Ponto", "record devolve o proprio nome"
assert typeof(Cor.Verde) is "Cor", "membro de enum devolve o nome do enum"
assert typeof(contador()) is "Stream", "Stream"

// Conversao explicita
assert cast "42" as Integer is 42, "texto para inteiro"
assert cast 3.9 as Integer is 3, "decimal trunca"
assert cast 42 as String is "42", "inteiro para texto"
assert cast "3.5" as Float is 3.5, "texto para decimal"

// Conversao impossivel dispara
falhou := no
monitor:
    cast "abc" as Integer
handle e:
    falhou := yes
assert falhou is yes, "texto sem numero nao converte"

out "conversoes verificadas"`, lang: 'df', title: `exercicios/11-tipos-e-checagem/123_typeof_e_cast.df` },
  {"h3": "Conceitos"},
  {"p": "**`typeof`**"},
  {"p": "`typeof x` devolve **o mesmo nome que você usaria numa anotação**. Isso não é detalhe: significa que estas duas linhas falam a mesma língua."},
  { code: `idade: Integer := 30
out typeof(idade)        // Integer`, lang: 'df' },
  {"p": "Para tipos que você define, `typeof` devolve o nome que você deu:"},
  {"table": {"head": ["Valor", "`typeof`"], "rows": [["`Ponto(1, 2)`", "`\"Ponto\"`"], ["`Cor.Verde`", "`\"Cor\"` (o enum, não o membro)"], ["`contador()`", "`\"Stream\"`"]]}},
  {"p": "**`cast`**"},
  {"p": "`cast valor as Tipo` converte explicitamente."},
  { code: `cast "42" as Integer     // 42
cast 3.9 as Integer      // 3     — trunca, não arredonda
cast "abc" as Integer    // erro`, lang: 'df' },
  {"p": "Note que `cast 3.9 as Integer` dá `3`, não `4`. Truncar é a regra; para arredondar use `round(3.9)`."},
  {"h3": "Passo a passo"},
  {"p": "1. O `cycle` percorre um valor de cada tipo e imprime seu nome. 2. Os `assert` fixam o contrato de `typeof` para todos os tipos. 3. A última parte confirma que uma conversão impossível dispara erro em vez de devolver lixo silenciosamente."},
  {"h3": "Saída esperada"},
  { code: `Integer
Float
String
Boolean
Void
Cluster
Vault
Ponto
Cor
conversoes verificadas`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["`out typeof(typeof(1))` — o que sai, e por quê?", "Compare `cast 3.9 as Integer` com `round(3.9)`."]},
  {"h2": "124 · Analise estatica"},
  {"p": "**Enunciado.** escreva erros de proposito e confirme que o dataforge check os encontra."},
  { code: `// Este arquivo roda sem erros. Os problemas que o analisador encontraria
// estao descritos abaixo, em comentarios, para voce reproduzir.

action somar(a: Integer, b: Integer) -> Integer:
    yield a + b

steady LIMITE := 100

out somar(2, 3)
out LIMITE

// Cada linha abaixo, se descomentada, e apontada por 'dataforge check':
//
//   somar(1)              -> action 'somar' is missing argument(s): b
//   somar(1, 2, 3)        -> action 'somar' takes 2 argument(s) but 3 were given
//   somar("x", 2)         -> parameter 'a' expects Integer but got String
//   sommar(1, 2)          -> undefined action 'sommar'  (sugere 'somar')
//   LIMITE := 200         -> cannot reassign the steady constant 'LIMITE'
//   x: Intger := 1        -> unknown type 'Intger'      (sugere 'Integer')
//   out 1 + [2]           -> cannot add Integer and Cluster

// O que o analisador NAO impede: erros que so existem em tempo de execucao.
divisor := 0
monitor:
    out 10 / divisor
handle e:
    out "isso so aparece rodando:", e.message

assert somar(2, 3) is 5, "soma"
out "rode 'dataforge check' neste arquivo: zero erros"`, lang: 'df', title: `exercicios/11-tipos-e-checagem/124_checagem_estatica.df` },
  {"h3": "Conceitos"},
  {"p": "`dataforge check` roda três etapas sem executar uma linha do seu programa:"},
  {"p": "1. **Léxica** — o arquivo é um DataForge válido? 2. **Sintática** — a estrutura faz sentido? 3. **Semântica** — os nomes existem? as chamadas batem? os tipos combinam?"},
  { code: `dataforge check meu_programa.df
dataforge check src/ --strict     # avisos também falham`, lang: 'bash' },
  {"h3": "O que ele encontra"},
  {"table": {"head": ["Categoria", "Exemplo"], "rows": [["nome indefinido", "`sommar(1, 2)` → *sugere `somar`*"], ["aridade", "`somar(1)` → falta `b`"], ["tipo de argumento", "`somar(\"x\", 2)`"], ["tipo de variável", "`x: Integer := \"texto\"`"], ["tipo inexistente", "`x: Intger := 1` → *sugere `Integer`*"], ["constante reatribuída", "`LIMITE := 200`"], ["operador incompatível", "`1 + [2]`"], ["campo de record", "`p.emial`"], ["membro de enum", "`Status.Cancelado`"], ["código inalcançável", "linha após `yield`"], ["retorno ausente", "`-> Integer` sem `yield`"]]}},
  {"h3": "O que ele NÃO encontra"},
  {"p": "O analisador é **deliberadamente otimista**: quando não consegue provar que algo está errado, fica calado. Um falso alarme atrapalha mais do que um alerta perdido, porque ensina a ignorar as mensagens."},
  {"p": "Por isso, isto passa no `check` e falha ao rodar:"},
  { code: `divisor := 0
out 10 / divisor      // o valor só é conhecido em tempo de execução`, lang: 'df' },
  {"h3": "Erros dentro de `monitor`"},
  {"p": "Código dentro de um `monitor:` existe justamente para conter falhas. Por isso o analisador **rebaixa erros a avisos** ali dentro — provocar uma falha de propósito é legítimo."},
  {"h3": "Experimente"},
  {"p": "1. Descomente uma das linhas listadas no arquivo. 2. Rode `dataforge check 124_checagem_estatica.df`. 3. Repare que a mensagem traz linha, coluna e uma sugestão."},
  {"h2": "125 · Tipos dentro de colecoes"},
  {"p": "**Enunciado.** combine anotacoes com listas e dicionarios, e valide o conteudo."},
  { code: `adopt Arcane.Collections as Col

// A anotacao cobre o recipiente; o conteudo se valida com codigo
notas: Cluster := [7.5, 8.0, 9.5]
alunos: Vault := {"ana": 9.5, "bruno": 7.0}

action media(valores: Cluster) -> Float:
    given len(valores) is 0:
        yield 0.0
    yield sum(valores) / len(valores)

action todos_numeros(valores: Cluster) -> Boolean:
    cycle v in valores:
        given typeof(v) isnt "Integer" and typeof(v) isnt "Float":
            yield no
    yield yes

out $"media das notas: {round(media(notas), 2)}"
out $"so numeros? {todos_numeros(notas)}"
out $"e com texto? {todos_numeros([1, "dois"])}"

// Validando um vault campo a campo
action validar_aluno(dados: Vault) -> Cluster:
    problemas := []
    given "nome" not in dados:
        problemas.append("falta o nome")
    orif typeof(dados["nome"]) isnt "String":
        problemas.append("nome deve ser String")
    given "nota" not in dados:
        problemas.append("falta a nota")
    orif typeof(dados["nota"]) is "String":
        problemas.append("nota deve ser numero")
    yield problemas

out validar_aluno({"nome": "Ana", "nota": 9.5})
out validar_aluno({"nota": "dez"})

assert todos_numeros(notas) is yes, "notas sao numeros"
assert len(validar_aluno({"nome": "Ana", "nota": 9.5})) is 0, "aluno valido"
assert len(validar_aluno({"nota": "dez"})) is 2, "dois problemas"
assert round(media(notas), 2) is 8.33, "media"`, lang: 'df', title: `exercicios/11-tipos-e-checagem/125_tipos_em_colecoes.df` },
  {"h3": "Conceitos"},
  {"p": "Uma anotação de coleção descreve **o recipiente**, não o conteúdo:"},
  { code: `notas: Cluster := [7.5, 8.0]      // "é uma lista" — nada diz sobre os itens`, lang: 'df' },
  {"p": "Quando o conteúdo é uma regra de **tipo**, a anotação resolve: `notas: Cluster<Float> := [7.5, 8.0]` confere cada item e recusa um `append` fora do tipo. Este exercício é sobre o que a anotação **não** alcança — uma regra de valor (nota entre 0 e 10), ou dados que chegam de fora como texto —, e escrever essa validação é útil por si só."},
  {"h3": "Duas estratégias"},
  {"p": "**Verificar tudo antes de usar:**"},
  { code: `action todos_numeros(valores: Cluster) -> Boolean:
    cycle v in valores:
        given typeof(v) isnt "Integer" and typeof(v) isnt "Float":
            yield no
    yield yes`, lang: 'df' },
  {"p": "**Coletar todos os problemas e reportar juntos:**"},
  { code: `action validar_aluno(dados: Vault) -> Cluster:
    problemas := []
    given "nome" not in dados:
        problemas.append("falta o nome")
    ...
    yield problemas`, lang: 'df' },
  {"p": "A segunda é quase sempre melhor para entrada de usuário: quem preencheu um formulário quer ver os cinco erros de uma vez, não um por vez."},
  {"h3": "O detalhe do `orif`"},
  {"p": "Repare:"},
  { code: `given "nome" not in dados:
    problemas.append("falta o nome")
orif typeof(dados["nome"]) isnt "String":
    problemas.append("nome deve ser String")`, lang: 'df' },
  {"p": "O `orif` é essencial: sem ele, o segundo teste rodaria mesmo quando a chave não existe, e `dados[\"nome\"]` estouraria. `orif` só é avaliado se o `given` foi falso — ou seja, se a chave existe."},
  {"h3": "Saída esperada"},
  { code: `media das notas: 8.33
so numeros? yes
e com texto? no
[]
[falta o nome, nota deve ser numero]`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Escreva `validar_aluno` devolvendo um `Vault` com `{\"ok\": …, \"erros\": …}`.", "Use `Arcane.Collections.partition` para separar válidos de inválidos numa lista."]},
  {"h2": "126 · Tipagem gradual com Any"},
  {"p": "**Enunciado.** use Any quando o tipo depende do uso, e estreite depois com typeof."},
  { code: `// Any diz honestamente "pode ser qualquer coisa"
action envolver(valor: Any) -> Vault:
    yield {"tipo": typeof(valor), "valor": valor}

out envolver(42)
out envolver("texto")
out envolver([1, 2])

// Estreitar o tipo dentro da acao e o padrao correto
action descrever(v: Any) -> String:
    match v:
        point Integer as n:
            yield $"inteiro {n}"
        point Float as f:
            yield $"decimal {f}"
        point String as s:
            yield $"texto de {len(s)} letras"
        point Cluster as c:
            yield $"lista com {len(c)} itens"
        point Vault:
            yield "dicionario"
        point Void:
            yield "nada"
        default:
            yield "outro"

cycle v in [7, 2.5, "abc", [1, 2, 3], {"a":1}, void]:
    out descrever(v)

assert descrever(7) is "inteiro 7", "Integer"
assert descrever(2.5) is "decimal 2.5", "Float"
assert descrever("abc") is "texto de 3 letras", "String"
assert descrever([1, 2, 3]) is "lista com 3 itens", "Cluster"
assert descrever(void) is "nada", "Void"
assert envolver(42).tipo is "Integer", "envolver guarda o tipo"`, lang: 'df', title: `exercicios/11-tipos-e-checagem/126_any_e_gradual.df` },
  {"h3": "Conceitos"},
  {"p": "DataForge tem **tipagem gradual**: você anota o que sabe e deixa o resto livre. `Any` é a forma de dizer isso explicitamente."},
  { code: `action envolver(valor: Any) -> Vault:
    yield {"tipo": typeof(valor), "valor": valor}`, lang: 'df' },
  {"p": "Isso é diferente de **não anotar**:"},
  {"table": {"head": ["Forma", "Significado"], "rows": [["`action f(x):`", "não pensei sobre o tipo"], ["`action f(x: Any):`", "pensei, e qualquer tipo serve"]]}},
  {"p": "A segunda comunica intenção. Numa base de código grande, essa diferença é o que separa \"falta anotar\" de \"está anotado como flexível\"."},
  {"h3": "Estreitando o tipo"},
  {"p": "Aceitar `Any` não significa tratar tudo igual. O padrão é estreitar logo na entrada:"},
  { code: `match v:
    point Integer as n:
        yield $"inteiro {n}"
    point String as s:
        yield $"texto de {len(s)} letras"`, lang: 'df' },
  {"p": "Cada `point Tipo as nome` faz duas coisas ao mesmo tempo: **testa** o tipo e **liga** o valor a um nome já com aquele tipo garantido. É o equivalente DataForge do *type narrowing* do TypeScript."},
  {"h3": "A ordem dos `point` importa"},
  {"p": "Padrões são testados de cima para baixo, e o primeiro que casa vence. Coloque os específicos antes dos gerais:"},
  { code: `point Integer as n when n bigger 100:    // específico
    ...
point Integer:                           // geral
    ...`, lang: 'df' },
  {"p": "Invertido, o segundo nunca rodaria."},
  {"h3": "Saída esperada"},
  { code: `{tipo: Integer, valor: 42}
{tipo: String, valor: texto}
{tipo: Cluster, valor: [1, 2]}
inteiro 7
decimal 2.5
texto de 3 letras
lista com 3 itens
dicionario
nada`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Remova `point Void` e veja `void` cair no `default`.", "Adicione `point Integer when n bigger 100` **depois** de `point Integer` e"]},
  {"p": "confirme que ele nunca é alcançado."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/11-tipos-e-checagem/121_anotacoes_basicas.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '121-anotacoes-de-tipo', text: "121 · Anotacoes de tipo", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'a-regra-de-conversao', text: "A regra de conversão", level: 3 as const }, { id: 'passo-a-passo', text: "Passo a passo", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '122-acoes-com-tipos', text: "122 · Acoes com tipos", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'por-que-a-mensagem-importa', text: "Por que a mensagem importa", level: 3 as const }, { id: 'o-tipo-any', text: "O tipo `Any`", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '123-typeof-e-conversao', text: "123 · typeof e conversao", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'passo-a-passo', text: "Passo a passo", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '124-analise-estatica', text: "124 · Analise estatica", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-que-ele-encontra', text: "O que ele encontra", level: 3 as const }, { id: 'o-que-ele-nao-encontra', text: "O que ele NÃO encontra", level: 3 as const }, { id: 'erros-dentro-de-monitor', text: "Erros dentro de `monitor`", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '125-tipos-dentro-de-colecoes', text: "125 · Tipos dentro de colecoes", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'duas-estrategias', text: "Duas estratégias", level: 3 as const }, { id: 'o-detalhe-do-orif', text: "O detalhe do `orif`", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '126-tipagem-gradual-com-any', text: "126 · Tipagem gradual com Any", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'estreitando-o-tipo', text: "Estreitando o tipo", level: 3 as const }, { id: 'a-ordem-dos-point-importa', text: "A ordem dos `point` importa", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"11 · Tipos e checagem"}
      description={"6 exercícios: anotações, o analisador estático e generics."}
      href={"/docs/exercicios/11-tipos-e-checagem"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
