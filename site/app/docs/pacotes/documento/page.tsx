import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "documento",
  description: "Markdown: converte para HTML e texto, extrai títulos e sumário.",
};

const blocos: Bloco[] = [
  { code: `dataforge add documento`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.1`"], ["Licença", "MIT"], ["Dependências", "`texto`"], ["Exporta", "12 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Subconjunto do Markdown: o que aparece num README. Processa código antes de ênfase, para que `**isto**` dentro de crase continue sendo código."},
  {"h2": "Uso"},
  { code: `adopt documento as D

out D.para_html("# Título\\n\\nUm **parágrafo**.")
out D.sumario(texto)      // os títulos, com nível e âncora`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 12 símbolos:"},
  { code: `nivel_do_titulo(linha)
titulo_html(linha)
bloco_codigo_html(linhas, i)
escapar(s)
ancora(titulo)
inline(linha)
titulos(fonte)
sumario(fonte, ate_nivel := 3)
para_html(fonte)
para_texto(fonte)
contar_palavras(fonte)
tempo_de_leitura(fonte, palavras_por_minuto := 200)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add documento
dataforge add documento@1.0.1
dataforge add documento@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"documento"}
      description={"Markdown: converte para HTML e texto, extrai títulos e sumário."}
      href={"/docs/pacotes/documento"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
