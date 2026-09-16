import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Primeiros passos",
  description: "Instale o DataForge, escreva seu primeiro programa e conheça a linha de comando.",
};

const blocos: Bloco[] = [
  {"h2": "Instalar"},
  {"p": "DataForge precisa de Python 3.10 ou superior. Nada além disso — o runtime não tem dependências externas, nem no seu computador nem no servidor."},
  {"p": "**A forma mais rápida**, macOS e Linux:"},
  { code: `curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh`, lang: 'bash' },
  {"p": "No Windows, PowerShell:"},
  { code: `irm https://dataforge-lang.vercel.app/instalar.ps1 | iex`, lang: 'powershell' },
  {"p": "Os dois criam um ambiente próprio em `~/.dataforge` — não tocam no Python do sistema e não pedem `sudo`. Se preferir clonar o repositório e instalar em modo editável:"},
  { code: `git clone https://github.com/estevam5s/DataForge.git
cd DataForge

python3 -m venv .venv && source .venv/bin/activate
pip install .

dataforge version`, lang: 'bash' },
  {"p": "A saída confirma a versão instalada:"},
  { code: `DataForge v1.0.0
Python 3.12.x`, lang: 'text', title: `saída` },
  {"callout": {"tipo": "dica", "texto": "O comando `df` é um atalho para `dataforge`. Os dois fazem exatamente a mesma coisa."}},
  {"h2": "O primeiro programa"},
  {"p": "Crie um arquivo `ola.df`:"},
  { code: `// ola.df — o primeiro programa

nome := "mundo"
out $"Ola, {nome}!"

cycle i from 1 to 3:
    out $"contando: {i}"`, title: `ola.df` },
  {"p": "Execute:"},
  { code: `dataforge run ola.df`, lang: 'bash' },
  { code: `Ola, mundo!
contando: 1
contando: 2
contando: 3`, lang: 'text', title: `saída` },
  {"h2": "Lendo o código"},
  {"p": "Quatro coisas acontecem nesse programa, e todas seguem o vocabulário da linguagem:"},
  {"table": {"head": ["Linha", "O que faz"], "rows": [["`nome := \"mundo\"`", "`:=` atribui. Cria a variável se não existir."], ["`out $\"...\"`", "`out` imprime. O prefixo `$` liga a interpolação de `{nome}`."], ["`cycle i from 1 to 3:`", "`cycle` é o laço. O limite é **inclusivo** nos dois extremos."], ["indentação", "Blocos abrem com `:` e são delimitados por **4 espaços**. Tab é erro."]]}},
  {"h2": "A linguagem em cinco minutos"},
  {"p": "Quase tudo o que se usa no dia a dia cabe num arquivo. Este roda inteiro:"},
  { code: `nome := "Ana"
steady LIMITE := 3                    // steady = não muda mais
out $"ola, {nome}"

given LIMITE bigger 2:                // given / orif / otherwise
    nivel := "alto"
otherwise:
    nivel := "baixo"
out nivel                             // o nome sai do ramo: "alto"

itens := ["pao", "leite", "cafe"]
cycle i, item in enumerate(itens):
    out $"{i + 1}. {item}"

out [x * x cycle x in [1, 2, 3, 4] given x % 2 is 0]   // compreensão

estoque := {"pao": 2, "leite": 0}
out estoque["leite"] ?? 0, estoque["cha"] ?? "sem registro"

action saudar(quem: String, entusiasmo: Integer := 1) -> String:
    yield $"oi, {quem}" + "!" * entusiasmo
out saudar("mundo", 3)`, title: `tour.df` },
  { code: `ola, Ana
alto
1. pao
2. leite
3. cafe
[4, 16]
0 sem registro
oi, mundo!!!`, lang: 'text', title: `saída` },
  {"p": "Se você vem de outra linguagem, a [referência da linguagem](/docs/referencia/gramatica) mostra o equivalente de cada construção. Os nomes são diferentes de propósito: `out` em vez de `print`, `cycle` em vez de `for`, `action` em vez de `def`."},

  {"h2": "Um programa com estrutura"},
  {"p": "O próximo passo é organizar o código em ações e tipos. Este exemplo já usa quase tudo o que a linguagem tem de característico:"},
  { code: `record Aluno:
    nome: String
    nota: Number

action conceito(nota: Number) -> String:
    given nota bigger_eq 9:
        yield "A"
    orif nota bigger_eq 7:
        yield "B"
    otherwise:
        yield "C"

turma := [
    Aluno("Ana", 9.5),
    Aluno("Bruno", 7.0),
    Aluno("Carla", 5.5)
]

cycle a in turma:
    out $"{a.nome.pad_end(8)} {a.nota}  {conceito(a.nota)}"

media := turma >> morph a: a.nota >> distill acc, n: acc + n 0
out $"\\nmedia da turma: {round(media / len(turma), 2)}"`, title: `turma.df` },
  { code: `Ana      9.5  A
Bruno    7.0  B
Carla    5.5  C

media da turma: 7.33`, lang: 'text', title: `saída` },
  {"h2": "Um programa inteiro, e pequeno"},
  {"p": "Uma lista de tarefas usa `record`, `with`, compreensão e pipeline — e cabe em vinte linhas. Note que nada é mutado: `concluir` devolve uma lista **nova**."},
  { code: `record Tarefa:
    titulo: String
    feita: Boolean := no

action concluir(lista: Cluster, titulo: String) -> Cluster:
    yield [t with {"feita": yes} given t.titulo is titulo otherwise t
           cycle t in lista]

action pendentes(lista: Cluster) -> Cluster:
    yield lista >> sift t: t.feita is no

lista := [Tarefa("comprar pao"), Tarefa("pagar conta"), Tarefa("ligar pro Bruno")]
lista := concluir(lista, "pagar conta")

cycle t in lista:
    marca := "[x]" given t.feita otherwise "[ ]"
    out $"{marca} {t.titulo}"

out $"\nfaltam {len(pendentes(lista))} de {len(lista)}"`, title: `lista.df` },
  { code: `[ ] comprar pao
[x] pagar conta
[ ] ligar pro Bruno

faltam 2 de 3`, lang: 'text', title: `saída` },
  {"p": "Três coisas aparecem aí e valem o nome: `record` é imutável, e por isso se muda com [`with`](/docs/fundamentos/records); o `given … otherwise` no meio de uma expressão é o **ternário**; e `>> sift` é o filtro de um [pipeline](/docs/pipelines)."},

  {"h2": "Quando algo dá errado"},
  {"p": "O erro é parte da linguagem, não um acidente. Ele diz o que houve, **onde**, o que existia no lugar e o que fazer:"},
  { code: `precos := {"pao": 5}
out precos["leite"] + 1`, title: `erro.df` },
  { code: `erro[DF0602]: A chave "leite" não está neste vault.
  ┌─ erro.df:2:5
  │
1 │ precos := {"pao": 5}
2 │ out precos["leite"] + 1
  │     ^ a chave foi lida aqui
  │
  = nota: o vault tem 1 chave(s): "pao"
  = dica: use  valor ?? padrao  para um padrão, ou confira antes com  vault.has(chave)
  = doc: https://dataforge-lang.vercel.app/docs/colecoes`, lang: 'text', title: `saída` },
  {"callout": {"tipo": "dica", "titulo": "As mensagens falam português", "texto": "E voltam ao inglês com `DF_IDIOMA=en`, que é o que se usa em log de servidor e em relato de bug."}},

  {"h2": "A linha de comando"},
  {"p": "O `dataforge` faz mais do que executar. Estes são os comandos do dia a dia:"},
  {"table": {"head": ["Comando", "O que faz"], "rows": [["`dataforge run arquivo.df`", "Executa um programa"], ["[`dataforge check`](/docs/cli/check)", "Análise estática: nomes, aridade, tipos — **antes** de executar"], ["[`dataforge test`](/docs/cli/test)", "Descobre e roda `*_test.df` e `tests/`"], ["[`dataforge fmt`](/docs/cli/fmt)", "Formata o código"], ["[`dataforge lint`](/docs/cli/lint)", "Aponta problemas de estilo"], ["[`dataforge repl`](/docs/cli/repl)", "Console interativo"], ["[`dataforge init`](/docs/cli/init)", "Cria um projeto novo"]]}},
  {"h3": "Verifique antes de rodar"},
  {"p": "O `check` encontra erros sem executar uma linha:"},
  { code: `dataforge check turma.df`, lang: 'bash' },
  { code: `turma.df:9:11: erro: Parameter 'nota' of 'conceito' expects Number but got String
    sugestão: Pass a Number
turma.df:14:5: erro: Undefined action 'Alunoo'
    sugestão: Did you mean 'Aluno'?`, lang: 'text', title: `exemplo de saída` },
  {"h2": "Testar o que você escreveu"},
  {"p": "O corredor de testes vem junto, e a sintaxe é da própria linguagem — sem biblioteca a instalar:"},
  { code: `action somar(a: Number, b: Number) -> Number:
    yield a + b
relay somar`, title: `soma.df` },
  { code: `adopt ../soma as S
adopt Arcane.Crucible as C

crucible "soma":
    trial "soma dois numeros":
        expect S.somar(2, 3) is 5
    trial "aceita decimais":
        expect S.somar(0.5, 0.25) is 0.75

C.run()`, title: `tests/soma_test.df` },
  { code: `dataforge test tests`, lang: 'bash' },
  { code: `✓ tests/soma_test.df (2/2)

2 passaram em 1 arquivo(s) — 0.03s
Tudo verde.`, lang: 'text', title: `saída` },
  {"p": "Com `--cobertura`, ele também diz quais linhas os testes executaram, e `--minimo=80` reprova no CI. Mais em [`dataforge test`](/docs/cli/test)."},

  {"h2": "O console interativo"},
  {"p": "Para experimentar uma linha sem criar arquivo:"},
  { code: `dataforge repl`, lang: 'bash' },
  { code: `forge> x := 21
forge> x * 2
=> 42
forge> :type x
Integer  = 21
forge> exit`, lang: 'text' },
  {"p": "Além de avaliar expressões, o console tem `:type` (o tipo e o valor de um nome), `:ast` (a árvore de uma linha) e `:load` (carregar um arquivo no ambiente atual)."},

  {"h2": "No editor"},
  {"p": "Um comando instala a extensão no VS Code e derivados — cores, autocompletar, ir-para-definição, os erros na margem enquanto você digita, e o depurador no F5:"},
  { code: `dataforge editor`, lang: 'bash' },
  {"p": "A coloração é **gerada** das palavras reservadas do próprio interpretador, então ela nunca fica atrás da linguagem. Detalhes em [Editor e LSP](/docs/editor)."},

  {"h2": "Um projeto de verdade"},
  {"p": "Para algo além de um arquivo solto, o `init` cria a estrutura:"},
  { code: `dataforge init meu-app
cd meu-app

dataforge run      # usa a entrada declarada no forge.toml
dataforge test     # roda tests/`, lang: 'bash' },
  {"p": "O que ele gera:"},
  { code: `meu-app/
  forge.toml              manifesto: nome, versão, entrada, scripts
  src/main.df             o programa
  tests/principal_test.df os testes`, lang: 'text' },
  {"h2": "Seis armadilhas de quem está chegando"},
  {"p": "Todas já custaram tempo a alguém. Ler esta tabela uma vez economiza a primeira tarde:"},
  {"table": {"head": ["Armadilha", "O que acontece", "A forma certa"], "rows": [["`total // n` para dividir", "`//` é **comentário**; a linha vira `out total` e imprime 10", "`total ~/ n` — a divisão inteira é `~/`"], ["Tab na indentação", "`Tab character detected. DataForge requires spaces only.`", "4 espaços por nível, sempre"], ["`no := 1`", "`'no' é palavra reservada e não pode receber valor`", "`no`, `in`, `is`, `to`, `from`, `as` e `step` são reservadas"], ["`yield` esperando uma sequência", "`yield` **encerra** a ação no primeiro valor", "`stream action` + `emit` para produzir vários"], ["`x` em vez de `self.x` num método", "lê a variável de fora, calado", "`self.` sempre, dentro de método"], ["`p.x := 1` num record", "record é imutável — é erro", "`p with {\"x\": 1}` devolve uma cópia"]]}},
  {"p": "Uma delas engana mesmo quem já sabe: `out total // 2` **é** divisão (o `//` seguido de dígito é operador), e `out total // n` é comentário. A regra completa está em [Operadores](/docs/operadores)."},

  {"h2": "Para onde ir agora"},
  {"cards": [{"href": "/docs/variaveis", "title": "Variáveis e tipos", "desc": "Como declarar, os tipos primitivos e as anotações opcionais."}, {"href": "/docs/exercicios/01-fundamentos", "title": "Exercícios 01", "desc": "Doze exercícios de fundamentos, cada um se verifica sozinho."}, {"href": "/docs/referencia/gramatica", "title": "A referência", "desc": "Gramática, precedência e semântica — a resposta definitiva."}, {"href": "/docs/instalacao", "title": "Instalação detalhada", "desc": "Windows, ambiente virtual e solução de problemas."}, {"href": "/docs/cli", "title": "A CLI completa", "desc": "Todos os comandos e suas opções."}, {"href": "/docs/big-o", "title": "Complexidade e Big-O", "desc": "Quanto o seu código cresce — analisado sem rodar nada."}]},
  {"callout": {"tipo": "nota", "titulo": "Aprender na ordem", "texto": "Se você prefere um caminho guiado a uma referência, a [trilha](/docs/exercicios) tem 18 capítulos em ordem, cada um com exercícios que se verificam sozinhos."}},
];

const headings = [{ id: 'instalar', text: "Instalar", level: 2 as const }, { id: 'o-primeiro-programa', text: "O primeiro programa", level: 2 as const }, { id: 'lendo-o-codigo', text: "Lendo o código", level: 2 as const }, { id: 'a-linguagem-em-cinco-minutos', text: "A linguagem em cinco minutos", level: 2 as const }, { id: 'um-programa-com-estrutura', text: "Um programa com estrutura", level: 2 as const }, { id: 'um-programa-inteiro-e-pequeno', text: "Um programa inteiro, e pequeno", level: 2 as const }, { id: 'quando-algo-da-errado', text: "Quando algo dá errado", level: 2 as const }, { id: 'a-linha-de-comando', text: "A linha de comando", level: 2 as const }, { id: 'verifique-antes-de-rodar', text: "Verifique antes de rodar", level: 3 as const }, { id: 'testar-o-que-voce-escreveu', text: "Testar o que você escreveu", level: 2 as const }, { id: 'o-console-interativo', text: "O console interativo", level: 2 as const }, { id: 'no-editor', text: "No editor", level: 2 as const }, { id: 'um-projeto-de-verdade', text: "Um projeto de verdade", level: 2 as const }, { id: 'seis-armadilhas-de-quem-esta-chegando', text: "Seis armadilhas de quem está chegando", level: 2 as const }, { id: 'para-onde-ir-agora', text: "Para onde ir agora", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Primeiros passos"}
      description={"Instale o DataForge, escreva seu primeiro programa e conheça a linha de comando."}
      href={"/docs/primeiros-passos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
