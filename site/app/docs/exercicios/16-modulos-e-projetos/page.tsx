import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "16 · Modulos e projetos",
  description: "6 exercícios: forge.toml, pacotes e organização.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 16`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["151", "**Modulos com adopt e relay**", "importe um modulo local e comprove que relay controla o que sai."], ["152", "**Imports seletivos e apelidos**", "traga so os simbolos que voce usa, com o nome que preferir."], ["153", "**Organizando um projeto**", "estruture codigo em modulos com responsabilidades separadas."], ["154", "**Manifesto e ferramentas**", "conheca o forge.toml e os comandos de projeto."], ["155", "**Testes automatizados**", "escreva testes que o dataforge test descobre e executa."], ["156", "**Projeto: biblioteca completa**", "escreva um modulo publicavel com interface, testes e documentacao."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/16-modulos-e-projetos/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/16-modulos-e-projetos/151_adopt_e_relay.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"16 · Modulos e projetos"}
      description={"6 exercícios: forge.toml, pacotes e organização."}
      href={"/docs/exercicios/16-modulos-e-projetos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
