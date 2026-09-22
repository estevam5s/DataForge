// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Checklist de release",
  description: "As doze conferências antes de uma tag — e o comando que faz cada uma.",
};

const blocos: Bloco[] = [
  {"p": "Uma lista que se segue é melhor que um cuidado que se tem. Estas doze saem do que já quebrou em releases de verdade — inclusive neste repositório."},
  {"table": {"head": ["#", "Conferir", "Com"], "rows": [["1", "o formato", "`dataforge fmt . --check`"], ["2", "a análise, com avisos como erro", "`dataforge check . --strict`"], ["3", "os testes, com piso de cobertura", "`dataforge test --minimo=80`"], ["4", "nenhum uso obsoleto", "`DF_OBSOLETOS=erro dataforge test`"], ["5", "o número de versão que a mudança exige", "`dataforge abi anterior.df atual.df`"], ["6", "a versão do `forge.toml` igual à tag", "o workflow de release confere"], ["7", "o CHANGELOG com *Quebra* e *Obsoleto*", "leitura"], ["8", "nenhum segredo no pacote", "`dataforge seguranca . --strict`"], ["9", "o pacote instala numa pasta limpa", "`dataforge pack` + `dataforge add` noutra pasta"], ["10", "o teste importa pelo **nome** do pacote", "`adopt minha_lib`, e não `../src`"], ["11", "os exemplos do README rodam", "extrair e rodar"], ["12", "a licença declarada", "`license` no `forge.toml`"]]}},
  { code: `dataforge fmt . --check && \\
dataforge check . --strict && \\
DF_OBSOLETOS=erro dataforge test --minimo=80 && \\
dataforge seguranca . --strict && \\
dataforge abi v_anterior/src/main.df src/main.df && \\
dataforge pack`, lang: 'bash' },
  {"callout": {"tipo": "dica", "titulo": "Automatize: `dataforge devops github`", "texto": "O workflow de release gerado confere a tag contra o `forge.toml`, roda os testes de novo e publica — ver [Release por tag](/docs/devops/release)."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Checklist de release"}
      description={"As doze conferências antes de uma tag — e o comando que faz cada uma."}
      href={"/docs/bibliotecas/checklist"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
