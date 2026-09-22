// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O analisador estático",
  description: "Nomes, aridade, tipos, alcance, membros atravessando arquivos — e a regra de só falar quando consegue provar.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge check` roda o analisador sobre a árvore, sem executar nada. Ele pega o erro que num arquivo pequeno aparece na primeira execução — e que num sistema de duzentos arquivos aparece em produção."},
  {"table": {"head": ["Pega", "Exemplo"], "rows": [["nome não definido, com sugestão", "`totl` → \"você quis dizer 'total'?\""], ["aridade", "`somar(1)` numa ação de dois parâmetros"], ["tipo de parâmetro e de retorno", "`dobro(\"x\")` com `n: Integer`"], ["membro que não existe", "`p.clientte` num record — também atravessando `adopt`"], ["código inalcançável", "depois de `yield`, ou `point` depois de uma captura"], ["ciclo de import", "com a cadeia inteira: `a.df → b.df → a.df`"], ["escrita concorrente", "uma rota escrevendo num nome de fora"], ["`??` que engole comparação", "`v[k] ?? void is void`"]]}},
  {"h2": "Otimista de propósito"},
  {"p": "Quando não consegue **provar** que algo está errado, ele cala. Um falso alarme ensina a ignorar mensagens — e aí o alarme verdadeiro é ignorado junto. Por isso ele se cala sobre o membro de um blueprint que herda de algo não visto, sobre o tipo depois de uma ação decorada, e sobre a chave de um vault que alguém escreveu em outro lugar."},
  { code: `adopt Arcane.Compilador as Comp

// o analisador vê o fluxo: 'y' só existe num dos caminhos
aviso := Comp.onde_talvez_nao_definidas("action f(x):\\n    given x bigger 0:\\n        y := 1\\n    yield y\\n")
out aviso`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Silenciar uma regra, nomeando-a", "texto": "`// df: permitir <regra>` na linha, ou na de cima. A regra tem de ser nomeada: um `permitir` solto esconderia o próximo erro, que ninguém pediu para esconder."}},
];

const headings = [{ id: 'otimista-de-proposito', text: "Otimista de propósito", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O analisador estático"}
      description={"Nomes, aridade, tipos, alcance, membros atravessando arquivos — e a regra de só falar quando consegue provar."}
      href={"/docs/compilador/analisador"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
