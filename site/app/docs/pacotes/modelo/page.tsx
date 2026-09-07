import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "modelo",
  description: "Templates de texto: variáveis, laços, condicionais e filtros.",
};

const blocos: Bloco[] = [
  { code: `dataforge add modelo`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "8 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Sintaxe deliberadamente pequena: variável, laço, condicional e filtro. Template que vira linguagem de programação é código escondido onde ninguém procura."},
  {"h2": "Uso"},
  { code: `adopt modelo as M

out M.render("Olá, {{nome}}!", {"nome": "Ana"})
out M.render("{{#itens}}- {{.}}\\n{{/itens}}", {"itens": ["a", "b"]})`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 8 símbolos:"},
  { code: `renderizar_secao(negado, valor, corpo, dados)
renderizar_itens(itens, corpo, dados)
render(modelo, dados := void)
buscar(dados, caminho)
verdadeiro(valor)
registrar_filtro(nome, acao)
de_arquivo(caminho, dados := void)
FILTROS`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add modelo
dataforge add modelo@1.0.0
dataforge add modelo@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"modelo"}
      description={"Templates de texto: variáveis, laços, condicionais e filtros."}
      href={"/docs/pacotes/modelo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
