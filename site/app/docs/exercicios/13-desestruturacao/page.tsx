// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "13 · Desestruturacao",
  description: "6 exercícios: cluster, vault, rest e troca de variáveis.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 13`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["133", "**Desestruturacao de listas**", "extraia varios valores de uma lista numa unica linha."], ["134", "**Resto e spread**", "colete o que sobra com ...resto e expanda colecoes com ..."], ["135", "**Desestruturar records e vaults**", "extraia campos nomeados de um record ou de um dicionario."], ["136", "**Compreensao de listas**", "construa listas transformando e filtrando numa unica expressao."], ["137", "**Compreensao de vaults**", "construa dicionarios com a mesma sintaxe, produzindo chave e valor."], ["138", "**Interpolacao de strings**", "monte textos com valores embutidos, sem concatenacao manual."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/13-desestruturacao/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/13-desestruturacao/133_desestruturar_listas.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"13 · Desestruturacao"}
      description={"6 exercícios: cluster, vault, rest e troca de variáveis."}
      href={"/docs/exercicios/13-desestruturacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
