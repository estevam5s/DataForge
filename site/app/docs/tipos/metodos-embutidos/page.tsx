// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/tipos_literais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O método que não existe",
  description: "O check acusava p.clientte num record e calava em \"ana\".naoExiste(). A conferência agora vale para os dois, e a lista de métodos é lida do interpretador.",
};

const blocos: Bloco[] = [
  {"p": "A forma mais comum de erro de digitação numa linguagem é chamar um método que não existe. O `dataforge check` acusava isso num `record` e num `blueprint` — com sugestão — e **calava** num texto, num cluster e num vault."},
  {"h2": "A medida"},
  {"p": "Quinze erros que **falham em execução**, conferidos contra o que o `check` pegava antes de rodar. Ele pegava oito. Dos sete silêncios, quatro eram este mesmo caso em tipos diferentes:"},
  { code: `nome := "ana"
xs := [1, 2, 3]

// Os dois abaixo sao acusados agora, com sugestao:
//   nome.uppper()   ->  'String' has no method 'uppper'
//                       sugestão: Você quis dizer 'upper'?
//   xs.apend(3)     ->  'Cluster' has no method 'apend'
//                       sugestão: Você quis dizer 'append'?

assert nome.upper() is "ANA"
xs.append(4)
assert len(xs) is 4
out "o mesmo erro, o mesmo tratamento"
`, lang: 'df' },
  {"h2": "A lista vem do interpretador"},
  {"p": "As tabelas de método de texto e de cluster moram em `dataforge/interpreter.py`, e o analisador as **lê de lá**. Uma segunda lista divergiria no primeiro método novo — e a divergência não daria erro: ela faria o analisador acusar um método que funciona, que é o falso alarme que ensina a desligar a verificação."},
  {"h2": "Onde ele cala, e por quê"},
  {"table": {"head": ["Cala sobre", "Porque"], "rows": [["um **Vault**", "`v.cidade` cai na chave quando ela existe — acusar exigiria saber as chaves"], ["um objeto vindo de `adopt Python.x`", "ali o membro é resolvido pelo Python, e a análise não sabe quais são"], ["um nome começando com `_`", "é combinado entre quem escreveu, não um engano"], ["um tipo que ele não conseguiu inferir", "a regra de sempre: sem prova, silêncio"]]}},
  {"callout": {"tipo": "nota", "titulo": "Zero falso alarme em 532 arquivos", "texto": "A calibragem foi feita rodando o `check` sobre `examples`, `exercicios`, `projetos`, `packages` e `trilha` — as cinco pastas do repositório. Nenhum arquivo que funciona passou a ser acusado."}},
  {"cards": [{"href": "/docs/faq/tipos", "title": "FAQ: tipos", "desc": "o que é conferido, e quando"}, {"href": "/docs/biblioteca", "title": "A biblioteca", "desc": "os métodos de cada tipo"}, {"href": "/docs/erros", "title": "Códigos de erro", "desc": "o catálogo"}]},
];

const headings = [{ id: 'a-medida', text: "A medida", level: 2 as const }, { id: 'a-lista-vem-do-interpretador', text: "A lista vem do interpretador", level: 2 as const }, { id: 'onde-ele-cala-e-por-que', text: "Onde ele cala, e por quê", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O método que não existe"}
      description={"O check acusava p.clientte num record e calava em \"ana\".naoExiste(). A conferência agora vale para os dois, e a lista de métodos é lida do interpretador."}
      href={"/docs/tipos/metodos-embutidos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
