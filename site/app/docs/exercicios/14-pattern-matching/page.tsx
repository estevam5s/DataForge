import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "14 · Pattern matching",
  description: "6 exercícios: point, when, tipos, sequências e vaults.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 14`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["139", "**Padroes basicos**", "case por literal, capture com um nome e use o curinga."], ["140", "**Padroes de tipo**", "case pelo tipo do valor e ligue o resultado ja tipado."], ["141", "**Padroes de sequencia**", "desmonte listas por posicao, com cabeca, cauda e tamanho fixo."], ["142", "**Padroes de record e vault**", "extraia campos direto no padrao, por posicao ou por nome."], ["143", "**Guardas e ligacao com as**", "combine condicoes e apelidos para casos precisos."], ["144", "**Projeto: validador de dados**", "junte padroes de tipo, sequencia e vault num validador de esquema."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/14-pattern-matching/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/14-pattern-matching/139_padroes_basicos.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"14 · Pattern matching"}
      description={"6 exercícios: point, when, tipos, sequências e vaults."}
      href={"/docs/exercicios/14-pattern-matching"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
