// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Versão e compatibilidade",
  description: "Semver na prática: o que cada número promete, como o resolvedor lê a faixa, e por que conflito é erro.",
};

const blocos: Bloco[] = [
  {"p": "A versão de uma biblioteca é uma **promessa legível por máquina**. Ela responde a uma pergunta só: *posso atualizar sem ler o changelog?*"},
  { code: `1.4.2
│ │ └── correção   — consertou algo, sem mudar o contrato
│ └──── menor      — acrescentou algo, sem quebrar o que havia
└────── maior      — quebrou alguma coisa
`, lang: 'text' },
  {"h2": "O que cabe em cada número"},
  {"table": {"head": ["Mudança", "Sobe"], "rows": [["corrigir um cálculo errado", "correção (`1.4.2` → `1.4.3`)"], ["melhorar a mensagem de um erro", "correção"], ["trocar a implementação interna", "correção"], ["**acrescentar** uma ação ao `relay`", "menor (`1.4.2` → `1.5.0`)"], ["acrescentar um parâmetro **com padrão**", "menor"], ["acrescentar um campo com padrão a um record", "menor"], ["renomear ou remover algo público", "**maior** (`1.4.2` → `2.0.0`)"], ["trocar o **tipo** de um erro levantado", "**maior**"], ["tornar obrigatório um parâmetro que era opcional", "**maior**"], ["mudar o que uma ação devolve", "**maior**"]]}},
  {"callout": {"tipo": "atencao", "titulo": "As três linhas de baixo são as esquecidas", "texto": "Trocar o tipo do erro quebra em silêncio — o `handle` de quem usa para de capturar e o erro sobe. Mudar o retorno de `Vault` para `record` quebra toda leitura por chave. Nenhuma das duas parece \"quebrar\" enquanto se escreve."}},
  {"h2": "A faixa, do lado de quem depende"},
  { code: `[dependencies]
validador = "^1.2.0"      # >=1.2.0 e <2.0.0   — aceita correção e menor
tabela    = "~1.2.0"      # >=1.2.0 e <1.3.0   — só correção
datas     = "1.2.3"       # exatamente essa
cofre     = ">=1.0 <3.0"  # comparadores, combináveis
texto     = "*"           # qualquer uma
`, lang: 'toml' },
  {"p": "`^` é o padrão razoável: ele confia no semver de quem publicou. `~` é para quando essa confiança ainda não existe, e a versão exata é para quando existe um motivo escrito."},
  {"h2": "Antes de 1.0.0"},
  {"p": "Enquanto o maior é `0`, o contrato ainda está sendo decidido, e a convenção é que o **menor** carrega as quebras: `0.3.0` pode quebrar `0.2.0`. Publicar `1.0.0` é a declaração de que o contrato está de pé — e é a partir dali que ele custa caro para mudar."},
  {"h2": "Conflito é erro, e não aviso"},
  {"p": "Se dois pacotes pedem faixas incompatíveis do mesmo terceiro, `dataforge install` **falha**, dizendo quem pediu o quê. A alternativa — instalar duas cópias em versões diferentes — produz o pior tipo de bug: dois `record` com o mesmo nome e campos distintos circulando no mesmo programa, e um `with` que recusa o próprio resultado."},
  {"h2": "O lockfile"},
  {"table": {"head": ["Arquivo", "Guarda", "Versionar?"], "rows": [["`forge.toml`", "o que você **pediu** (faixas)", "sim"], ["`forge.lock`", "o que foi **instalado** (versões exatas + sha256)", "sim"], ["`forge_modules/`", "os arquivos", "não"]]}},
  {"p": "O lock é o que faz a instalação de hoje ser igual à de três meses atrás — e o `sha256` é o que faz \"a mesma versão\" significar \"os mesmos bytes\"."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/bibliotecas/publicar", "title": "Publicar", "desc": "empacotar e mandar para o registro"}, {"href": "/docs/pacotes", "title": "O gerenciador", "desc": "add, install, search e o resolvedor"}]},
];

const headings = [{ id: 'o-que-cabe-em-cada-numero', text: "O que cabe em cada número", level: 2 as const }, { id: 'a-faixa-do-lado-de-quem-depende', text: "A faixa, do lado de quem depende", level: 2 as const }, { id: 'antes-de-100', text: "Antes de 1.0.0", level: 2 as const }, { id: 'conflito-e-erro-e-nao-aviso', text: "Conflito é erro, e não aviso", level: 2 as const }, { id: 'o-lockfile', text: "O lockfile", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Versão e compatibilidade"}
      description={"Semver na prática: o que cada número promete, como o resolvedor lê a faixa, e por que conflito é erro."}
      href={"/docs/bibliotecas/versao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
