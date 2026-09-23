// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_engenharia.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Junções que não inflam",
  description: "Uma chave duplicada na tabela de apoio multiplica o fato — e o total sobe sem nada acusar.",
};

const blocos: Bloco[] = [
  {"p": "É o desastre mais caro da engenharia de dados, e ele cabe em quatro linhas: a tabela de apoio ganhou uma linha duplicada, a junção multiplicou o fato, e o total do relatório subiu."},
  { code: `adopt Arcane.Quadro as Q

vendas := Q.de_vaults([{"cli": "a", "v": 10}, {"cli": "b", "v": 20}])

// A tabela de apoio com a chave DUPLICADA — quase sempre por um
// carregamento repetido, ou por um cadastro que virou dois.
clientes := Q.de_vaults([
    {"cli": "a", "nome": "Ana"},
    {"cli": "a", "nome": "Ana (duplicada)"},
    {"cli": "b", "nome": "Bia"},
])

junto := vendas.juntar(clientes, "cli")
assert junto.altura() is 3                              // eram 2 vendas
assert (junto.coluna("v") >> distill a, x: a + x 0) is 40   // era 30
out "duas vendas de 30 viraram três linhas de 40 — sem erro nenhum"`, lang: 'df' },
  {"h2": "Declarar fecha a porta"},
  { code: `adopt Arcane.Quadro as Q

vendas := Q.de_vaults([{"cli": "a", "v": 10}, {"cli": "b", "v": 20}])
clientes := Q.de_vaults([
    {"cli": "a", "nome": "Ana"},
    {"cli": "a", "nome": "Ana (duplicada)"},
    {"cli": "b", "nome": "Bia"},
])

monitor:
    vendas.juntar(clientes, "cli", "dentro", "muitos_para_um")
    assert no
handle Error as e:
    out e.message
    out $"  {e.dica}"`, lang: 'df' },
  {"table": {"head": ["Cardinalidade", "Promete", "Quando"], "rows": [["`muitos_para_um`", "a chave é única **do outro lado**", "a busca numa tabela de apoio — o caso mais comum"], ["`um_para_muitos`", "única **deste lado**", "um pedido e seus itens"], ["`um_para_um`", "única nos dois", "duas visões da mesma entidade"], ["`muitos_para_muitos`", "nada", "a permissiva **declarada** — e é o padrão"]]}},
  {"p": "O padrão continua sendo **não conferir**: mudá-lo reprovaria código que já existe e pode estar certo. O que muda é ser possível declarar — e um `muitos_para_um` numa junção de apoio custa uma palavra."},
  {"h2": "Declarar a explosão é diferente de não dizer nada"},
  { code: `adopt Arcane.Quadro as Q

pedidos := Q.de_vaults([{"id": 1}, {"id": 2}])
itens := Q.de_vaults([
    {"id": 1, "produto": "cafe"},
    {"id": 1, "produto": "filtro"},
    {"id": 2, "produto": "cha"},
])

// Aqui a multiplicação é o PONTO: um pedido tem vários itens.
// Declará-la diz a quem lê que alguém pensou nisso.
junto := pedidos.juntar(itens, "id", "dentro", "um_para_muitos")
assert junto.altura() is 3
out junto.texto()`, lang: 'df' },
  {"h2": "Antes de declarar, olhe"},
  { code: `adopt Arcane.Quadro as Q

clientes := Q.de_vaults([
    {"cli": "a", "nome": "Ana"},
    {"cli": "a", "nome": "Ana 2"},
    {"cli": "b", "nome": "Bia"},
])

// 'duplicadas' responde quais chaves se repetem, e quantas vezes.
repetidas := clientes.duplicadas(["cli"])
assert repetidas.altura() > 0
out repetidas.texto()

// E 'sem_duplicadas' mantém a PRIMEIRA de cada chave.
limpo := clientes.sem_duplicadas(["cli"])
assert limpo.altura() is 2`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A junção que não casa nada também é silenciosa", "texto": "Com `tipo := \"dentro\"`, uma chave que mudou de tipo (o `id` inteiro virou texto) não casa com **nada** — e o resultado é um quadro vazio, sem erro. Confira a altura depois de juntar: `assert junto.altura() > 0` é a asserção mais barata de um pipeline."}},
];

const headings = [{ id: 'declarar-fecha-a-porta', text: "Declarar fecha a porta", level: 2 as const }, { id: 'declarar-a-explosao-e-diferente-de-nao-dizer-nada', text: "Declarar a explosão é diferente de não dizer nada", level: 2 as const }, { id: 'antes-de-declarar-olhe', text: "Antes de declarar, olhe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Junções que não inflam"}
      description={"Uma chave duplicada na tabela de apoio multiplica o fato — e o total sobe sem nada acusar."}
      href={"/docs/dados/cardinalidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
