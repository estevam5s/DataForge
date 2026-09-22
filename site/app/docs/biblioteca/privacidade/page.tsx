// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/privacidade.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Privacidade",
  description: "O que a LGPD pede, como operações sobre dado: pseudonimização com chave (e não hash sem chave, que se desfaz), generalização de quase-identificadores, a medida do k-anonimato, minimização por lista de permitidos, retenção, consentimento por titular e por finalidade com histórico, os direitos de acesso e eliminação percorrendo todo lugar onde o dado mora, e contagem com privacidade diferencial.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (10)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Consentimentos()`"], ["`Titulares()`"], ["`consentimentos()`"], ["`contagem_privada(n, epsilon=1.0, semente=None)`"], ["`generalizar(valor, tipo, nivel=1)`"], ["`k_anonimato(linhas, quase_identificadores)`"], ["`minimizar(linha, permitidos)`"], ["`pseudonimizar(valor, chave, finalidade='', tamanho=16)`"], ["`titulares()`"], ["`vencidos(linhas, campo_data, dias, agora=None)`"]]}},
];

const headings = [{ id: 'funcoes-10', text: "Funções (10)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Privacidade"}
      description={"O que a LGPD pede, como operações sobre dado: pseudonimização com chave (e não hash sem chave, que se desfaz), generalização de quase-identificadores, a medida do k-anonimato, minimização por lista de permitidos, retenção, consentimento por titular e por finalidade com histórico, os direitos de acesso e eliminação percorrendo todo lugar onde o dado mora, e contagem com privacidade diferencial."}
      href={"/docs/biblioteca/privacidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
