import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Importar módulos",
  description: "adopt: stdlib, arquivo ao lado, caminho relativo e pacote.",
};

const blocos: Bloco[] = [
  {"h2": "As formas"},
  { code: `adopt Arcane.Math as M              // biblioteca padrão
adopt validador as V                // pacote instalado
adopt ./util as U                   // arquivo ao lado
adopt ./lib/formato as F            // numa subpasta
adopt ../compartilhado/config as C  // subindo
adopt "src/legado.df" as L          // caminho literal`, lang: 'df' },
  {"h2": "Importar só o que usa"},
  { code: `adopt Arcane.Math.{sqrt, floor}     // forma compacta
adopt {sqrt as raiz} from Arcane.Math
adopt ./util.{dobro, VERSAO}`, lang: 'df' },
  {"p": "O nome entra direto no escopo — `sqrt(16)`, não `Math.sqrt(16)`. Útil para o que se usa muito; para o resto, o prefixo documenta de onde veio."},
  {"h2": "Onde o adopt procura"},
  {"p": "Nesta ordem:"},
  {"list": ["**Biblioteca padrão** — `Arcane.*` e os nomes curtos (`Math`, `IO`, `Text`)", "**Ao lado do arquivo** que faz o import, não do diretório de onde se rodou", "**`forge_modules/`**, subindo até achar um `forge.toml`"]},
  {"callout": {"tipo": "nota", "titulo": "Relativo ao arquivo, não ao cwd", "texto": "`adopt ./util` resolve a partir de quem escreve o import. Mover a pasta inteira não quebra nada, e ler o código basta para saber o que ele importa."}},
  {"h2": "Exportar"},
  { code: `action publica():
    yield interna() * 2

action interna():
    yield 21

relay publica          // 'interna' fica dentro do módulo`, lang: 'df' },
  {"p": "Sem nenhum `relay`, o módulo exporta tudo o que definiu no topo — conveniente para script. Num pacote, declare explicitamente: é o que separa a API do detalhe."},
  {"h2": "Fachada"},
  { code: `// lib/index.df
relay from ./util
relay from ./mat

// app.df
adopt ./lib/index as Lib      // uma API só, vários módulos dentro`, lang: 'df' },
  {"p": "`relay from` re-exporta tudo o que aquele módulo exporta. É o que permite quebrar a implementação em vários arquivos sem que quem consome precise saber disso. O nome local vence o re-exportado."},
  {"h2": "Ciclos"},
  {"p": "Dois módulos que se importam são detectados, com o caminho completo:"},
  { code: `erro[DF0501]: Circular import: b.df → a.df → b.df.
              Break the cycle by moving the shared part into a third module.`, lang: 'text' },
  {"h2": "Tipos vindos de módulo"},
  { code: `adopt ./tipos as T

p := T.Ponto(1, 2)          // record
c := spawn T.Caixa(7)       // blueprint
out T.Cor.Azul              // enum
out T.dobro(21)             // ação`, lang: 'df' },
];

const headings = [{ id: 'as-formas', text: "As formas", level: 2 as const }, { id: 'importar-so-o-que-usa', text: "Importar só o que usa", level: 2 as const }, { id: 'onde-o-adopt-procura', text: "Onde o adopt procura", level: 2 as const }, { id: 'exportar', text: "Exportar", level: 2 as const }, { id: 'fachada', text: "Fachada", level: 2 as const }, { id: 'ciclos', text: "Ciclos", level: 2 as const }, { id: 'tipos-vindos-de-modulo', text: "Tipos vindos de módulo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Importar módulos"}
      description={"adopt: stdlib, arquivo ao lado, caminho relativo e pacote."}
      href={"/docs/pacotes/importar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
