import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "registro",
  description: "Registro estruturado: níveis, campos, destinos e formatação JSON ou texto.",
};

const blocos: Bloco[] = [
  { code: `dataforge add registro`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "3 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Log com campos, não com frase concatenada. A diferença aparece no dia em que alguém precisa filtrar por cliente: com campos é uma consulta, com frase é uma expressão regular que quebra na semana seguinte."},
  {"h2": "Uso"},
  { code: `adopt registro as L

log := L.novo("api")
log.info("pedido recebido", {"id": 42, "cliente": "ana"})

[14:07:19] INFO  api  pedido recebido  id=42 cliente=ana`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 3 símbolos:"},
  { code: `blueprint Registrador
novo(nome := "app", nivel := "info")
NIVEIS`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add registro
dataforge add registro@1.0.0
dataforge add registro@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"registro"}
      description={"Registro estruturado: níveis, campos, destinos e formatação JSON ou texto."}
      href={"/docs/pacotes/registro"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
