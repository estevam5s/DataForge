// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gestão de segredos",
  description: "Onde o segredo mora, como ele não aparece em log, como é achado no código — e o que fazer quando vaza.",
};

const blocos: Bloco[] = [
  {"p": "Um segredo tem quatro momentos: onde ele **mora**, como ele **passa** pelo programa, como ele **não aparece** onde não devia, e o que se faz quando ele **vaza**. Cada um tem uma ferramenta aqui."},
  {"table": {"head": ["Momento", "Onde", "Ferramenta"], "rows": [["mora", "variável de ambiente, cofre do provedor, KMS — **nunca** o repositório", "`OS.env`, `.env` no `.gitignore`"], ["passa", "dentro de um `Segredo`, que não se imprime", "`Seguranca.segredo(valor)` → `revelar()`"], ["não aparece", "log, erro, relatório", "`redigir(texto)`, `mascarar_no_log` no CI"], ["vaza", "commit, log público, print de tela", "`procurar_segredos`, `dataforge seguranca` — e **rotacionar**"]]}},
  { code: `adopt Arcane.Seguranca as S

s := S.segredo("sk_live_" + "x" * 24, "stripe")
out s                          // nao aparece
assert "sk_live" not in str(s)
assert s.revelar().startswith("sk_live")   // so onde for preciso — e aparece na revisao

log := "conectando com postgres://app:s3nh4-forte@db:5432/loja"
limpo := S.redigir(log)
out limpo
assert "s3nh4-forte" not in limpo

achados := S.procurar_segredos("chave := \\"ghp_" + "R8tK2mQ9vX4pL7nZ3wB6yH1cJ5dF0sG8aE2u" + "\\"")
assert len(achados) is 1
out $"achado: {achados[0]['tipo']} na linha {achados[0]['linha']}"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Um segredo commitado é um segredo vazado", "texto": "Apagar no commit seguinte não o tira do histórico, e um repositório público é espelhado em minutos. A única resposta é **rotacionar**: gerar outro, trocar onde é usado, revogar o velho. `Arcane.Chaves` foi desenhado para que rotacionar não quebre o que a chave velha cifrou."}},
  {"p": "Antes do commit: [pre-commit](/docs/devops/ambiente-de-dev). O ciclo da chave: [Criptografia e chaves](/docs/seguranca/criptografia)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Gestão de segredos"}
      description={"Onde o segredo mora, como ele não aparece em log, como é achado no código — e o que fazer quando vaza."}
      href={"/docs/seguranca/segredos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
