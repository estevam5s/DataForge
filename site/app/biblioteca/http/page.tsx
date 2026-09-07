import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Http",
  description: "Servidor HTTP com rotas, middleware e JSON.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Http as Http

app := Http.create("Minha API")
Http.cors(app)

action listar(req, res):
    res.json([{"id": 1, "nome": "Primeiro"}])

Http.get(app, "/api/itens", listar)
Http.listen(app, 3000)`, title: `exemplo` },
  {"callout": {"tipo": "nota", "texto": "`Http.listen` bloqueia: ele fica servindo até você interromper. Guia completo em [Servidor HTTP](/tecnicas/http)."}},
  {"p": "Guia com contexto e boas práticas: [Http](/tecnicas/http)."},
  {"h2": "Funções (17)"},
  {"table": {"head": ["Assinatura"], "rows": [["`cors(app)`"], ["`create(name='DataForge App')`"], ["`delete(app, path, handler)`"], ["`get(app, path, handler)`"], ["`html_response(html, status=200)`"], ["`json_parser(app)`"], ["`json_response(data, status=200)`"], ["`listen(app, port=3000, host='0.0.0.0')`"], ["`logger(app)`"], ["`patch(app, path, handler)`"], ["`post(app, path, handler)`"], ["`put(app, path, handler)`"], ["`route(app, method, path, handler)`"], ["`static(app, directory)`"], ["`stop(app)`"], ["`templates(app, directory)`"], ["`use(app, middleware)`"]]}},
];

const headings = [{ id: 'funcoes-17', text: "Funções (17)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Http"}
      description={"Servidor HTTP com rotas, middleware e JSON."}
      href={"/biblioteca/http"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
