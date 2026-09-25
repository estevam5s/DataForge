// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Os componentes",
  description: "Vinte e dois componentes, os mesmos na Janela e numa tela da Bigorna — e o que cada um devolve.",
};

const blocos: Bloco[] = [
  {"p": "Cada chamada **põe** um componente e **devolve** o valor dele. É o que faz a tela ser um programa comum, de cima para baixo."},
  {"callout": {"tipo": "nota", "titulo": "Os mesmos na Bigorna", "texto": "Uma tela da [Bigorna](/docs/desktop) recebe o mesmo `t`: tudo desta página vale lá, e ela acrescenta `t.comando`, `t.ir`, os diálogos, `t.status` e a tabela com seleção. Os exemplos abaixo usam a `Arcane.Janela`, a camada de baixo, porque ela basta para uma tela só."}},
  {"h2": "Entradas"},
  { code: `adopt Arcane.Janela as J

action tela(t):
    nome := t.entrada("Nome", "")
    senha := t.senha("Senha")
    idade := t.numero("Idade", 18, 0, 120)
    obs := t.area("Observações", "", 4)
    cor := t.escolha("Cor", ["azul", "verde"], "verde")
    ativo := t.caixa("Ativo", yes)
    nivel := t.deslizante("Nível", 0, 10, 5)
    quando := t.data("Quando", "2026-09-22")
    onde := t.arquivo("Arquivo", "", ["csv"])

    t.texto($"{nome}|{idade}|{cor}|{ativo}|{nivel}")

s := J.testar(tela)
assert s.campos() is ["Arquivo", "Ativo", "Cor", "Idade", "Nome", "Nível", "Observações", "Quando", "Senha"]
s.digitar("Nome", "Ana")
s.digitar("Idade", 30)
assert s.tem("Ana|30|verde|yes|5")
out s.texto()`, lang: 'df' },
  {"table": {"head": ["Componente", "Devolve", "Nota"], "rows": [["`entrada`", "texto", "uma linha"], ["`senha`", "texto", "esconde o que se digita"], ["`numero`", "**Integer ou Float**", "digitado ele chega como texto, e `n + 1` daria concatenação"], ["`area`", "texto", "várias linhas"], ["`escolha`", "a opção", "uma de uma lista"], ["`caixa`", "`yes`/`no`", ""], ["`deslizante`", "número", "com mínimo e máximo"], ["`data`", "texto", "sem seletor nativo — é um campo com formato"], ["`arquivo`", "o caminho", "sem display, é um campo de texto"]]}},
  {"h2": "Mostrar"},
  { code: `adopt Arcane.Janela as J

action tela(t):
    t.titulo("Relatório")
    t.texto("uma linha de texto comum")
    t.aviso("deu certo")
    t.erro("não deu")
    t.separador()
    t.tabela(["produto", "preço"], [
        {"produto": "café", "preço": "32,90"},
        {"produto": "filtro", "preço": "8,50"},
    ])
    t.lista(["primeiro", "segundo"])
    t.progresso(0.72, "carregando")

s := J.testar(tela)
assert s.tem("Relatório") and s.tem("deu certo")
assert s.tabelas()[0]["linhas"] is [["café", "32,90"], ["filtro", "8,50"]]
out s.texto()`, lang: 'df' },
  {"p": "A tabela aceita **vault ou lista**: com vault, as colunas casam pelo nome; com lista, pela posição. Os dois são comuns — `Database.query` devolve vaults, e um CSV lido devolve listas."},
  {"h2": "O botão vale para UMA execução"},
  { code: `adopt Arcane.Janela as J

salvos := []

action tela(t):
    t.entrada("Nome", "")
    given t.botao("Salvar", yes):
        salvos.append(1)

s := J.testar(tela)
s.clicar("Salvar")
assert len(salvos) is 1

// Reexecutar NÃO salva de novo: o clique é um evento, e não estado.
s.digitar("Nome", "x")
assert len(salvos) is 1
out "um clique, um salvamento"`, lang: 'df' },
  {"p": "Se o clique ficasse guardado, a próxima reexecução salvaria o formulário de novo — e esse é o defeito clássico de quem monta isto à mão."},
  {"h2": "Agrupar"},
  { code: `adopt Arcane.Janela as J

action tela(t):
    t.grupo("Identificação")
    t.entrada("Nome")
    t.entrada("E-mail")
    t.fim()

    t.grupo("Endereço")
    t.entrada("Rua")
    t.fim()

s := J.testar(tela)
assert s.tem("Identificação") and s.tem("Endereço")
assert len(s.campos()) is 3
out s.texto()`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Dois campos com o mesmo rótulo", "texto": "Eles existem — e sem um contador na chave dividiriam o estado, o que faz digitar num mudar o outro. A chave é `especie:rotulo`, com `#2` a partir do segundo."}},
];

const headings = [{ id: 'entradas', text: "Entradas", level: 2 as const }, { id: 'mostrar', text: "Mostrar", level: 2 as const }, { id: 'o-botao-vale-para-uma-execucao', text: "O botão vale para UMA execução", level: 2 as const }, { id: 'agrupar', text: "Agrupar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Os componentes"}
      description={"Vinte e dois componentes, os mesmos na Janela e numa tela da Bigorna — e o que cada um devolve."}
      href={"/docs/desktop/componentes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
