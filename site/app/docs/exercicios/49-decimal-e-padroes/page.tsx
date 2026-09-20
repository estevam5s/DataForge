// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "49 · Decimal exato e padrões",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 49`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[267](#267-o-centavo-que-fecha-e-o-caso-que-aparece-antes-de-rodar)", "**o centavo que fecha, e o caso que aparece antes de rodar**", "dois itens de CORRECAO. 'Float' e IEEE 754 binario e nao"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "267 · o centavo que fecha, e o caso que aparece antes de rodar"},
  {"p": "**Enunciado.** dois itens de CORRECAO. 'Float' e IEEE 754 binario e nao"},
  { code: `// representa 0,1, e quem escrevia 19.99 nao era avisado de nada — o
// sufixo 'd' constroi o valor a partir do TEXTO. E um 'match' sobre
// [Cor, x] que trata so uma cor deixava a outra de fora em silencio: o
// caso esquecido devolve 'void', e 'void' atravessa meia duzia de
// chamadas antes de virar erro em outro lugar.

adopt Arcane.Decimal as Dec

out "== 1. o literal decimal exato =="

// 'Float' e IEEE 754 binario: ele nao representa 0,1.
assert 0.1 + 0.2 is not 0.3
// O sufixo 'd' constroi o valor a partir do TEXTO — e essa e a
// diferenca: Decimal("0.1") e exato, Decimal(0.1) ja carrega o erro.
assert 0.1d + 0.2d is 0.3d
assert typeof(19.99d) is "Decimal"
out $"   0.1d + 0.2d = {0.1d + 0.2d}"

// O literal e o modulo produzem o MESMO valor
assert 19.99d is Dec.de("19.99")
assert Dec.centavos(19.99d) is 1999

// O 'd' so conta quando TERMINA o numero, e um nome 'd' continua livre
d := 3
assert d is 3
out "   um nome chamado 'd' continua valendo"

// Misturar com Float e RECUSADO: e a mesma decisao que faz
// 'Decimal' nao ser um 'Number'.
monitor:
    quebrado := 19.99d + 0.01
    assert no
handle Error as e:
    assert "Decimal" in e.message

// Num carrinho de verdade: centavos que fecham
record Item:
    nome: String
    preco: Decimal

action total(itens: Cluster) -> Decimal:
    soma := 0d
    cycle i in itens:
        soma += i.preco
    yield soma

carrinho := [Item("cafe", 19.99d), Item("pao", 5.01d), Item("leite", 4.50d)]
assert total(carrinho) is 29.50d
out $"   total do carrinho: {total(carrinho)}"

out ""
out "== 2. exaustividade em padrao aninhado =="

enum Cor:
    Verde
    Amarelo

// Um 'match' sobre [Cor, x] que trata so uma cor deixa a outra de fora,
// e o 'check' avisa: "nao cobre 1 combinacao: [Cor.Amarelo, _]".
// Aqui esta completo — e e por isso que ele nao avisa.
action rotular(par):
    match par:
        point [Cor.Verde, n]:
            yield $"verde {n}"
        point [Cor.Amarelo, n]:
            yield $"amarelo {n}"
        default:
            yield "outro"

assert rotular([Cor.Verde, 1]) is "verde 1"
assert rotular([Cor.Amarelo, 2]) is "amarelo 2"
out "   as duas cores tratadas, nas duas posicoes"

// Uma captura no eixo do enum cobre TODOS os membros dele
action qualquer_cor(par):
    match par:
        point [c, n]:
            yield $"{c.name}:{n}"
        default:
            yield "nao e par"

assert qualquer_cor([Cor.Amarelo, 9]) is "Amarelo:9"
out "   e uma captura no eixo cobre o enum inteiro"

out ""
out "Tudo verde: o centavo fecha, e o caso esquecido aparece antes de rodar."`, lang: 'df', title: `exercicios/49-decimal-e-padroes/267_decimal_e_exaustividade.df` },
  {"p": "Dois itens que faltavam para a linguagem estar completa, e os dois são de **correção**: um erra dinheiro em silêncio, o outro devolve `void` em silêncio."},
  {"h3": "1. O literal decimal: `19.99d`"},
  {"p": "`Float` é IEEE 754 de 64 bits, e ele **não representa 0,1** — representa o binário mais próximo. A diferença aparece na soma:"},
  { code: `assert 0.1 + 0.2 is not 0.3          // Float
assert 0.1d + 0.2d is 0.3d           // Decimal: exato`, lang: 'df' },
  {"p": "Antes do sufixo, a exatidão exigia escrever `Dec.de(\"19.99\")` — e quem escrevia `19.99` **não era avisado de nada**. Um centavo que some numa linha some de novo num milhão de linhas."},
  {"p": "O sufixo constrói o valor a partir do **texto**, sem passar por float nenhum. É a diferença que decide:"},
  {"table": {"head": ["Como", "Resultado"], "rows": [["`Decimal(\"0.1\")`", "exato"], ["`Decimal(0.1)`", "já carrega o erro do float que veio antes"]]}},
  {"p": "**Três detalhes que o exercício cobra**"},
  {"p": "**O `d` só conta quando termina o número.** `19.99dias` é um número seguido de um nome — engolir o `d` ali criaria um `ias` do nada. E um nome chamado `d` continua valendo. É a mesma disciplina de adjacência do `~/` e do hífen num caminho relativo."},
  {"p": "**O literal e o módulo são o mesmo valor.** `19.99d is Dec.de(\"19.99\")`, e `Dec.centavos`, `Dec.arredondar` e `Dec.repartir` trabalham com ele."},
  {"p": "**Misturar com `Float` é recusado.** Um `Decimal` existe para ser exato, e somá-lo a um `Float` devolveria o erro binário de volta dentro — o exato contaminado pelo aproximado, sem nada denunciar. E é por isso que `Decimal` **não é um `Number`**: um `Number` que o aceitasse faria a falha aparecer dentro da ação, longe de quem passou o valor."},
  {"p": "O `check` acusa a mistura **antes de rodar** (`decimal-com-float`). Antes ela só aparecia em execução."},
  {"h3": "2. Exaustividade em padrão aninhado"},
  {"p": "O `match` já avisava o que ficava de fora num enum solto. Com o enum **dentro** de uma sequência, ele calava:"},
  { code: `point [Cor.A, x]:     // e o Cor.B? Nada avisava.`, lang: 'df' },
  {"p": "O motivo é arquitetural, e vale entender: a conferência de enum olha o padrão **inteiro**, e `[Cor.A, x]` não é um membro de enum. A de sequência **reivindica** o match e se cala, porque `Cor.A` não é irrefutável e o ramo não conta como cobertura de tamanho. Duas conferências, e o caso passava entre as duas."},
  {"p": "Hoje a cobertura é **por posição**, e o que se cobra é o produto cartesiano dos eixos de enum — com duas posições de `Cor`, quatro combinações."},
  {"p": "**O que faz a regra calar**"},
  {"table": {"head": ["Quando", "Por quê"], "rows": [["ramos de tamanhos diferentes, ou com `...resto`", "ali a pergunta é de **tamanho**, e quem responde é a outra conferência"], ["uma posição com literal (`[Cor.A, 0]`)", "`[Cor.A, 0]` **não** cobre `[Cor.A, *]`, e tratar como se cobrisse inverteria o sentido do aviso"], ["mais de 64 combinações", "um aviso que lista duzentas é ruído, e ninguém o lê duas vezes"]]}},
  {"p": "Uma posição **irrefutável** cobre todos os membros daquele eixo — é o que faz `point [Cor.A, x]` mais `point [c, x]` ser completo, e o exercício demonstra os dois."},
  {"p": "E um `point` com **guarda** nunca conta como cobertura, aqui como nas outras quatro formas: `point [Cor.B, x] when x bigger 0` deixa passar o `x` negativo."},
  {"h3": "O que levar"},
  {"list": ["Um número que uma pessoa vai conferir na mão pede `d`.", "Um caso esquecido num `match` devolve `void`, e `void` atravessa meia"]},
  {"p": "dúzia de chamadas antes de virar erro **em outro lugar**. É por isso que vale ser avisado antes de rodar."},
  {"list": ["E as duas regras **calam** onde não conseguem provar. Um falso alarme"]},
  {"p": "ensina a ignorar mensagens."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/49-decimal-e-padroes/267_decimal_e_exaustividade.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '267-o-centavo-que-fecha-e-o-caso-que-aparece-antes-de-rodar', text: "267 · o centavo que fecha, e o caso que aparece antes de rodar", level: 2 as const }, { id: '1-o-literal-decimal-1999d', text: "1. O literal decimal: `19.99d`", level: 3 as const }, { id: '2-exaustividade-em-padrao-aninhado', text: "2. Exaustividade em padrão aninhado", level: 3 as const }, { id: 'o-que-levar', text: "O que levar", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"49 · Decimal exato e padrões"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/49-decimal-e-padroes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
