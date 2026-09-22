// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Cálculo financeiro",
  description: "Folha de pagamento com faixas progressivas — em Decimal, e com o centavo que sobra repartido.",
};

const blocos: Bloco[] = [
  {"p": "Dinheiro tem duas regras que float quebra: somar tem de ser exato, e dividir tem de fechar. Um salário de R$ 1000,00 dividido em três parcelas não são três de 333,33: é 333,34 + 333,33 + 333,33. Este projeto calcula uma folha com desconto progressivo por faixa e reparte sem perder centavo."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`19.99d`", "o literal decimal, construído do texto"], ["`Dec.arredondar`", "arredondar com modo declarado"], ["`Dec.repartir`", "dividir e o centavo fechar"], ["tabela de faixas", "o imposto progressivo como dado"]]}},
  {"h2": "Estrutura"},
  { code: `folha/
  src/
    faixas.df     a tabela do ano — so dados
    calculo.df    bruto -> descontos -> liquido
    holerite.df   o texto que vai para a pessoa
  tests/
    calculo_test.df  com os exemplos da tabela oficial`, lang: 'text' },
  { code: `[project]
name = "folha"
version = "0.1.0"
description = "Folha de pagamento"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `adopt Arcane.Decimal as Dec

// Faixas de exemplo (NAO sao as oficiais): 'ate' e o teto da faixa.
FAIXAS := [
    {"ate": 2000.00d, "aliquota": 0.075d},
    {"ate": 3500.00d, "aliquota": 0.09d},
    {"ate": 5000.00d, "aliquota": 0.12d},
    {"ate": void,     "aliquota": 0.14d}
]

// Progressivo: cada faixa cobra so o PEDACO do salario que cai nela.
action desconto(bruto, faixas):
    total := Dec.zero()
    piso := Dec.zero()
    cycle f in faixas:
        teto := f["ate"] ?? bruto
        given bruto bigger piso:
            base := min(bruto, teto) - piso
            given base bigger Dec.zero():
                total := total + base * f["aliquota"]
        piso := teto
    yield Dec.arredondar(total, 2)

action holerite(nome, bruto):
    d := desconto(bruto, FAIXAS)
    yield {"nome": nome, "bruto": bruto, "desconto": d, "liquido": bruto - d}

h := holerite("Ana", 4200.00d)
out $"{h['nome']}: bruto {Dec.texto(h['bruto'])}, desconto {Dec.texto(h['desconto'])}, liquido {Dec.texto(h['liquido'])}"

// 2000 * 7,5% + 1500 * 9% + 700 * 12% = 150 + 135 + 84 = 369
assert Dec.texto(h["desconto"]) is "369.00"
assert Dec.texto(h["liquido"]) is "3831.00"

// A parcela que fecha: tres de 333,33 perderiam um centavo.
parcelas := Dec.repartir(1000.00d, 3)
out parcelas >> morph p: Dec.texto(p)
assert Dec.texto(Dec.soma(parcelas)) is "1000.00"`, lang: 'df', title: `src/calculo.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt Arcane.Decimal as Dec
adopt ../src/calculo as C

crucible "desconto progressivo":
    trial "abaixo da primeira faixa":
        expect Dec.texto(C.desconto(1000.00d, C.FAIXAS)) is "75.00"

    trial "a soma das parcelas fecha":
        expect Dec.texto(Dec.soma(Dec.repartir(10.00d, 3))) is "10.00"`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["o literal `d`", "`Decimal(0.1)` já nasce com o erro do float"], ["a faixa cobra só o **pedaço** dela", "o salário de 2001 paga 9% sobre tudo, e ganhar um real a mais reduz o líquido"], ["`repartir` em vez de dividir", "o parcelamento some com um centavo por cliente, e a conciliação nunca fecha"], ["as faixas são um arquivo de dados", "a atualização anual vira uma mudança de código"]]}},
  {"h2": "Para ir além"},
  {"list": ["Compare com [Arcane.Decimal](/docs/biblioteca/decimal) e [Decimal](/docs/tecnicas/decimal).", "Gere o holerite em planilha: [Planilhas](/docs/tecnicas/planilhas).", "Um teste por linha da tabela oficial — quando a lei muda, o teste muda junto."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Cálculo financeiro"}
      description={"Folha de pagamento com faixas progressivas — em Decimal, e com o centavo que sobra repartido."}
      href={"/docs/projetos/folha-de-pagamento"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
