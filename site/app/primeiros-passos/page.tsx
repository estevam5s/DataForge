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
  {"p": "DataForge precisa de Python 3.10 ou superior. Nada além disso — o runtime não tem dependências externas."},
  { code: `git clone https://github.com/estevam5s/DataForge.git
cd DataForge

python3 -m venv .venv && source .venv/bin/activate
pip install .

dataforge version`, lang: 'bash' },
  {"p": "A saída confirma a versão instalada:"},
  { code: `DataForge v4.0.0
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
  {"h2": "A linha de comando"},
  {"p": "O `dataforge` faz mais do que executar. Estes são os comandos do dia a dia:"},
  {"table": {"head": ["Comando", "O que faz"], "rows": [["`dataforge run arquivo.df`", "Executa um programa"], ["[`dataforge check`](/cli/check)", "Análise estática: nomes, aridade, tipos — **antes** de executar"], ["[`dataforge test`](/cli/test)", "Descobre e roda `*_test.df` e `tests/`"], ["[`dataforge fmt`](/cli/fmt)", "Formata o código"], ["[`dataforge lint`](/cli/lint)", "Aponta problemas de estilo"], ["[`dataforge repl`](/cli/repl)", "Console interativo"], ["[`dataforge init`](/cli/init)", "Cria um projeto novo"]]}},
  {"h3": "Verifique antes de rodar"},
  {"p": "O `check` encontra erros sem executar uma linha:"},
  { code: `dataforge check turma.df`, lang: 'bash' },
  { code: `turma.df:9:11: erro: Parameter 'nota' of 'conceito' expects Number but got String
    sugestão: Pass a Number
turma.df:14:5: erro: Undefined action 'Alunoo'
    sugestão: Did you mean 'Aluno'?`, lang: 'text', title: `exemplo de saída` },
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
  {"h2": "Para onde ir agora"},
  {"cards": [{"href": "/variaveis", "title": "Variáveis e tipos", "desc": "Como declarar, os tipos primitivos e as anotações opcionais."}, {"href": "/instalacao", "title": "Instalação detalhada", "desc": "Windows, ambiente virtual e solução de problemas."}, {"href": "/exercicios/01-fundamentos", "title": "Exercícios 01", "desc": "Doze exercícios de fundamentos, cada um se verifica sozinho."}, {"href": "/cli", "title": "A CLI completa", "desc": "Todos os comandos e suas opções."}]},
];

const headings = [{ id: 'instalar', text: "Instalar", level: 2 as const }, { id: 'o-primeiro-programa', text: "O primeiro programa", level: 2 as const }, { id: 'lendo-o-codigo', text: "Lendo o código", level: 2 as const }, { id: 'um-programa-com-estrutura', text: "Um programa com estrutura", level: 2 as const }, { id: 'a-linha-de-comando', text: "A linha de comando", level: 2 as const }, { id: 'um-projeto-de-verdade', text: "Um projeto de verdade", level: 2 as const }, { id: 'para-onde-ir-agora', text: "Para onde ir agora", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Primeiros passos"}
      description={"Instale o DataForge, escreva seu primeiro programa e conheça a linha de comando."}
      href={"/primeiros-passos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
