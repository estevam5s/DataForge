// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O contrato no CI",
  description: "dataforge abi sai com erro quando a versão declarada é menor que a quebra exige — antes do release, e não depois.",
};

const blocos: Bloco[] = [
  {"p": "Conferir a superfície à mão é o tipo de passo que se pula na sexta-feira. No CI ele não é pulado: o job compara o módulo publicado com o de agora, e **reprova** o release que quebra o contrato sem subir a versão maior."},
  { code: `# no CI, com a última versão publicada baixada em ultima/
dataforge abi ultima/src/main.df src/main.df
# sai com 0 (compatível), 2 (quebra) — e o relatório diz qual regra`, lang: 'bash' },
  { code: `adopt Arcane.Abi as Abi
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-abi-{randint(100000, 999999)}"
IO.mkdir(pasta)
antes := $"{pasta}/v1.df"
IO.write(antes, "action somar(a, b):\\n    yield a + b\\naction dobro(x):\\n    yield x * 2\\nrelay somar, dobro\\n")

depois := $"{pasta}/v2.df"
IO.write(depois, "action somar(a):\\n    yield a\\nrelay somar\\n")

versao_declarada := "1.5.0"                         // o que está no forge.toml
calculada := Abi.proxima_versao("1.4.2", antes, depois)["proxima"]
subiu_certo := versao_declarada.split(".")[0] is calculada.split(".")[0]
assert not subiu_certo                             // 1.5.0 numa quebra: reprovar
out $"declarada {versao_declarada}, exigida {calculada}"
IO.remove_tree(pasta)`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que não compila não é julgado", "texto": "Se uma das duas versões não compila, o veredito é `desconhecido` e o job não reprova por contrato — reprova pelo erro de compilação, que é o problema real. Um falso alarme de quebra reprovaria um release correto, e na segunda vez a conferência inteira seria desligada."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"O contrato no CI"}
      description={"dataforge abi sai com erro quando a versão declarada é menor que a quebra exige — antes do release, e não depois."}
      href={"/docs/abi/ci"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
