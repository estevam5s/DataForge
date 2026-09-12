import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Análise estática",
  description: "O que o dataforge check encontra antes de executar, e por que ele é otimista.",
};

const blocos: Bloco[] = [
  {"h2": "Três etapas sem executar"},
  { code: `dataforge check meu_programa.df
dataforge check src/ --strict      # avisos também falham
dataforge check x.df --syntax-only # só a sintaxe`, lang: 'bash' },
  {"list": ["**Léxica** — o arquivo é um DataForge válido?", "**Sintática** — a estrutura faz sentido?", "**Semântica** — os nomes existem? as chamadas batem? os tipos combinam?"]},
  {"h2": "O que ele encontra"},
  {"table": {"head": ["Categoria", "Exemplo", "Mensagem"], "rows": [["nome indefinido", "`sommar(1, 2)`", "*Did you mean `somar`?*"], ["aridade", "`somar(1)`", "*is missing argument(s): b*"], ["tipo de argumento", "`somar(\"x\", 2)`", "*expects Integer but got String*"], ["tipo de variável", "`x: Integer := \"texto\"`", "*Declared as Integer but the value is String*"], ["tipo inexistente", "`x: Intger := 1`", "*Did you mean `Integer`?*"], ["constante reatribuída", "`LIMITE := 200`", "*Cannot reassign the steady constant*"], ["operador incompatível", "`1 + [2]`", "*Cannot add Integer and Cluster*"], ["campo de record", "`p.emial`", "*Record has no field. Fields: nome, idade*"], ["membro de enum", "`Status.Cancelado`", "*Members: Ativo, Inativo*"], ["código inalcançável", "linha após `yield`", "*Unreachable code* (aviso)"], ["retorno ausente", "`-> Integer` sem `yield`", "*can end without a yield* (aviso)"], ["`halt` fora de laço", "", "*halt outside of a loop*"], ["`point` inalcançável", "uma captura antes de um literal", "*este `point` nunca casa*"], ["escrita concorrente", "`total := total + 1` dentro de `parallel`", "*duas threads podem perder atualizações* (aviso)"], ["ciclo de import", "`a.df → b.df → a.df`", "a cadeia inteira"], ["membro entre arquivos", "`P.naoExiste()`", "*Did you mean…* — mesmo vindo de outro `.df`"]]}},
  {"h2": "Um exemplo"},
  { code: `app.df:5:1: erro: Cannot reassign the steady constant 'LIMITE'
    sugestão: Use another name, or drop 'steady' from the declaration
app.df:9:11: erro: Parameter 'a' of 'somar' expects Integer but got String
    sugestão: Pass a Integer
app.df:10:5: erro: Undefined action 'sommar'
    sugestão: Did you mean 'somar'?

✗ 3 erro(s), 0 aviso(s)`, lang: 'text' },
  {"p": "Cada diagnóstico traz **linha, coluna e sugestão**. As sugestões de nome usam distância de edição — `sommar` → `somar` é encontrado automaticamente."},
  {"h2": "Por que é otimista"},
  {"p": "O analisador fica calado quando não consegue **provar** que algo está errado. Isso é deliberado: DataForge é dinamicamente tipado, e um falso alarme atrapalha mais que um alerta perdido — porque ensina a ignorar as mensagens."},
  {"p": "Calibragem atual: **zero erros** em 259 arquivos conhecidamente bons (os 231 exercícios mais os 44 exemplos)."},
  {"h3": "O que ele não encontra"},
  { code: `divisor := 0
out 10 / divisor      # o valor só é conhecido em tempo de execução` },
  {"p": "Isso passa no `check` e falha ao rodar. Erros que dependem de dados não são detectáveis estaticamente."},
  {"h2": "Ele atravessa o `adopt`"},
  {"p": "É a checagem que mais importa em projeto grande: num arquivo de 40 linhas o erro aparece na primeira execução; num de 200 arquivos, a **maioria das chamadas atravessa módulo** — e todas elas eram invisíveis."},
  { code: `adopt ./pedido as P

p := P.criar(1, "Ana")

out p.clientte        // Record 'P.Pedido' has no field 'clientte'
q := P.criar(1)       // 'P.criar' takes 2 argument(s), got 1
P.apagar(1)           // module 'P' has no 'apagar'
P.criar(1, 2)         // Parameter 'cliente' expects String, got Integer` },
  {"p": "O primeiro e o último dependem das declarações de tipo: uma ação que declara `-> Tipo` leva o tipo através da fronteira, e uma que declara `param: Tipo` tem cada argumento conferido — com a linha onde ela foi declarada, no outro arquivo. Sem as declarações, o analisador cala."},
  {"callout": {"tipo": "dica", "titulo": "É o que torna a anotação de tipo valer a pena", "texto": "Num arquivo só, `-> Tipo` e `param: Tipo` documentam. Atravessando módulo, eles são a diferença entre um erro achado em 0,4 s e um erro achado em produção — e a maioria das chamadas de um sistema grande atravessa módulo."}},
  {"callout": {"tipo": "nota", "titulo": "A superfície é lida sem executar", "texto": "O `check` abre o outro `.df` com o lexer e o parser, e nunca o roda — analisar não pode ter efeito colateral. O resultado fica em cache por `(caminho, mtime)`: sem ele, 200 arquivos importando três vizinhos cada levariam o `check` de 0,7 s a mais de um minuto."}},
  {"p": "E ele cala **inteiro** quando a superfície do outro arquivo não é confiável: se ele não compila, se há ciclo de import, se a profundidade (4 níveis) acaba, ou se o `relay` nomeia algo que só existe em execução."},
  {"h2": "A corrida de dados, que ninguém avisava"},
  {"p": "Quatro threads somando vinte mil vezes na mesma variável entregaram **40.425 de 80.000** — metade, sem nada denunciando. `x := x + 1` são três passos (ler, somar, escrever), e o interpretador pode trocar de thread entre eles."},
  {"p": "A linguagem não sincroniza sozinha, e isso é uma decisão: `Arcane.Concurrent` tem as ferramentas, e aplicá-las é escolha de quem escreve. Mas nem o `check` nem o `lint` **mencionavam** o risco — era o único bug caro que passava calado."},
  { code: `total := 0
v := {"n": 0}

parallel:
    total := total + 1    // aviso: 'total' vem de fora
    v["n"] := v["n"] + 1  // aviso: 'v' vem de fora

thread:
    meu := 0              // sem aviso: cada thread tem o seu
    meu := meu + 1` },
  {"p": "A forma `v[\"n\"] := …` é a que mais engana — parece mexer só no campo, e o vault vem de fora. Ela é acusada igual."},
  {"table": {"head": ["Cala quando", "Porque"], "rows": [
   ["o nome é declarado **dentro** do bloco", "cada thread tem o seu; não há o que perder"],
   ["o bloco só **lê**", "duas threads lendo o mesmo valor não perdem nada — e avisar aqui daria alarme no uso mais comum, que é passar dado para a thread"],
   ["a escrita está numa **ação** que o bloco chama", "seguir chamada exigiria um grafo, e um aviso que depende disso seria impreciso nos dois sentidos"]]}},
  {"callout": {"tipo": "nota", "titulo": "É aviso, e não erro", "texto": "Escrever de duas threads é legítimo quando quem escreve sabe: um acumulador protegido por `mutex` passa por aqui igual, e recusá-lo seria proibir o uso correto. Para silenciar num caso específico, `// df: permitir escrita-concorrente` — é o que o exercício 170 faz, porque ali a corrida é o assunto."}},
  {"h2": "Silenciar uma regra, de propósito"},
  {"p": "Quando o alarme está certo e o código também, `// df: permitir <regra>` silencia aquela regra naquela linha — ou na de baixo, que é onde o comentário cabe num `match` longo."},
  { code: `action ordem(n):
    match n:
        point x:
            yield "pegou tudo"
        // df: permitir point-inalcancavel
        point 5:
            yield "nunca chega aqui"` },
  {"p": "A regra tem de ser **nomeada**. Um `permitir` solto esconderia o erro seguinte, que ninguém pediu para esconder — e várias regras cabem numa linha, separadas por vírgula."},
  {"callout": {"tipo": "nota", "titulo": "O caso que provou a necessidade", "texto": "O exercício 139 **demonstra** a armadilha de um `point` inalcançável, com um `assert` provando o comportamento. Quando a checagem foi escrita, ela acusou o exercício — e estava certa. O exercício também. Um analisador sem escape obriga quem escreve a escolher entre conviver com um alarme e desligar a verificação inteira, e a segunda é o que acontece."}},
  {"h2": "Erros dentro de monitor"},
  {"p": "Código dentro de um `monitor:` existe justamente para conter falhas — provocar uma de propósito é legítimo. Por isso o analisador **rebaixa erros a avisos** ali dentro:"},
  { code: `monitor:
    x := 1 / 0        # aviso, não erro
handle e:
    out e.message` },
  {"h2": "Em integração contínua"},
  { code: `dataforge fmt . --check && dataforge check . && dataforge test`, lang: 'bash' },
  {"p": "Cada comando sai com código diferente de zero em caso de falha. Com `--strict`, os avisos também derrubam o build."},
];

const headings = [{ id: 'tres-etapas-sem-executar', text: "Três etapas sem executar", level: 2 as const }, { id: 'o-que-ele-encontra', text: "O que ele encontra", level: 2 as const }, { id: 'um-exemplo', text: "Um exemplo", level: 2 as const }, { id: 'por-que-e-otimista', text: "Por que é otimista", level: 2 as const }, { id: 'o-que-ele-nao-encontra', text: "O que ele não encontra", level: 3 as const }, { id: 'ele-atravessa-o-adopt', text: "Ele atravessa o `adopt`", level: 2 as const }, { id: 'a-corrida-de-dados-que-ninguem-avisava', text: "A corrida de dados, que ninguém avisava", level: 2 as const }, { id: 'silenciar-uma-regra-de-proposito', text: "Silenciar uma regra, de propósito", level: 2 as const }, { id: 'erros-dentro-de-monitor', text: "Erros dentro de monitor", level: 2 as const }, { id: 'em-integracao-continua', text: "Em integração contínua", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Análise estática"}
      description={"O que o dataforge check encontra antes de executar, e por que ele é otimista."}
      href={"/docs/tecnicas/analise-estatica"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
