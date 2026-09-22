// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Guia de migração",
  description: "Numa versão maior, o guia que diz a cada pessoa o que trocar — com a busca que acha cada uso.",
};

const blocos: Bloco[] = [
  {"p": "Uma versão maior sem guia de migração deixa cada pessoa descobrir sozinha o que quebrou. O guia é uma tabela: o que era, o que é agora, e como achar cada uso no próprio código."},
  { code: `# Migrar da 1.x para a 2.0

| Era (1.x)                 | Agora (2.0)                    | Achar                         |
|---------------------------|--------------------------------|-------------------------------|
| \`total(itens)\`            | \`calcular_total(itens)\`        | \`grep -rn "\\.total(" src/\`    |
| \`frete(uf)\`               | \`calcular_frete(uf, peso := 1)\` | \`grep -rn "\\.frete(" src/\`    |
| \`Pedido.cliente\` (texto)  | \`Pedido.cliente\` (record)       | \`dataforge check\` acusa        |`, lang: 'text', title: `MIGRACAO.md` },
  {"list": ["Uma versão menor **antes**, com tudo que vai sair marcado com `obsoleta` — quem roda com `DF_OBSOLETOS=erro` acha cada uso sozinho.", "O guia lista cada quebra com o **como achar**: um `grep`, ou *“o `check` acusa”* quando o tipo mudou.", "Onde der, mantenha o nome velho por uma versão com `Evolucao.renomeada` — ele funciona e avisa."], "ordered": true},
  { code: `adopt Arcane.Evolucao as Ev

action calcular_total(itens):
    yield sum(itens)

// O nome velho, por mais uma versao: funciona e avisa.
total := Ev.renomeada(calcular_total, "total", "2.0")
assert total([1, 2, 3]) is 6
assert Ev.avisos()[0]["acao"] is "total"`, lang: 'df' },
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Guia de migração"}
      description={"Numa versão maior, o guia que diz a cada pessoa o que trocar — com a busca que acha cada uso."}
      href={"/docs/bibliotecas/migracao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
