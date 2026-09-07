import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "API REST",
  description: "Um servidor HTTP com rotas, parâmetros de caminho, JSON e validação separada.",
};

const blocos: Bloco[] = [
  {"p": "Este é o código completo do exercício `166_http_servidor.df`, que roda e verifica a si mesmo."},
  { code: `adopt Arcane.Http as Http
adopt Arcane.Serialization as Serde

// Este exercicio monta a aplicacao e verifica a configuracao sem
// abrir a porta — assim ele roda na suite de testes.

app := Http.create("API de Tarefas")
Http.cors(app)
Http.logger(app)

// ── dados em memoria ──
tarefas := [
    {"id": 1, "titulo": "Estudar DataForge", "feita": yes},
    {"id": 2, "titulo": "Escrever testes", "feita": no}
]
proximo_id := 3

// ── validacao, separada da rota ──
action validar_tarefa(corpo):
    problemas := []
    given corpo is void:
        problemas.append("corpo ausente")
        yield problemas
    given "titulo" not in corpo:
        problemas.append("titulo e obrigatorio")
    orif len(corpo["titulo"].trim()) smaller 3:
        problemas.append("titulo precisa de ao menos 3 letras")
    yield problemas

// ── as rotas ──
action listar(req, res):
    res.json(tarefas)

action buscar(req, res):
    id := cast req["params"]["id"] as Integer
    achadas := tarefas >> sift t: t["id"] is id
    given len(achadas) is 0:
        res.json({"erro": "tarefa nao encontrada"}, 404)
    otherwise:
        res.json(achadas[0])

action criar(req, res):
    problemas := validar_tarefa(req["json"])
    given len(problemas) bigger 0:
        res.json({"erros": problemas}, 400)
        yield void
    nova := {
        "id": proximo_id,
        "titulo": req["json"]["titulo"].trim(),
        "feita": no
    }
    proximo_id += 1
    tarefas.append(nova)
    res.json(nova, 201)

action concluir(req, res):
    id := cast req["params"]["id"] as Integer
    cycle i from 0 to len(tarefas) - 1:
        given tarefas[i]["id"] is id:
            tarefas[i]["feita"] := yes
            res.json(tarefas[i])
            yield void
    res.json({"erro": "tarefa nao encontrada"}, 404)

action remover(req, res):
    id := cast req["params"]["id"] as Integer
    tarefas := tarefas >> sift t: t["id"] isnt id
    res.json({"removida": id})

Http.get(app, "/api/tarefas", listar)
Http.get(app, "/api/tarefas/:id", buscar)
Http.post(app, "/api/tarefas", criar)
Http.put(app, "/api/tarefas/:id", concluir)
Http.delete(app, "/api/tarefas/:id", remover)

// ── verificando a configuracao ──
out "── rotas registradas ──"
out "  GET    /api/tarefas"
out "  GET    /api/tarefas/:id"
out "  POST   /api/tarefas"
out "  PUT    /api/tarefas/:id"
out "  DELETE /api/tarefas/:id"

// A validacao e testavel sem subir servidor
out ""
out "── validacao ──"
out $"  sem corpo:      {validar_tarefa(void)}"
out $"  sem titulo:     {validar_tarefa({"outro": 1})}"
out $"  titulo curto:   {validar_tarefa({"titulo": "ab"})}"
out $"  valido:         {validar_tarefa({"titulo": "Uma tarefa"})}"

assert len(validar_tarefa(void)) is 1, "corpo ausente"
assert len(validar_tarefa({"titulo": "ab"})) is 1, "titulo curto"
assert len(validar_tarefa({"titulo": "Uma tarefa"})) is 0, "valido"

out ""
out $"tarefas iniciais: {len(tarefas)}"
out ""
out "Para subir de verdade, acrescente ao final:"
out "    Http.listen(app, 3000)"`, title: `166_http_servidor.df` },
  {"h2": "A estrutura"},
  {"p": "Cinco rotas REST sobre um recurso, com a validação **fora** das rotas — testável sem subir servidor e reutilizável entre POST e PUT."},
  {"h2": "Códigos que importam"},
  {"table": {"head": ["Código", "Quando"], "rows": [["200", "deu certo"], ["201", "criou algo novo"], ["400", "o cliente mandou dado inválido"], ["404", "não existe"]]}},
  {"p": "Devolver 200 com `{\"erro\": …}` no corpo obriga todo cliente a inspecionar o JSON. O código HTTP existe justamente para isso."},
  {"h2": "Subir de verdade"},
  {"p": "Acrescente `Http.listen(app, 3000)` ao final e teste com `curl`:"},
  { code: `curl localhost:3000/api/tarefas
curl -X POST localhost:3000/api/tarefas \\
     -H 'Content-Type: application/json' -d '{"titulo":"Nova"}'`, lang: 'bash' },
  {"p": "Guia completo em [Servidor HTTP](/docs/tecnicas/http)."},
];

const headings = [{ id: 'a-estrutura', text: "A estrutura", level: 2 as const }, { id: 'codigos-que-importam', text: "Códigos que importam", level: 2 as const }, { id: 'subir-de-verdade', text: "Subir de verdade", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"API REST"}
      description={"Um servidor HTTP com rotas, parâmetros de caminho, JSON e validação separada."}
      href={"/docs/receitas/api-rest"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
