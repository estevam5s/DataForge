// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/lago.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Lago",
  description: "Data Lake: Parquet nativo, partições Hive, camadas bronze/prata/ouro e compactação.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (18)"},
  {"table": {"head": ["Assinatura"], "rows": [["`acrescentar(lago, tabela, linhas, particoes=None, compressao='gzip')`"], ["`arquivos(lago, tabela, filtro=None)`"], ["`camada(lago, nome)`"], ["`compactar(lago, tabela, minimo=2)`"], ["`esquema(lago, tabela)`"], ["`esquema_parquet(caminho)`"], ["`eventos(lago, quantos=20)`"], ["`gravar(lago, tabela, linhas, particoes=None, compressao='gzip')`"], ["`gravar_parquet(caminho, linhas, compressao='gzip')`"], ["`lago(raiz)`"], ["`ler(lago, tabela, filtro=None, colunas=None, limite=0)`"], ["`ler_parquet(caminho, colunas=None)`"], ["`particoes(lago, tabela)`"], ["`promover(lago, tabela, de, para, transformar=None, particoes=None)`"], ["`remover_particao(lago, tabela, filtro)`"], ["`tabelas(lago)`"], ["`tamanho(lago, tabela='')`"], ["`vacuo(lago)`"]]}},
];

const headings = [{ id: 'funcoes-18', text: "Funções (18)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Lago"}
      description={"Data Lake: Parquet nativo, partições Hive, camadas bronze/prata/ouro e compactação."}
      href={"/docs/biblioteca/lago"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
