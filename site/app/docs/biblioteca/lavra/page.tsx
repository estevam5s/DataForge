// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/lavra.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Lavra",
  description: "A consulta tipada: o cliente diz exatamente quais campos quer, numa consulta indentada, e recebe exatamente aqueles. O esquema nasce dos 'record' que já existem; traz resolvedores, contexto, trechos, variáveis, diretivas, contratos, uniões, introspecção, validação antes de executar, lote contra o N+1, paginação por cursor, limites de profundidade e custo, assinaturas por WebSocket e federação de vários serviços.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (42)"},
  {"table": {"head": ["Assinatura"], "rows": [["`assinatura(esq, nome, tipo_do_campo, resolve=None, args=None, descricao='', custo=1)`"], ["`busca(esq, nome, tipo_do_campo, resolve=None, args=None, descricao='', custo=1)`"], ["`campo(esq, tipo_nome, nome, tipo_do_campo, resolve=None, args=None, descricao='', obsoleto='', custo=1)`"], ["`cliente(url, cabecalhos=None, tempo_limite=10.0)`"], ["`conferir(esq)`"], ["`contexto(dados=None)`"], ["`contrato(esq, nome, campos, descricao='', resolve_tipo=None)`"], ["`descrever(esq)`"], ["`diretiva(esq, nome, decidir)`"], ["`em_segundo_plano(esquema, porta=0, host='127.0.0.1', caminho='/lavra', contexto_de=None)`"], ["`entao(promessa, acao)`"], ["`entrada(esq, alvo, nome=None, descricao='', campos=None)`"], ["`enum(esq, nome, valores, descricao='')`"], ["`erro(mensagem, codigo='erro', extra=None)`"], ["`escalar(esq, nome, serializa=None, desserializa=None, descricao='')`"], ["`esquema(nome='lavra')`"], ["`estender(p, tipo_nome, campo_nome, tipo_do_campo, resolve=None, args=None, descricao='', custo=1)`"], ["`executar(esq, texto, variaveis=None, contexto=None, raiz=None, operacao=None, validar_antes=True)`"], ["`fonte(nome='fonte')`"], ["`introspeccao(esq, ligada=True)`"], ["`juntar(p, servico, esquema)`"], ["`ler(texto)`"], ["`limites(esq, profundidade=None, complexidade=None, itens=None)`"], ["`local(esquema, contexto=None)`"], ["`lote(ctx, nome, buscar)`"], ["`lotes(ctx)`"], ["`mapa(p)`"], ["`montar(app, esquema, caminho='/lavra', contexto_de=None, permitir_get=True, introspeccao_publica=True)`"], ["`montar_assinaturas(app, esquema, caminho='/lavra/assinar', contexto_de=None)`"], ["`mudanca(esq, nome, tipo_do_campo, resolve=None, args=None, descricao='', custo=1)`"], ["`pagina(itens, primeiros=None, depois=None, total=None)`"], ["`parar(app)`"], ["`pedir(ctx, nome, chave)`"], ["`portao(nome='portao')`"], ["`preencher(ctx, nome, chave, valor)`"], ["`recusar(mensagem='sem permissão', extra=None)`"], ["`servir(esquema, porta=8080, host='127.0.0.1', caminho='/lavra', contexto_de=None, silencioso=False)`"], ["`texto_do_esquema(esq)`"], ["`tipo(esq, alvo, nome=None, descricao='', cumpre=None, campos=None, esconder=None)`"], ["`tipo_pagina(esq, nome_do_item, nome=None)`"], ["`uniao(esq, nome, membros, descricao='', resolve_tipo=None)`"], ["`validar(esq, texto, operacao=None)`"]]}},
];

const headings = [{ id: 'funcoes-42', text: "Funções (42)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Lavra"}
      description={"A consulta tipada: o cliente diz exatamente quais campos quer, numa consulta indentada, e recebe exatamente aqueles. O esquema nasce dos 'record' que já existem; traz resolvedores, contexto, trechos, variáveis, diretivas, contratos, uniões, introspecção, validação antes de executar, lote contra o N+1, paginação por cursor, limites de profundidade e custo, assinaturas por WebSocket e federação de vários serviços."}
      href={"/docs/biblioteca/lavra"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
