import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "medida",
  description: "Conversão de unidades: distância, massa, volume, temperatura e tempo.",
};

const blocos: Bloco[] = [
  { code: `dataforge add medida`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.1`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "13 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Cada família converte por uma unidade de referência: metro, grama, litro, segundo. Duas conversões em vez de uma tabela n×n — a tabela não cresce ao quadrado."},
  {"h2": "Uso"},
  { code: `adopt medida as U

out U.converter(5, "km", "milha")     // 3.1069
out U.temperatura(100, "C", "F")      // 212.0
out U.formatar(1500, "m")             // 1.5 km`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 13 símbolos:"},
  { code: `converter(valor, de, para)
temperatura(valor, de, para)
formatar(valor, unidade, casas := 2)
familia_de(unidade)
unidades(familia := void)
mesma_familia(a, b)
ESCADAS
DISTANCIA
MASSA
VOLUME
TEMPO
DADOS
FAMILIAS`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add medida
dataforge add medida@1.0.1
dataforge add medida@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"medida"}
      description={"Conversão de unidades: distância, massa, volume, temperatura e tempo."}
      href={"/docs/pacotes/medida"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
