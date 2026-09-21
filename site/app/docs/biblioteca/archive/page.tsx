// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/archive.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Archive",
  description: "Zip e tar: compactar, listar, conferir e extrair recusando Zip Slip e zip bomb. Comprime e descomprime VALORES em memória, em deflate cru ou em gzip, com a taxa medida.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (13)"},
  {"table": {"head": ["Assinatura"], "rows": [["`acrescentar(arquivo, caminho, nome='')`"], ["`compactar(origem, destino, nivel=6)`"], ["`compactar_tar(origem, destino, compressao='gz')`"], ["`comprimir(dados, nivel=6)`"], ["`conferir(arquivo)`"], ["`de_gzip(dados, como_texto=False)`"], ["`descomprimir(dados, como_texto=False)`"], ["`extrair(arquivo, destino='.', senha='')`"], ["`extrair_tar(arquivo, destino='.')`"], ["`gzip(dados, nivel=6)`"], ["`ler_de(arquivo, nome, senha='')`"], ["`listar(arquivo)`"], ["`taxa(original, comprimido)`"]]}},
];

const headings = [{ id: 'funcoes-13', text: "Funções (13)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Archive"}
      description={"Zip e tar: compactar, listar, conferir e extrair recusando Zip Slip e zip bomb. Comprime e descomprime VALORES em memória, em deflate cru ou em gzip, com a taxa medida."}
      href={"/docs/biblioteca/archive"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
