import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Servidor HTTP",
  description: "Rotas, parâmetros, JSON e validação com Arcane.Http.",
};

const blocos: Bloco[] = [
  {"h2": "Montar"},
  { code: `adopt Arcane.Http as Http

app := Http.create("API de Tarefas")
Http.cors(app)         # libera chamadas de outra origem
Http.logger(app)       # registra cada requisição` },
  {"h2": "Rotas"},
  { code: `Http.get(app, "/api/tarefas", listar)
Http.get(app, "/api/tarefas/:id", buscar)
Http.post(app, "/api/tarefas", criar)
Http.put(app, "/api/tarefas/:id", atualizar)
Http.delete(app, "/api/tarefas/:id", remover)

Http.listen(app, 3000)` },
  {"p": "O `:id` é um **parâmetro de caminho**, disponível em `req[\"params\"][\"id\"]` — como texto, sempre. Converta antes de comparar."},
  {"h2": "Requisição e resposta"},
  {"table": {"head": ["Leitura", "Contém"], "rows": [["`req[\"params\"]`", "parâmetros do caminho (`:id`)"], ["`req[\"query\"]`", "da query string (`?pagina=2`)"], ["`req[\"json\"]`", "o corpo, já interpretado"], ["`req[\"headers\"]`", "os cabeçalhos"]]}},
  {"table": {"head": ["Escrita", "Faz"], "rows": [["`res.json(dados)`", "responde JSON com 200"], ["`res.json(dados, 404)`", "com o código que você escolher"], ["`res.html(texto)`", "responde HTML"], ["`res.send(texto, 200)`", "texto puro"]]}},
  {"h2": "Uma rota completa"},
  { code: `action buscar(req, res):
    id := cast req["params"]["id"] as Integer
    achadas := tarefas >> sift t: t["id"] is id
    given len(achadas) is 0:
        res.json({"erro": "tarefa nao encontrada"}, 404)
    otherwise:
        res.json(achadas[0])` },
  {"h2": "Códigos que importam"},
  {"table": {"head": ["Código", "Quando"], "rows": [["200", "deu certo"], ["201", "criou algo novo"], ["400", "o cliente mandou dado inválido"], ["404", "não existe"], ["500", "o servidor quebrou"]]}},
  {"p": "Devolver 200 com `{\"erro\": …}` no corpo obriga todo cliente a inspecionar o JSON para saber se deu certo. O código HTTP existe justamente para isso."},
  {"h2": "Validação fora da rota"},
  { code: `action validar_tarefa(corpo):
    problemas := []
    given corpo is void:
        problemas.append("corpo ausente")
        yield problemas
    given "titulo" not in corpo:
        problemas.append("titulo e obrigatorio")
    orif len(corpo["titulo"].trim()) smaller 3:
        problemas.append("titulo precisa de ao menos 3 letras")
    yield problemas

action criar(req, res):
    problemas := validar_tarefa(req["json"])
    given len(problemas) bigger 0:
        res.json({"erros": problemas}, 400)
        yield void
    ...` },
  {"p": "Duas vantagens de separar: **testável sem servidor**, e **reutilizável** entre POST e PUT. E devolver todos os problemas de uma vez poupa o cliente de descobrir um erro por requisição."},
  {"h3": "O detalhe do orif"},
  {"p": "Repare: sem o `orif`, o segundo teste rodaria mesmo quando a chave não existe, e `corpo[\"titulo\"]` estouraria. `orif` só é avaliado se o `given` foi falso."},
  {"h2": "Testar"},
  { code: `curl localhost:3000/api/tarefas
curl -X POST localhost:3000/api/tarefas \\
     -H 'Content-Type: application/json' \\
     -d '{"titulo":"Nova tarefa"}'`, lang: 'bash' },
];

const headings = [{ id: 'montar', text: "Montar", level: 2 as const }, { id: 'rotas', text: "Rotas", level: 2 as const }, { id: 'requisicao-e-resposta', text: "Requisição e resposta", level: 2 as const }, { id: 'uma-rota-completa', text: "Uma rota completa", level: 2 as const }, { id: 'codigos-que-importam', text: "Códigos que importam", level: 2 as const }, { id: 'validacao-fora-da-rota', text: "Validação fora da rota", level: 2 as const }, { id: 'testar', text: "Testar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Servidor HTTP"}
      description={"Rotas, parâmetros, JSON e validação com Arcane.Http."}
      href={"/docs/tecnicas/http"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
