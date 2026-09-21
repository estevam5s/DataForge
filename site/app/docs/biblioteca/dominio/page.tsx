// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/dominio.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Dominio",
  description: "As pecas de um modelo de dominio que se sustenta (DDD): valor (igualdade por conteudo, imutavel, com regra cobrada na criacao), entidade (igualdade por identidade), agregado (a unica porta de escrita, com invariantes conferidas na SAIDA de cada comando e desfazer quando o comando falha no meio), evento (um fato no passado, imutavel), regra (condicao de negocio que se combina com e/ou/nao e explica o \"nao\"), repositorio (guarda agregados INTEIROS), unidade de trabalho (confirma tudo ou nada, e so entao publica) e contexto delimitado (com a traducao que atravessa a fronteira).",
};

const blocos: Bloco[] = [
  {"h2": "Funções (18)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Agregado(tipo, identidade=None, **estado)`"], ["`Contexto(nome)`"], ["`Entidade(tipo, identidade=None, **estado)`"], ["`Evento(nome, dados=None, origem='', tipo='')`"], ["`Regra(descricao, condicao)`"], ["`Repositorio(tipo, ler=None, gravar=None, apagar=None, listar=None)`"], ["`Unidade(publicar=None)`"], ["`Valor(nome, campos, valores, regra=None, motivo='')`"], ["`agregado(tipo, identidade=None, **estado)`"], ["`contexto(nome)`"], ["`entidade(tipo, identidade=None, **estado)`"], ["`evento(nome, dados=None, origem='', tipo='')`"], ["`novo_id()`"], ["`regra(descricao, condicao)`"], ["`repositorio(tipo)`"], ["`repositorio_de(tipo, ler, gravar, apagar=None, listar=None)`"], ["`unidade(publicar=None)`"], ["`valor(nome, campos, regra=None, motivo='')`"]]}},
];

const headings = [{ id: 'funcoes-18', text: "Funções (18)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Dominio"}
      description={"As pecas de um modelo de dominio que se sustenta (DDD): valor (igualdade por conteudo, imutavel, com regra cobrada na criacao), entidade (igualdade por identidade), agregado (a unica porta de escrita, com invariantes conferidas na SAIDA de cada comando e desfazer quando o comando falha no meio), evento (um fato no passado, imutavel), regra (condicao de negocio que se combina com e/ou/nao e explica o \"nao\"), repositorio (guarda agregados INTEIROS), unidade de trabalho (confirma tudo ou nada, e so entao publica) e contexto delimitado (com a traducao que atravessa a fronteira)."}
      href={"/docs/biblioteca/dominio"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
