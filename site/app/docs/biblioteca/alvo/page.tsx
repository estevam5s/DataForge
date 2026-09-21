// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/alvo.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Alvo",
  description: "'Isso roda no navegador?', respondido a partir dos 'adopt'. Seis alvos descritos (servidor, cli, navegador, wasi, funcao serverless, embarcado) com o que cada um suporta e POR QUE nao suporta o resto, no mesmo vocabulario de capacidade do 'Arcane.Capacidade'. A leitura e ESTATICA e o modulo diz isso em 'limites()': um 'roda' quer dizer 'nao achei impedimento por esta via', e nao 'vai funcionar'.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (7)"},
  {"table": {"head": ["Assinatura"], "rows": [["`alvos()`"], ["`conferir(caminho, alvo='servidor')`"], ["`conferir_todos(caminho)`"], ["`exigencias(caminho)`"], ["`limites()`"], ["`porque(alvo, capacidade)`"], ["`relatorio(resultado)`"]]}},
];

const headings = [{ id: 'funcoes-7', text: "Funções (7)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Alvo"}
      description={"'Isso roda no navegador?', respondido a partir dos 'adopt'. Seis alvos descritos (servidor, cli, navegador, wasi, funcao serverless, embarcado) com o que cada um suporta e POR QUE nao suporta o resto, no mesmo vocabulario de capacidade do 'Arcane.Capacidade'. A leitura e ESTATICA e o modulo diz isso em 'limites()': um 'roda' quer dizer 'nao achei impedimento por esta via', e nao 'vai funcionar'."}
      href={"/docs/biblioteca/alvo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
