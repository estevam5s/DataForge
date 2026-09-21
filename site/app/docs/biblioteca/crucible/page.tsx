// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/crucible.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Crucible",
  description: "Framework de testes: suítes, matchers, fixtures, dublês e benchmark.",
};

const blocos: Bloco[] = [
  {"h2": "Constantes"},
  {"table": {"head": ["Nome", "Valor"], "rows": [["`matchers_novos`", "`[\"to_be_one_of\", \"to_be_ordered_by\", \"to_be_subset_of\", \"…`"], ["`mutacoes`", "`[{\"de\": \"bigger_eq\", \"para\": \"bigger\", \"descricao\": \"afro…`"]]}},
  {"h2": "Funções (58)"},
  {"table": {"head": ["Assinatura"], "rows": [["`after(corpo)`"], ["`after_all(corpo)`"], ["`approx(valor, casas=7)`"], ["`banco(db)`"], ["`before(corpo)`"], ["`before_all(corpo)`"], ["`benchmark(nome, acao, vezes=1000, aquecimento=10)`"], ["`booleans()`"], ["`capture(acao)`"], ["`check(condicao, mensagem='a condicao nao se cumpriu')`"], ["`clusters(item=None, tamanho_max=10)`"], ["`com_relogio(acao, inicio=None)`"], ["`contrato(nome, casos)`"], ["`corrida(acao, threads=4, voltas=5000, leitor=None, esperado=None)`"], ["`database(db)`"], ["`describe(nome, corpo=None)`"], ["`determinismo(acao, vezes=5)`"], ["`diff(esperado, obtido)`"], ["`expect(valor, rotulo='')`"], ["`fail(mensagem='falhou por decisao do teste')`"], ["`fixture(nome, corpo)`"], ["`flaky(acao, tentativas=3, espera=0.0)`"], ["`floats(minimo=-1000.0, maximo=1000.0)`"], ["`forall(gerador, propriedade, casos=100, semente=None)`"], ["`freeze_time(instante)`"], ["`instantaneo(nome, valor, atualizar=None)`"], ["`instavel(acao, tentativas=3, espera=0.0)`"], ["`integers(minimo=-1000, maximo=1000)`"], ["`json()`"], ["`junit()`"], ["`mock(nome='mock', alvo=None)`"], ["`mutar(arquivo, rodar_testes, limite=40)`"], ["`one_of(valores)`"], ["`only(nome, corpo, tags=None)`"], ["`pending(nome, motivo='', corpo=None)`"], ["`relatorio_de_mutacao(resultado)`"], ["`relogio(inicio=None)`"], ["`report(colorir=True, verboso=False)`"], ["`reset()`"], ["`results()`"], ["`run(opcoes=None)`"], ["`servidor_falso(porta=0)`"], ["`snapshot(nome, valor, atualizar=None)`"], ["`snapshot_dir(arquivo)`"], ["`spy(alvo, nome='spy')`"], ["`stub(respostas=None, nome='stub')`"], ["`suite(nome, corpo=None)`"], ["`summary()`"], ["`table(nome, casos, corpo, tags=None)`"], ["`tag(*nomes)`"], ["`tap()`"], ["`temp_dir()`"], ["`temp_file(conteudo='', sufixo='.txt')`"], ["`test(nome, corpo, tags=None, prazo=0, repetir=1, dados=None)`"], ["`texts(tamanho_max=20, alfabeto=None)`"], ["`timed(acao, vezes=1)`"], ["`trial(nome, corpo, tags=None, prazo=0, repetir=1, dados=None)`"], ["`vaults(valor=None, tamanho_max=6)`"]]}},
];

const headings = [{ id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-58', text: "Funções (58)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Crucible"}
      description={"Framework de testes: suítes, matchers, fixtures, dublês e benchmark."}
      href={"/docs/biblioteca/crucible"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
