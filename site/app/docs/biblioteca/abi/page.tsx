// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/abi.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Abi",
  description: "A superficie de um modulo e o CONTRATO dele, e quebra-la e o mesmo problema que quebrar uma ABI — com outro nome e o mesmo sintoma: nao e erro de quem publicou, e erro de quem consome, depois. Compara duas versoes e diz o que quebrou (simbolo removido, aridade incompativel, parametro renomeado, tipo trocado, campo novo obrigatorio) e qual bump de semver a mudanca EXIGE. Mais o mapa de simbolos: de onde vem cada nome, o analogo do mapa que um ligador escreve.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (10)"},
  {"table": {"head": ["Assinatura"], "rows": [["`changelog(antes, depois, versao='')`"], ["`comparar(antes, depois)`"], ["`compativel(antes, depois)`"], ["`mapa(caminho)`"], ["`proxima_versao(atual, antes, depois)`"], ["`quebras(antes, depois)`"], ["`regras()`"], ["`relatorio(resultado)`"], ["`superficie(caminho)`"], ["`veredito(antes, depois)`"]]}},
];

const headings = [{ id: 'funcoes-10', text: "Funções (10)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Abi"}
      description={"A superficie de um modulo e o CONTRATO dele, e quebra-la e o mesmo problema que quebrar uma ABI — com outro nome e o mesmo sintoma: nao e erro de quem publicou, e erro de quem consome, depois. Compara duas versoes e diz o que quebrou (simbolo removido, aridade incompativel, parametro renomeado, tipo trocado, campo novo obrigatorio) e qual bump de semver a mudanca EXIGE. Mais o mapa de simbolos: de onde vem cada nome, o analogo do mapa que um ligador escreve."}
      href={"/docs/biblioteca/abi"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
