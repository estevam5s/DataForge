// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/qualidade.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Qualidade",
  description: "Qualidade de dados: as seis dimensões, perfil, validação e limpeza.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (16)"},
  {"table": {"head": ["Assinatura"], "rows": [["`atualidade(linhas, campo, dias=1)`"], ["`completude(linhas, campos=None)`"], ["`conferir(linhas, regras, parar_em=0)`"], ["`deriva(esperado, recebido)`"], ["`duplicadas(linhas, campos)`"], ["`esperar(linhas, regras, minimo=1.0)`"], ["`esquema_de(linhas, amostra=0)`"], ["`exigir_esquema(linhas, esperado, amostra=0)`"], ["`fora_da_faixa(linhas, campo, minimo=None, maximo=None)`"], ["`formatos()`"], ["`perfil(linhas, amostra=0)`"], ["`preencher(linhas, padroes)`"], ["`relatorio(resultado, largura=72)`"], ["`sem_duplicadas(linhas, campos=None)`"], ["`so_validas(linhas, regras)`"], ["`unicidade(linhas, campo)`"]]}},
];

const headings = [{ id: 'funcoes-16', text: "Funções (16)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Qualidade"}
      description={"Qualidade de dados: as seis dimensões, perfil, validação e limpeza."}
      href={"/docs/biblioteca/qualidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
