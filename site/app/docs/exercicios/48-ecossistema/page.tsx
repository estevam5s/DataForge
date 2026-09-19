// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "48 · Ecossistema e design",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 48`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[266](#266-o-mapa-que-nao-pode-mentir-e-o-principio-que-se-mede)", "**o mapa que nao pode mentir, e o principio que se mede**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "266 · o mapa que nao pode mentir, e o principio que se mede"},
  { code: `// As tres ultimas partes da referencia Deep Tech sao as de SINTESE: o
// desenho do ecossistema, os dez principios de design e a visao de
// implementacao. Sao as tres coisas que um projeto costuma escrever
// como prosa — e prosa nao roda, nao reprova e envelhece calada.
//
// Este exercicio mostra as tres feitas de outro jeito: derivadas do
// codigo e CONFERIDAS contra ele.

adopt Arcane.Ecossistema as Eco
adopt Arcane.Principios as Prin
adopt Arcane.Percurso as Perc
adopt Arcane.IO as IO
adopt Arcane.OS as OS

out "== 1. o mapa, conferido nas duas direcoes =="

// A conferencia cobra DUAS coisas, e a segunda e a que importa:
//   faltando  -> caminho citado no mapa que nao existe mais no disco
//   orfaos    -> modulo do nucleo que nao aparece em componente nenhum
//
// Sem a segunda, um modulo novo nasce FORA do mapa e o inventario fica
// incompleto em silencio. Foi ela que pegou o primeiro erro deste
// modulo: o mapa citava 'arcane_concurrent.py', e o arquivo se chama
// 'arcane_paralelo.py' — so a CLASSE se chama ArcaneConcurrent.
c := Eco.conferir()
assert c["ok"] is yes
assert len(c["faltando"]) is 0
assert len(c["orfaos"]) is 0
out $"   {c['citados']} caminhos conferidos, 0 orfaos"

// As tres marcas, e a terceira e a que da valor ao mapa
assert len(Eco.ESTADOS) is 3
assert "nao-existe" in Eco.ESTADOS

n := Eco.numeros()
assert n["existem"] + n["equivalem"] + n["nao_existem"] is n["componentes"]
out $"   {n['componentes']} componentes: {n['existem']} existem, " +
$"{n['equivalem']} equivalem, {n['nao_existem']} nao existem"

out ""
out "== 2. toda ausencia tem motivo escrito =="

// Um mapa que marca tudo como pronto nao e um mapa, e publicidade.
faltam := Eco.o_que_nao_existe()
assert len(faltam) bigger 0
cycle f in faltam:
    assert f["porque"] is not ""
    assert f["aqui"] is not ""

// A maior ausencia, e a razao dela
llvm := [f cycle f in faltam given f["no"] is "LLVM Backend"][0]
assert "fechamentos" in llvm["aqui"]
out $"   {len(faltam)} ausencias nomeadas, cada uma com o porque"

out ""
out "== 3. o principio que se MEDE =="

// A prova nao repete o texto do principio: ela roda o analisador sobre
// quatro trechos com defeito conhecido e conta quantos ele pega ANTES
// de o programa rodar.
p := Prin.conferir("compile-time-first")[0]
assert p["veredito"] is "parcial"
assert "4 de 4" in p["medido"]
out $"   {p['medido']}"

// E o veredito NAO e dez de dez, de proposito: um relatorio que
// aprovasse os dez seria a prova de que ninguem o leu.
v := Prin.veredito()
assert v["total"] is 10
assert v["cumprido"] + v["parcial"] + v["nao-se-aplica"] is 10
assert v["parcial"] bigger 0
out $"   {v['cumprido']} cumpridos, {v['parcial']} parciais, " +
$"{v['nao-se-aplica']} nao se aplica"

out ""
out "== 4. a tensao e o conteudo =="

// Um principio isolado nao informa nada: todo mundo e a favor de
// seguranca e de velocidade. O que informa e ONDE dois se contradizem
// e qual venceu — e essa decisao esta sempre num arquivo.
ts := Prin.tensoes()
assert len(ts) bigger_eq 9
cycle t in ts:
    assert len(t["entre"]) is 2
    assert t["custo"] is not ""  // toda escolha tem preco declarado
    assert t["onde"] is not ""  // e mora num arquivo
out $"   {len(ts)} tensoes, todas com custo e arquivo"

out ""
out "== 5. o percurso, e a fase que NAO roda =="

pasta := $"{OS.temp_dir()}/df-266-{randint(100000, 999999)}"
IO.mkdir(pasta)
alvo := $"{pasta}/exemplo.df"
IO.write(alvo, "action fatorial(n):\\n" +
    "    given n smaller_eq 1:\\n" +
    "        yield 1\\n" +
    "    yield n * fatorial(n - 1)\\n" +
    "out fatorial(10)\\n")

r := Perc.percorrer(alvo)
assert len(r["fases"]) is 10
assert r["ms"] bigger 0

// A ultima fase e NOMEADA e nao percorrida. Executar e o que o
// programa faz: um arquivo de verdade abre soquete e escreve em disco,
// e um comando que mostra fases nao pode ter efeito no mundo.
ultima := r["fases"][9]
assert ultima["fase"] is "execucao"
assert ultima["percorrida"] is no
assert ultima["ms"] is 0.0

// Apagar a fase do mapa faria o desenho parecer completo. Ela fica.
assert "nao percorrida" in ultima["saiu"]

percorridas := [f cycle f in r["fases"] given f["percorrida"]]
assert len(percorridas) is 9
cycle f in percorridas:
    assert f["ms"] bigger_eq 0.0
    assert f["saiu"] is not ""

out $"   9 fases percorridas em {r['ms']} ms; a mais cara: {r['mais_cara']}"

// E as divergencias em relacao ao desenho do documento
d := Perc.divergencias()
assert len(d) bigger_eq 5
cycle x in d:
    assert x["porque"] is not ""
out $"   {len(d)} divergencias do desenho, com motivo"

IO.remove_tree(pasta)

out ""
out "Tudo verde: o mapa bate com o disco, e os principios foram medidos."`, lang: 'df', title: `exercicios/48-ecossistema/266_ecossistema_e_principios.df` },
  {"p": "As três últimas partes da referência Deep Tech são as de **síntese**: o desenho do ecossistema, os dez princípios de design e a visão de implementação."},
  {"p": "São as três coisas que um projeto costuma escrever como prosa — e prosa não roda, não reprova e envelhece calada. Este exercício mostra as três feitas de outro jeito: **derivadas do código e conferidas contra ele**."},
  {"h3": "1. A conferência nas duas direções"},
  {"p": "`Arcane.Ecossistema.conferir()` cobra duas coisas, e a segunda é a que importa:"},
  {"table": {"head": ["Direção", "O que cobra", "O que impede"], "rows": [["`faltando`", "todo caminho citado existe no disco", "a peça foi renomeada e o mapa aponta para o nome antigo"], ["`orfaos`", "todo módulo do núcleo aparece em algum componente", "um módulo novo nasce **fora** do mapa, e o inventário fica incompleto em silêncio"]]}},
  {"p": "**Foi a segunda que pegou o primeiro erro deste módulo.** O mapa citava `dataforge/stdlib/arcane_concurrent.py` em dois componentes. O arquivo se chama `arcane_paralelo.py` — só a *classe* se chama `ArcaneConcurrent`. `conferir()` acusou os dois antes de o primeiro teste existir."},
  {"p": "Sem essa direção, o mapa teria nascido mentindo em dois pontos, e ninguém teria como saber."},
  {"h3": "2. As três marcas, e por que a terceira é a que vale"},
  {"table": {"head": ["Marca", "Estado", "Quer dizer"], "rows": [["`[+]`", "`existe`", "a peça está aqui, com esse papel"], ["`[~]`", "`equivale`", "há **outra** peça que responde a mesma pergunta, nomeada"], ["`[-]`", "`nao-existe`", "não há, e o motivo está escrito"]]}},
  {"p": "A lista é fechada de propósito. Um quarto estado seria o lugar onde \"mais ou menos\" se esconderia — e é exatamente o que não se quer num inventário."},
  {"p": "Sete componentes do desenho estão marcados `nao-existe`, e o exercício cobra que **cada um tenha motivo escrito**. Um mapa que marca tudo como pronto não é um mapa, é publicidade: quem o lê descobre a ausência ao tentar, no pior momento, e depois de ter escolhido a linguagem por causa dele."},
  {"h3": "3. A prova que roda"},
  {"p": "`Arcane.Principios` não repete o texto do princípio. Três das dez provas executam o analisador ou o interpretador:"},
  {"table": {"head": ["Princípio", "O que a prova faz", "Mediu"], "rows": [["`compile-time-first`", "roda o `check` sobre quatro trechos com defeito conhecido", "**4 de 4** antes de rodar"], ["`custo-zero`", "cria um blueprint sem contrato nem invariante e olha o que ele carrega", "**3 de 3** sentinelas em `None`"], ["`seguranca-por-padrao`", "roda o `check` num `thread` que escreve de fora e olha a severidade", "sai como `warning`"]]}},
  {"p": "E o veredito **não é dez de dez**: cinco cumpridos, quatro parciais, um que não se aplica. Um relatório que aprovasse os dez seria a prova de que ninguém o leu."},
  {"p": "`custo-zero` é `nao-se-aplica` porque a frase do documento — *abstrações devem compilar para código equivalente a implementações manuais* — não tem como valer sem compilação nativa. Forçá-la a valer seria redefini-la em silêncio. O que vale, e é cobrado, é outra leitura: **uma abstração custa zero para quem não a usa.**"},
  {"h3": "4. A tensão é o conteúdo"},
  {"p": "Um princípio isolado não informa nada. Todo mundo é a favor de segurança, e todo mundo é a favor de velocidade."},
  {"p": "O que informa é **onde dois princípios se contradizem e qual venceu** — e essa decisão, nesta linguagem, está sempre num arquivo. O exercício cobra que cada uma das nove tensões tenha **custo declarado** e **arquivo**."},
  {"p": "Exemplo: segurança por padrão × verificação antes de rodar. A escrita concorrente é **aviso**, não erro, porque um acumulador protegido por mutex passa pelo mesmo caminho de um sem proteção — e recusá-lo proibiria o uso correto. Custo aceito, escrito: um programa com bug de concorrência passa pelo `check`."},
  {"h3": "5. A fase que não roda"},
  {"p": "`Arcane.Percurso` leva o arquivo por nove fases e mede cada uma. A décima — `execucao` — é **nomeada, medida em zero e marcada como não percorrida**."},
  {"p": "Executar é o que o programa faz. Um arquivo de verdade abre soquete, escreve em disco e manda e-mail: um comando cuja função é *mostrar as fases* não pode ter efeito no mundo, e um que tivesse seria usado uma vez."},
  {"p": "E ela **fica no mapa**. Apagá-la faria o desenho parecer completo — a mesma razão por que `Machine Code` continua no desenho do ecossistema, marcado como ausente."},
  {"h3": "A armadilha que inverteu a resposta"},
  {"p": "A primeira versão do percurso apontava a fase errada, **com confiança**:"},
  {"table": {"head": ["Arquivo de 12 tokens", "Antes", "Depois"], "rows": [["fase mais cara", "`lir`, com **93,8%**", "`tipos`, com 27,2%"], ["total", "7,266 ms", "**0,526 ms**"], ["trabalho real do `lir`", "0,05 ms", "0,064 ms"]]}},
  {"p": "A causa: `lir` importa `compilador` e abre um interpretador por dentro. A primeira fase que toca um módulo paga o `import` dele, e o cronômetro atribui esse custo a ela."},
  {"p": "**Uma ferramenta que aponta a fase errada é pior que nenhuma**, porque a pessoa vai otimizar o lugar que a ferramenta indicou. Hoje os imports lentos acontecem antes de qualquer cronômetro, e há um comentário ao lado da linha que os aquece — para que ninguém os remova por parecerem inúteis."},
  {"h3": "O que levar"},
  {"list": ["Um mapa escrito à mão mente sem avisar; um mapa **conferido** reprova.", "Nomear a ausência **com o motivo** vale mais que marcar tudo como"]},
  {"p": "pronto."},
  {"list": ["Um princípio que não se aplica é informação, não um problema a"]},
  {"p": "esconder."},
  {"list": ["A medida precisa ser honesta sobre o que ela é: uma vez, nesta máquina,"]},
  {"p": "para comparar as fases **entre si**. Para comparar mudanças, há `Arcane.Bench`."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/48-ecossistema/266_ecossistema_e_principios.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '266-o-mapa-que-nao-pode-mentir-e-o-principio-que-se-mede', text: "266 · o mapa que nao pode mentir, e o principio que se mede", level: 2 as const }, { id: '1-a-conferencia-nas-duas-direcoes', text: "1. A conferência nas duas direções", level: 3 as const }, { id: '2-as-tres-marcas-e-por-que-a-terceira-e-a-que-vale', text: "2. As três marcas, e por que a terceira é a que vale", level: 3 as const }, { id: '3-a-prova-que-roda', text: "3. A prova que roda", level: 3 as const }, { id: '4-a-tensao-e-o-conteudo', text: "4. A tensão é o conteúdo", level: 3 as const }, { id: '5-a-fase-que-nao-roda', text: "5. A fase que não roda", level: 3 as const }, { id: 'a-armadilha-que-inverteu-a-resposta', text: "A armadilha que inverteu a resposta", level: 3 as const }, { id: 'o-que-levar', text: "O que levar", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"48 · Ecossistema e design"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/48-ecossistema"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
