// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/forge.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Forge",
  description: "Banco de dados: SQLite, Postgres, MySQL, Redis e MongoDB pela mesma interface.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (28)"},
  {"table": {"head": ["Assinatura"], "rows": [["`buscar_modelo(nome)`"], ["`colunas(db, t)`"], ["`conectar(url, **opcoes)`"], ["`conexao(pool)`"], ["`consultar(conexao, sql, parametros=None)`"], ["`de(conexao, tabela)`"], ["`de_csv(caminho_ou_texto)`"], ["`dialetos()`"], ["`executar(conexao, sql, parametros=None)`"], ["`fechar(db)`"], ["`ligar(modelo, conexao)`"], ["`limpar_modelos()`"], ["`memoria()`"], ["`migracoes(conexao)`"], ["`migrar_tudo(conexao)`"], ["`modelo(nome, campos=None, opcoes=None)`"], ["`modelos()`"], ["`motores()`"], ["`para_csv(linhas, caminho='')`"], ["`ping(db)`"], ["`pool(url, tamanho=5, **o)`"], ["`primeiro(conexao, sql, parametros=None)`"], ["`tabela(conexao, tabela)`"], ["`tabelas(db)`"], ["`tipos()`"], ["`transacao(conexao, corpo)`"], ["`url(url)`"], ["`versao(db)`"]]}},
];

const headings = [{ id: 'funcoes-28', text: "Funções (28)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Forge"}
      description={"Banco de dados: SQLite, Postgres, MySQL, Redis e MongoDB pela mesma interface."}
      href={"/docs/biblioteca/forge"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
