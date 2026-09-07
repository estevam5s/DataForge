import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "colecao",
  description: "Coleções: agrupar, particionar, zip, janela, achatar e frequências.",
};

const blocos: Bloco[] = [
  { code: `dataforge add colecao`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "20 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Cluster já tem `map`, `filter` e `unique`. Falta o que aparece sempre que se mexe com dados: agrupar por chave, particionar numa varredura só, janela deslizante, ordenar por campo."},
  {"h2": "Uso"},
  { code: `adopt colecao as C
out C.agrupar(pessoas, lambda p => p["cidade"])
out C.particionar([1,2,3,4], lambda n => n % 2 is 0)
out C.zip([1,2], ["a","b"])`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 20 símbolos:"},
  { code: `agrupar(itens, chave)
contar_por(itens, chave)
indexar(itens, chave)
particionar(itens, condicao)
zip(a, b)
descompactar(pares)
janela(itens, tamanho, passo := 1)
pares_consecutivos(itens)
achatar(itens, profundidade := 1)
frequencias(itens)
mais_comum(itens, quantos := 1)
somar_por(itens, valor)
media_por(itens, valor)
ordenar_por(itens, chave, decrescente := no)
distintos_por(itens, chave)
intersecao(a, b)
diferenca(a, b)
uniao(a, b)
fatiar(itens, tamanho)
selecionar_campos(vaults, campos)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add colecao
dataforge add colecao@1.0.0
dataforge add colecao@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"colecao"}
      description={"Coleções: agrupar, particionar, zip, janela, achatar e frequências."}
      href={"/docs/pacotes/colecao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
