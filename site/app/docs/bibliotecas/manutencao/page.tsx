// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Manter uma biblioteca",
  description: "Depreciar sem quebrar, o que fazer numa mudança incompatível, e como não abandonar quem depende de você.",
};

const blocos: Bloco[] = [
  {"p": "A parte difícil de uma biblioteca começa depois do `1.0.0`. Tudo o que você publicou está rodando na máquina de alguém, e cada mudança tem de escolher entre **melhorar** e **não quebrar**."},
  {"h2": "Acrescentar é quase sempre seguro"},
  { code: `// antes
action formatar(valor: Float) -> String:
    yield $"R$ {round(valor, 2)}"

// depois — menor, não maior: quem chamava com um argumento continua igual
action formatar(valor: Float, moeda: String := "R$") -> String:
    yield $"{moeda} {round(valor, 2)}"
`, lang: 'df' },
  {"p": "Parâmetro novo **com padrão**, campo novo **com padrão**, ação nova no `relay`: tudo isso é versão menor. A armadilha é o parâmetro novo **sem** padrão — e a linguagem recusa declará-lo depois de um com padrão, o que evita metade dos casos."},
  {"h2": "Depreciar: avise antes de remover"},
  {"p": "Remover na hora quebra; remover depois de um ciclo de aviso não. A sequência tem três etapas e leva uma versão maior:"},
  { code: `// 1.5.0 — o novo nasce, o velho continua e avisa
action validar_cpf(texto: String) -> Boolean:
    yield len(texto) is 11

action cpf(texto: String) -> Boolean:
    // descontinuada em 1.5.0, sai na 2.0.0
    out "aviso: V.cpf virou V.validar_cpf; ela sai na 2.0.0"
    yield validar_cpf(texto)

relay validar_cpf, cpf
`, lang: 'df' },
  {"list": ["**1.5.0** — o nome novo aparece; o antigo continua funcionando e avisa.", "**1.x** seguintes — o CHANGELOG repete o aviso.", "**2.0.0** — o antigo sai, e a nota de versão diz exatamente o que fazer."], "ordered": true},
  {"p": "O aviso precisa dizer **o que usar no lugar**. Um \"descontinuado\" sem substituto só transfere o problema."},
  {"h2": "Quando a quebra é inevitável"},
  {"table": {"head": ["Faça", "Porque"], "rows": [["suba o **maior**", "é a única sinalização que o resolvedor entende"], ["escreva o caminho de migração", "\"o que mudou\" sem \"o que fazer\" custa uma tarde a cada usuário"], ["mantenha a linha antiga viva por um tempo", "correção de segurança em `1.x` enquanto a `2.x` amadurece"], ["quebre **uma vez**, e não aos poucos", "três versões maiores em seis meses é pior que uma com três quebras"]]}},
  {"h2": "O CHANGELOG é para quem atualiza"},
  { code: `## 2.0.0

### Quebrado
- \`V.cpf\` saiu. Use \`V.validar_cpf\`, que tem a mesma assinatura.
- \`V.email\` devolve um record em vez de Boolean:
      antes:  given V.email(x):
      agora:  given V.email(x).valido:

### Adicionado
- \`V.cep\`, com os dois formatos.
`, lang: 'text' },
  {"p": "A seção **Quebrado** vem primeiro e mostra as duas linhas — a de antes e a de agora. É o que transforma uma atualização numa busca-e-substitui em vez de uma investigação."},
  {"h2": "Segurança"},
  {"list": ["Uma correção de segurança sai como **correção** em todas as linhas ainda vivas, e não só na mais nova.", "A nota diz **o que estava exposto** e **desde quando** — sem isso ninguém sabe se foi afetado.", "Se um segredo vazou dentro de um tarball publicado, ele está comprometido: **rotacione**, e publique uma versão nova. Despublicar não desfaz o download de ninguém."]},
  {"h2": "Abandonar com honestidade"},
  {"p": "Uma biblioteca sem manutenção é comum e legítimo. O que faz diferença é dizer: uma linha no README — \"não tenho mantido isto; `outra-lib` faz o mesmo\" — economiza horas de quem estava prestes a adotá-la, e é mais útil que qualquer último commit."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/bibliotecas/contrato", "title": "O contrato", "desc": "o que está em jogo em cada mudança"}, {"href": "/docs/versoes", "title": "Versões e estabilidade", "desc": "como a própria linguagem trata isso"}]},
];

const headings = [{ id: 'acrescentar-e-quase-sempre-seguro', text: "Acrescentar é quase sempre seguro", level: 2 as const }, { id: 'depreciar-avise-antes-de-remover', text: "Depreciar: avise antes de remover", level: 2 as const }, { id: 'quando-a-quebra-e-inevitavel', text: "Quando a quebra é inevitável", level: 2 as const }, { id: 'o-changelog-e-para-quem-atualiza', text: "O CHANGELOG é para quem atualiza", level: 2 as const }, { id: 'seguranca', text: "Segurança", level: 2 as const }, { id: 'abandonar-com-honestidade', text: "Abandonar com honestidade", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Manter uma biblioteca"}
      description={"Depreciar sem quebrar, o que fazer numa mudança incompatível, e como não abandonar quem depende de você."}
      href={"/docs/bibliotecas/manutencao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
