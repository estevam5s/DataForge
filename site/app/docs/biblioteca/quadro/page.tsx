// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/quadro.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Quadro",
  description: "A tabela de dados: colunas nomeadas e linhas como vault. Filtrar, agrupar, resumir, juntar, pivotar, limpar a ausência e a duplicata, converter tipos, normalizar, codificar e descrever — colunar por dentro, imutável por fora.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (10)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Grupo(quadro, chaves)`"], ["`Quadro(colunas=None, dados=None)`"], ["`agregacoes()`"], ["`ausente(valor)`"], ["`de_colunas(vault)`"], ["`de_csv(caminho, separador=',', tipos=True)`"], ["`de_json(caminho)`"], ["`de_vaults(linhas)`"], ["`tipos()`"], ["`vazio(colunas=None)`"]]}},
];

const headings = [{ id: 'funcoes-10', text: "Funções (10)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Quadro"}
      description={"A tabela de dados: colunas nomeadas e linhas como vault. Filtrar, agrupar, resumir, juntar, pivotar, limpar a ausência e a duplicata, converter tipos, normalizar, codificar e descrever — colunar por dentro, imutável por fora."}
      href={"/docs/biblioteca/quadro"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
