import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Códigos de erro",
  description: "O que cada código significa, com exemplo e solução.",
};

const blocos: Bloco[] = [
  {"p": "Todo erro do DataForge carrega um código estável. Ele aparece no relatório e serve para procurar aqui — ou no terminal, com `dataforge explain`."},
  { code: `dataforge explain DF0601`, lang: 'bash' },
  {"h2": "Anatomia de um erro"},
  { code: `erro[DF0601]: Key "b" is not in this vault.
  ┌─ exemplo.df:2:5
  │
1 │ v := {"nome": "ana"}
2 │ out v["b"]
  │     ^^^^^^ key read here
  │
  = nota: the vault has 1 key: "nome"
  = dica: use  valor ?? padrao, ou vault.has(chave) antes de ler
  = doc:  https://dataforge-lang.vercel.app/docs/colecoes`, lang: 'text' },
  {"table": {"head": ["Parte", "O que traz"], "rows": [["`erro[DF0601]`", "o código, para procurar"], ["`┌─ arquivo:linha:coluna`", "onde"], ["O trecho", "duas linhas de contexto, com a que falhou destacada"], ["`^^^^` e o rótulo", "o que exatamente falhou"], ["`nota:`", "contexto que ajuda a entender"], ["`dica:`", "o que fazer"], ["`doc:`", "a página que trata do assunto"]]}},
  {"p": "A separação entre **nota** e **dica** é deliberada: a mensagem diz o que houve, a dica diz o que fazer. Misturar as duas produz textos longos que ninguém lê."},
  {"h2": "As famílias"},
  {"table": {"head": ["Faixa", "Sobre"], "rows": [["`DF01xx`", "sintaxe — lexer e parser"], ["`DF02xx`", "execução"], ["`DF03xx`", "tipos e OOP"], ["`DF04xx`", "nomes"], ["`DF05xx`", "módulos"], ["`DF06xx`", "índice e chave"], ["`DF07xx`", "erro lançado pelo programa"], ["`DF08xx`", "recursão"]]}},
  {"h2": "DF0101 — Indentacao inconsistente"},
  {"p": "DataForge usa indentacao para delimitar blocos, e aceita apenas espacos.\nUm caractere de tabulacao no meio de linhas indentadas com espaco produz\num bloco que o leitor ve de um jeito e o parser ve de outro."},
  { code: `given x bigger 0:
    out "com espacos"
	out "com tab"      // <- SyncError`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Como resolver", "texto": "Configure o editor para inserir espacos no lugar de tab.\nNo VS Code:  \"editor.insertSpaces\": true, \"editor.tabSize\": 4\nDepois:      dataforge fmt arquivo.df"}},
  {"h2": "DF0102 — Caractere inesperado"},
  {"p": "O lexer encontrou um simbolo que nao faz parte da linguagem.\n\nA causa mais comum e usar '=' para atribuir. Em DataForge a atribuicao e\n':=' — o '=' sozinho nao existe."},
  { code: `x = 10        // errado
x := 10       // certo`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Como resolver", "texto": "Troque '=' por ':=', ou remova o simbolo desconhecido."}},
  {"h2": "DF0103 — Erro de sintaxe"},
  {"p": "O parser encontrou um token onde esperava outro. A mensagem diz o que\nesperava; a coluna marca onde.\n\nCausas frequentes:\n  - falta ':' no fim de um cabecalho (given, cycle, action, blueprint)\n  - parentese ou colchete sem fechar\n  - 'otherwise' sem o 'given' correspondente"},
  { code: `given x bigger 0        // falta ':'
    out "positivo"

given x bigger 0:       // certo
    out "positivo"`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Como resolver", "texto": "Confira o ':' e o pareamento de parenteses e colchetes."}},
  {"h2": "DF0201 — Erro em tempo de execucao"},
  {"p": "O programa foi analisado sem problema, mas falhou ao rodar. Divisao por\nzero, conversao impossivel e reatribuicao de 'steady' caem aqui."},
  { code: `out 10 / divisor          // se divisor for 0, estoura aqui

given divisor isnt 0:     // a guarda evita
    out 10 / divisor`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Como resolver", "texto": "Guarde a condicao antes, ou envolva em 'monitor':\n\n    monitor:\n        out 10 / divisor\n    handle e:\n        out \"nao deu:\", e.message"}},
  {"h2": "DF0301 — Tipo incompativel"},
  {"p": "Uma operacao recebeu um tipo que nao aceita, ou uma anotacao foi\ncontrariada.\n\nTambem aparece em OOP: metodo de instancia chamado no blueprint, spawn de\nblueprint abstrato, escrita em propriedade so-leitura, e blueprint que\nnao implementou o que o trait exige."},
  { code: `action dobro(n: Integer) -> Integer:
    yield n * 2

out dobro("texto")        // String onde se esperava Integer`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Como resolver", "texto": "Converta antes (int, float, str), ou ajuste a anotacao.\n'dataforge check .' aponta a maioria destes antes de rodar."}},
  {"h2": "DF0401 — Nome nao definido"},
  {"p": "O nome nao existe em nenhum escopo visivel deste ponto.\n\nQuando ha algo parecido, a mensagem sugere — o caso mais comum e erro de\ndigitacao. Quando nao ha, geralmente o nome foi usado antes de receber\nvalor, ou esta em outro escopo."},
  { code: `contador := 0
out contadr        // DF0401: voce quis dizer 'contador'?`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Como resolver", "texto": "Confira a grafia, e lembre que a atribuicao e ':=' — 'x = 1' nao cria x.\nVariavel criada dentro de um bloco nao existe fora dele."}},
  {"h2": "DF0501 — Modulo nao encontrado"},
  {"p": "O 'adopt' procurou em tres lugares e nao achou:\n\n  1. biblioteca padrao (Arcane.*)\n  2. arquivos ao lado do que faz o import\n  3. forge_modules/, subindo ate achar um forge.toml"},
  { code: `adopt validador as V      // se nao instalado, DF0501`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Como resolver", "texto": "Se e um pacote:            dataforge add validador\nSe e um arquivo seu:       confira o caminho e o nome\nSe e da stdlib:            confira a grafia (Arcane.Math, nao Arcane.math)"}},
  {"h2": "DF0601 — Indice ou chave invalida"},
  {"p": "Leitura fora da faixa de um cluster, ou de uma chave que o vault nao tem.\n\nEm cluster de n itens, os indices validos vao de 0 a n-1 — ou de -1 a -n\ncontando do fim. O erro classico e usar len(x) como indice, quando o\nultimo e len(x) - 1."},
  { code: `itens := [10, 20, 30]
out itens[3]        // DF0601: so ha 0, 1 e 2
out itens[-1]       // 30, o ultimo

v := {"nome": "ana"}
out v["idade"]      // DF0601: a chave nao existe`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Como resolver", "texto": "Confira o tamanho antes:   given len(itens) bigger i:\nUse valor de reserva:      v[\"idade\"] ?? 0\nOu confirme a chave:       given v.has(\"idade\"):"}},
  {"h2": "DF0701 — Erro lancado pelo programa"},
  {"p": "Alguem chamou 'trigger'. Nao e uma falha da linguagem: e o programa\nsinalizando uma condicao que ele mesmo considera invalida."},
  { code: `action sacar(saldo, valor):
    given valor bigger saldo:
        trigger "saldo insuficiente"
    yield saldo - valor`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Como resolver", "texto": "Trate com monitor/handle:\n\n    monitor:\n        novo := sacar(100, 500)\n    handle e:\n        out \"recusado:\", e.message"}},
  {"h2": "DF0801 — Recursao profunda demais"},
  {"p": "A pilha passou de mil quadros. Quase sempre e recursao sem caso base, ou\ncom um caso base que nunca e alcancado."},
  { code: `action contar(n):
    yield contar(n - 1)     // nunca para

action contar(n):
    given n smaller_eq 0:   // caso base
        yield 0
    yield contar(n - 1)`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Como resolver", "texto": "Confirme que o caso base existe e que cada chamada se aproxima dele.\nPara profundidade grande de verdade, troque a recursao por um laco."}},
  {"h2": "Pilha de chamadas"},
  {"p": "Quando o erro acontece dentro de uma ação, o relatório mostra o caminho até ele:"},
  { code: `  pilha de chamadas (mais recente primeiro):
    em media                  relatorio.df:8
    em resumo                 relatorio.df:10`, lang: 'text' },
];

const headings = [{ id: 'anatomia-de-um-erro', text: "Anatomia de um erro", level: 2 as const }, { id: 'as-familias', text: "As famílias", level: 2 as const }, { id: 'df0101-indentacao-inconsistente', text: "DF0101 — Indentacao inconsistente", level: 2 as const }, { id: 'df0102-caractere-inesperado', text: "DF0102 — Caractere inesperado", level: 2 as const }, { id: 'df0103-erro-de-sintaxe', text: "DF0103 — Erro de sintaxe", level: 2 as const }, { id: 'df0201-erro-em-tempo-de-execucao', text: "DF0201 — Erro em tempo de execucao", level: 2 as const }, { id: 'df0301-tipo-incompativel', text: "DF0301 — Tipo incompativel", level: 2 as const }, { id: 'df0401-nome-nao-definido', text: "DF0401 — Nome nao definido", level: 2 as const }, { id: 'df0501-modulo-nao-encontrado', text: "DF0501 — Modulo nao encontrado", level: 2 as const }, { id: 'df0601-indice-ou-chave-invalida', text: "DF0601 — Indice ou chave invalida", level: 2 as const }, { id: 'df0701-erro-lancado-pelo-programa', text: "DF0701 — Erro lancado pelo programa", level: 2 as const }, { id: 'df0801-recursao-profunda-demais', text: "DF0801 — Recursao profunda demais", level: 2 as const }, { id: 'pilha-de-chamadas', text: "Pilha de chamadas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Códigos de erro"}
      description={"O que cada código significa, com exemplo e solução."}
      href={"/docs/referencia/erros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
