import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "11 · Tipos e checagem",
  description: "6 exercícios: anotações, o analisador estático e generics.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 11`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["121", "**Anotacoes de tipo**", "declare variaveis com tipo e comprove que o valor errado e recusado."], ["122", "**Acoes com tipos**", "anote parametros e retorno, e veja o erro apontar o parametro exato."], ["123", "**typeof e conversao**", "descubra o tipo de qualquer valor e converta entre tipos com seguranca."], ["124", "**Analise estatica**", "escreva erros de proposito e confirme que o dataforge check os encontra."], ["125", "**Tipos dentro de colecoes**", "combine anotacoes com listas e dicionarios, e valide o conteudo."], ["126", "**Tipagem gradual com Any**", "use Any quando o tipo depende do uso, e estreite depois com typeof."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/11-tipos-e-checagem/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/11-tipos-e-checagem/121_anotacoes_basicas.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"11 · Tipos e checagem"}
      description={"6 exercícios: anotações, o analisador estático e generics."}
      href={"/docs/exercicios/11-tipos-e-checagem"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
