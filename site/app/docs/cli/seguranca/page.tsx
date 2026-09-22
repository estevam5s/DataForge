// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/cli_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge seguranca",
  description: "Segredo escrito no código e padrão arriscado — em todo arquivo, não só nos .df.",
};

const blocos: Bloco[] = [
  {"p": "Duas varreduras. A primeira acha **segredo pelo formato** — chave da AWS, token do GitHub, `sk_live` da Stripe, bloco de chave privada, token do PyPI —, e por isso acha o que você esqueceu, que é o único tipo que importa. A segunda aplica regras sintáticas: SQL concatenado, shell com interpolação, MD5 para assinatura, senha sem derivação, verificação de certificado desligada."},
  { code: `dataforge seguranca .              # o projeto inteiro
dataforge seguranca src/ --strict  # sai com 1 se houver achado: reprova o CI
dataforge seguranca . --json       # para outra ferramenta
dataforge seguranca . --so=alto    # esconde os medios`, lang: 'bash' },
  {"h2": "O que ela cala, de propósito"},
  {"table": {"head": ["Cala sobre", "Porque"], "rows": [["valor que se anuncia como exemplo", "`sua-senha-aqui`, `AKIA…EXAMPLE`"], ["JWT com papel `anon`", "a chave `anon` do Supabase vai no navegador de propósito — a `service_role` não"], ["credencial de `localhost`", "`postgres://app:app@localhost` num teste é um teste normal"], ["`// df: permitir segredo-no-codigo`", "o escape nomeado, em qualquer arquivo"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Um falso alarme desliga a ferramenta", "texto": "Sem esses silêncios a varredura apontava 19 vezes neste repositório, e as 19 eram falso alarme — inclusive os exercícios que ensinam a não escrever token no arquivo. Uma varredura assim é desligada no mesmo dia, e junto vão os achados de verdade."}},
  {"p": "No CI, antes do commit: [pre-commit](/docs/devops/ambiente-de-dev). O resto do assunto: [Segurança da informação](/docs/seguranca/mapa)."},
];

const headings = [{ id: 'o-que-ela-cala-de-proposito', text: "O que ela cala, de propósito", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge seguranca"}
      description={"Segredo escrito no código e padrão arriscado — em todo arquivo, não só nos .df."}
      href={"/docs/cli/seguranca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
