import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "texto",
  description: "Texto: slug, truncar, mascarar, distância de edição, similaridade e templates.",
};

const blocos: Bloco[] = [
  { code: `dataforge add texto`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "15 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "A biblioteca padrão já traz `upper`, `split` e companhia. Aqui está o que se reescreve em todo projeto: slug, truncar sem cortar palavra, mascarar, e distância de edição para sugerir \"você quis dizer\"."},
  {"h2": "Uso"},
  { code: `adopt texto as T
out T.slug("Olá, Mundo Cruel!")     // ola-mundo-cruel
out T.truncar("uma frase longa", 10)
out T.similaridade("casa", "caza")  // 0.75`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 15 símbolos:"},
  { code: `sem_acento(s)
slug(s, separador := "-")
truncar(s, limite, reticencias := "…")
mascarar(s, visivel_inicio := 0, visivel_fim := 4, marca := "*")
mascarar_email(email)
distancia(a, b)
similaridade(a, b)
mais_parecido(alvo, candidatos, minimo := 0.6)
preencher(modelo, valores)
titulo(s)
contar_palavras(s)
quebrar_linhas(s, largura := 72)
inverter(s)
e_palindromo(s)
iniciais(nome, maximo := 2)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add texto
dataforge add texto@1.0.0
dataforge add texto@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"texto"}
      description={"Texto: slug, truncar, mascarar, distância de edição, similaridade e templates."}
      href={"/docs/pacotes/texto"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
