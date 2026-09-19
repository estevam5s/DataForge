// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Os dez princípios, medidos",
  description: "Cada princípio com a frase do documento, o que ela significa aqui, o veredito e uma prova que roda — duas delas chamam o analisador e uma abre um interpretador.",
};

const blocos: Bloco[] = [
  {"p": "A referência fecha com dez princípios de design. Uma lista de princípios é o texto mais fácil de escrever num projeto e o mais fácil de não cumprir: **ninguém a executa, e por isso ela nunca reprova.**"},
  {"p": "Aqui cada princípio carrega cinco coisas, e a terceira é a que muda o gênero do texto:"},
  {"table": {"head": ["Campo", "O que é"], "rows": [["`no_documento`", "a frase como a referência a escreve"], ["`aqui`", "o que ela significa **nesta** implementação"], ["`veredito`", "`cumprido`, `parcial` ou `nao-se-aplica` — e a lista é fechada"], ["`prova`", "uma medida que **roda**, e o número que ela deu"], ["`custo`", "o que foi entregue em troca"]]}},
  { code: `dataforge principios             # os dez, medidos
dataforge principios --tensoes   # so onde dois se contradizem
dataforge principios --json      # como dado`, lang: 'bash' },
  {"h2": "O veredito não é dez de dez, de propósito"},
  {"p": "Cinco cumpridos, quatro parciais, um que não se aplica. Um relatório que aprovasse os dez seria a prova de que ninguém o leu."},
  { code: `adopt Arcane.Principios as Prin

v := Prin.veredito()
assert v["total"] is 10
assert v["cumprido"] bigger 0
assert v["parcial"] bigger 0

// A prova RODA: ela nao repete o texto, ela mede
p := Prin.conferir("compile-time-first")[0]
assert p["veredito"] is "parcial"
assert "4 de 4" in p["medido"]
out p["medido"]`, lang: 'df' },
  {"h2": "As provas que rodam de verdade"},
  {"p": "Três das dez não consultam tabela nenhuma: elas executam o analisador ou o interpretador, porque \"verificação antes de rodar\" e \"custo zero quando desligado\" não são frases — são coisas que se demonstram ou não se demonstram."},
  {"table": {"head": ["Princípio", "O que a prova faz", "O que ela mediu"], "rows": [["`compile-time-first`", "roda o `check` sobre quatro trechos com defeito conhecido — índice fora do alcance, chave ausente, laço que nunca roda, igualdade impossível", "**4 de 4** acusados antes de rodar"], ["`custo-zero`", "cria um blueprint sem contrato, invariante nem modificador e olha o que ele carrega", "**3 de 3** sentinelas em `None`, **2 de 2** atalhos de acesso ligados"], ["`seguranca-por-padrao`", "roda o `check` sobre um `thread` que escreve num nome de fora e olha a **severidade**", "sai como `warning` — e não como `error`"], ["`interoperabilidade`", "adota um módulo do Python de verdade", "a ponte resolve"], ["`runtime-modular`", "abre um interpretador sem nenhum `adopt`", "**0** módulos carregados, **0** dependências externas"]]}},
  {"h2": "O que \"custo zero\" quer dizer aqui — e por que o veredito é `nao-se-aplica`"},
  {"p": "O documento diz: *abstrações de alto nível devem compilar para código equivalente a implementações manuais.* Não havendo compilação para código nativo, **a frase não tem como valer**, e forçá-la a valer seria redefini-la em silêncio."},
  {"p": "Então o veredito é `nao-se-aplica` — e há outra leitura que vale, é cobrada e foi medida: **uma abstração custa zero para quem não a usa.**"},
  {"table": {"head": ["Leitura", "Como é cobrada"], "rows": [["contrato, sobrecarga, `exclusive`", "`DFAction.extras` é `None`"], ["invariante na linhagem, metaclasse com gancho", "`DFBlueprint.vigias` é `None`"], ["congelado, travado, `lazy`, `readonly` em construção", "`DFInstance._estado` é `None`"], ["propriedade, descritor, `__getattribute__`", "`leitura_simples` e `escrita_simples` continuam ligados"]]}},
  {"callout": {"tipo": "dica", "titulo": "O acesso a campo ficou mais rápido DEPOIS de os recursos existirem", "texto": "4,47 s → cerca de 3,8 s na carga de método/campo/`spawn`. Não é coincidência: os dois atalhos por blueprint só existiram porque os recursos precisavam de um jeito de sair do caminho — e, no caminho, encontraram o que já estava custando."}},
  {"callout": {"tipo": "atencao", "titulo": "E aqui está o preço, escrito", "texto": "Quem acrescenta um jeito novo de interceptar acesso precisa **derrubar o atalho** do blueprint. A falta disso não dá erro: só faz o recurso novo não rodar para os objetos simples — silenciosamente, que é a pior forma de falhar."}},
  {"h2": "Os dez, em resumo"},
  {"table": {"head": ["#", "Princípio", "Veredito", "O limite"], "rows": [["1", "segurança por padrão", "`parcial`", "o analisador é otimista: a escrita concorrente é **aviso**, não erro"], ["2", "custo zero", "`nao-se-aplica`", "não há compilação nativa; vale a leitura \"custa zero quando desligado\""], ["3", "controle explícito de recursos", "`cumprido`", "controla-se o protocolo e o coletor, não a alocação"], ["4", "compile-time first", "`parcial`", "quando não consegue provar, **cala** — e os silêncios estão listados"], ["5", "interoperabilidade", "`cumprido`", "depende de tratar objeto estranho por protocolo, em todo o caminho"], ["6", "portabilidade", "`parcial`", "é **herdada** do CPython: é o que dá ARM de graça e o que põe o teto"], ["7", "performance observável", "`cumprido`", "medir e ler erram de formas opostas, e por isso existem as duas"], ["8", "extensibilidade", "`cumprido`", "palavra nova entra como **contextual**, ao custo de complexidade no parser"], ["9", "runtime modular", "`cumprido`", "zero dependência: criptografia e formato de arquivo escritos aqui"], ["10", "escalabilidade técnica", "`parcial`", "kernel, bare-metal e microcontrolador estão **fora**, e são nomeados"]]}},
  {"p": "Cada linha da tabela aponta um arquivo. É o que a próxima página usa: [onde dois princípios se contradizem](/docs/ecossistema/tensoes), e qual venceu."},
];

const headings = [{ id: 'o-veredito-nao-e-dez-de-dez-de-proposito', text: "O veredito não é dez de dez, de propósito", level: 2 as const }, { id: 'as-provas-que-rodam-de-verdade', text: "As provas que rodam de verdade", level: 2 as const }, { id: 'o-que-custo-zero-quer-dizer-aqui-e-por-que-o-veredito-e-nao-se-aplica', text: "O que \"custo zero\" quer dizer aqui — e por que o veredito é `nao-se-aplica`", level: 2 as const }, { id: 'os-dez-em-resumo', text: "Os dez, em resumo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Os dez princípios, medidos"}
      description={"Cada princípio com a frase do documento, o que ela significa aqui, o veredito e uma prova que roda — duas delas chamam o analisador e uma abre um interpretador."}
      href={"/docs/ecossistema/principios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
