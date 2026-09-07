import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Logging",
  description: "Registro estruturado com níveis e destinos.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Logging as Log

registro := Log.logger("pedidos", "DEBUG")
registro.info("pedido recebido", {"id": 1042})
registro.warn("estoque baixo", {"restam": 3})
registro.error("pagamento recusado", {"codigo": 402})

out registro.stats()`, title: `exemplo` },
  {"p": "Guia com contexto e boas práticas: [Logging](/docs/tecnicas/logging)."},
  {"h2": "Funções (14)"},
  {"table": {"head": ["Assinatura"], "rows": [["`as_json(a=True)`"], ["`debug(m, campos=None)`"], ["`default()`"], ["`error(m, campos=None)`"], ["`fatal(m, campos=None)`"], ["`info(m, campos=None)`"], ["`levels()`"], ["`log(n, m, campos=None)`"], ["`logger(nome='app', nivel='INFO')`"], ["`set_level(n)`"], ["`stats()`"], ["`to_file(c, anexar=True)`"], ["`trace(m, campos=None)`"], ["`warn(m, campos=None)`"]]}},
];

const headings = [{ id: 'funcoes-14', text: "Funções (14)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Logging"}
      description={"Registro estruturado com níveis e destinos."}
      href={"/docs/biblioteca/logging"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
