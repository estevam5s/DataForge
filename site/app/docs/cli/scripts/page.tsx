// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/cli_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A CLI em scripts",
  description: "Códigos de saída, cor, idioma, variáveis de ambiente, eval — e o que um script pode confiar.",
};

const blocos: Bloco[] = [
  {"p": "A CLI é usada por gente e por programa. Para o programa, o que importa é o que não muda: o **código de saída**, a saída sem cor, e as variáveis de ambiente que mudam o comportamento."},
  {"h2": "Códigos de saída"},
  {"table": {"head": ["Código", "Significa"], "rows": [["`0`", "deu certo — inclusive `check` com avisos (use `--strict` para reprovar)"], ["`1`", "falhou: erro no programa, teste reprovado, erro de análise, quebra de ABI"], ["`2`", "o seu programa pediu — `OS.exit(2)` sai com o código que você escolher"]]}},
  {"h2": "Variáveis de ambiente"},
  {"table": {"head": ["Variável", "Efeito"], "rows": [["`NO_COLOR=1` ou `--no-color`", "sem códigos de cor — para log e CI"], ["`DF_IDIOMA=en`", "as mensagens em inglês (o padrão é português)"], ["`DATAFORGE_SEM_TROCA=1`", "ignora o pino de versão do `forge.toml`"], ["`DATAFORGE_REGISTRY`", "o registro de pacotes"], ["`DF_ATUALIZAR_SNAPSHOT=1`", "aceita as mudanças dos instantâneos"], ["`DATABASE_URL`", "a conexão que `Forge.de_ambiente()` lê"]]}},
  {"h2": "Uma linha, sem arquivo"},
  { code: `dataforge eval 'out 2 ** 10'
dataforge eval 'out [1, 2, 3] >> morph n: n * 2'
dataforge --version            # o que o instalador e o CI conferem
dataforge converter script.py  # um ponto de partida, a partir de Python`, lang: 'bash' },
  {"h2": "Numa esteira"},
  { code: `#!/bin/sh
set -e                                    # para no primeiro codigo diferente de zero
export NO_COLOR=1
dataforge fmt . --check
dataforge check . --strict --formato=github
dataforge seguranca . --strict
dataforge test --minimo=80
dataforge abi v1/lib.df src/lib.df        # 1 se a versao nova quebra`, lang: 'bash' },
  {"callout": {"tipo": "atencao", "titulo": "`--version`, e não a ajuda", "texto": "`dataforge --version` sai com a versão e o Python, e nada mais — é o que todo script chama para conferir a instalação. Ele caía no ramo sem argumentos e imprimia a ajuda inteira, que nenhum script sabe ler."}},
  {"p": "Continue em [Referência completa](/docs/cli/referencia)."},
];

const headings = [{ id: 'codigos-de-saida', text: "Códigos de saída", level: 2 as const }, { id: 'variaveis-de-ambiente', text: "Variáveis de ambiente", level: 2 as const }, { id: 'uma-linha-sem-arquivo', text: "Uma linha, sem arquivo", level: 2 as const }, { id: 'numa-esteira', text: "Numa esteira", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A CLI em scripts"}
      description={"Códigos de saída, cor, idioma, variáveis de ambiente, eval — e o que um script pode confiar."}
      href={"/docs/cli/scripts"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
