import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "21 · Oop avancado",
  description: "10 exercícios: propriedades, estáticos, operadores, SOLID.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 21`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["181", "**Campos declarados**", "declare campos com tipo e padrao no corpo do blueprint."], ["182", "**Metodos estaticos**", "crie metodos que pertencem ao blueprint, nao a instancia."], ["183", "**Propriedades com get e set**", "exponha um valor calculado, e valide na atribuicao."], ["184", "**Visibilidade: private e protected**", "proteja o estado interno de um objeto."], ["185", "**Sobrecarga de operadores**", "faca '+' e '==' funcionarem no seu proprio tipo."], ["186", "**Blueprints abstratos e contratos de trait**", "declare o que um tipo precisa ter, e deixe o compilador cobrar."], ["187", "**Heranca e 'root'**", "estenda um comportamento sem reescrever o do pai."], ["188", "**Composicao no lugar de heranca**", "monte comportamento juntando objetos, nao estendendo."], ["189", "**Quando usar record e quando usar blueprint**", "compare os dois, e escolha pelo que o dado precisa."], ["190", "**Polimorfismo**", "trate tipos diferentes pela interface comum."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/21-oop-avancado/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/21-oop-avancado/181_campos_declarados.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"21 · Oop avancado"}
      description={"10 exercícios: propriedades, estáticos, operadores, SOLID."}
      href={"/docs/exercicios/21-oop-avancado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
