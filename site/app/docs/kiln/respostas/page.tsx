import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Respostas",
  description: "respond, status, cabeçalhos, cookies e arquivos.",
};

const blocos: Bloco[] = [
  {"h2": "As formas de `respond`"},
  { code: `respond json {"ok": yes}              // 200, application/json
respond html "<h1>Oi</h1>"           // 200, text/html
respond text "pong"                  // 200, text/plain
respond file "/tmp/relatorio.xlsx"   // com o Content-Type do arquivo

respond 201 json novo                // status antes do tipo
respond 404 json {"erro": "não achei"}
respond 204                          // só status, sem corpo

respond {"a": 1}                     // sem tipo: vault vira JSON
respond "<p>oi</p>"                  // texto começando com '<' vira HTML` },
  {"p": "Um inteiro logo depois de `respond` é sempre o **status**. Para responder o número 404 como JSON, escreva `respond json 404`."},
  {"h2": "`respond` encerra a rota"},
  { code: `route GET "/":
    respond json {"ok": yes}
    out "isto nunca roda"` },
  {"p": "Exatamente como `yield` encerra uma ação. É o que permite escrever guardas sem `otherwise`:"},
  { code: `route GET "/itens/:id":
    p := achar(params["id"])
    given p is void:
        respond 404 json {"erro": "não achei"}
    respond json p` },
  {"h2": "Os status que importam"},
  {"table": {"head": ["Código", "Quando", "Corpo"], "rows": [
    ["200", "deu certo", "o recurso"],
    ["**201**", "criou algo novo", "o que foi criado"],
    ["**204**", "deu certo, nada a dizer", "**nenhum**"],
    ["**302**", "mudou de lugar por ora", "vazio, `Location` no cabeçalho"],
    ["400", "o cliente mandou dado inválido", "o que está errado"],
    ["401", "não sei quem é você", "como se autenticar"],
    ["403", "sei quem é você, e não pode", "por quê"],
    ["404", "não existe", "opcional"],
    ["409", "conflito (já existe, versão velha)", "o conflito"],
    ["422", "entendi o formato, mas o dado não serve", "os campos"],
    ["429", "pedidos demais", "`Retry-After`"],
    ["500", "o servidor quebrou", "nada de detalhe em produção"]
  ]}},
  {"p": "Devolver 200 com `{\"erro\": …}` no corpo obriga todo cliente a inspecionar o JSON para saber se deu certo. O código HTTP existe para isso."},
  {"h2": "Cabeçalhos e cookies"},
  { code: `pronto := Kiln.json({"ok": yes})
Kiln.header(pronto, "X-Versao", "4.2")
Kiln.cookie(pronto, "tema", "escuro", 30)     // 30 dias
respond pronto` },
  {"p": "`Kiln.cookie` já marca `HttpOnly` e `SameSite=Lax` — os dois padrões que fecham a maioria dos problemas. Passe `seguro: yes` para exigir HTTPS, e `dias: 0` para apagar o cookie."},
  {"h2": "Redirecionar"},
  { code: `route GET "/antigo":
    redirect "/novo"                 // 302, temporário

route GET "/mudou-de-vez":
    redirect "/novo" status 301      // permanente` },
  {"p": "O 301 fica no cache do navegador praticamente para sempre. Use só quando o endereço mudou de verdade — voltar atrás depois é muito trabalho."},
  {"h2": "Servir um arquivo"},
  { code: `route GET "/relatorio.xlsx":
    // gerado na hora, com os dados de agora
    livro := montar_planilha()
    Xls.save(livro, "/tmp/r.xlsx")
    respond file "/tmp/r.xlsx"

// forçando o download com um nome
respond Kiln.file("/tmp/r.xlsx", void, "relatorio-marco.xlsx")` },
  {"h2": "Páginas de erro"},
  { code: `Kiln.on_error(app, 404, lambda req => Kiln.html(
    "<h1>404</h1><p>Não achei essa página.</p>", 404))

Kiln.on_error(app, 500, lambda req => Kiln.html(
    "<h1>Algo quebrou</h1><p>Já estamos olhando.</p>", 500))` },
  {"p": "Mantenha o status. Uma página de erro que responde 200 é indexada pelos buscadores como se fosse conteúdo."},
];

const headings = [{ id: 'as-formas-de-respond', text: "As formas de `respond`", level: 2 as const }, { id: 'respond-encerra-a-rota', text: "`respond` encerra a rota", level: 2 as const }, { id: 'os-status-que-importam', text: "Os status que importam", level: 2 as const }, { id: 'cabecalhos-e-cookies', text: "Cabeçalhos e cookies", level: 2 as const }, { id: 'redirecionar', text: "Redirecionar", level: 2 as const }, { id: 'servir-um-arquivo', text: "Servir um arquivo", level: 2 as const }, { id: 'paginas-de-erro', text: "Páginas de erro", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title={"Respostas"}
      description={"respond, status, cabeçalhos, cookies e arquivos."}
      href={"/docs/kiln/respostas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
