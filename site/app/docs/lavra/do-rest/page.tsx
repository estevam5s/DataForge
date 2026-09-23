// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Do REST para o Lavra",
  description: "O que muda, o que não muda, e o caminho de migração que não exige parar.",
};

const blocos: Bloco[] = [
  {"p": "A migração que funciona **não** é reescrever a API: é pôr o Lavra ao lado do REST, sobre os mesmos casos de uso, e mover tela por tela. As duas convivem no mesmo servidor."},
  {"table": {"head": ["No REST", "No Lavra", "O que muda de verdade"], "rows": [["`GET /produtos`", "`busca: produtos`", "o cliente escolhe os campos"], ["`GET /produtos/1`", "`busca: produto(id: 1)`", "nada, exceto a forma"], ["`POST /produtos`", "`mudanca: criarProduto`", "o retorno traz o objeto criado"], ["`GET /produtos/1/categoria`", "campo `categoria` dentro de `produto`", "some a segunda ida à rede"], ["`?campos=nome,preco`", "a própria consulta", "deixa de ser convenção e passa a ser tipo"], ["404", "`void` no campo", "**ausência não é erro**, e o cliente trata diferente"], ["`Cache-Control`", "não há", "o cache volta a ser problema do cliente e do resolvedor"]]}},
  {"h2": "Os dois no mesmo servidor"},
  { code: `adopt Arcane.Lavra as Lavra
adopt Arcane.Kiln as Kiln

record Produto:
    id: Integer
    nome: String

PRODUTOS := [Produto(1, "café"), Produto(2, "filtro")]

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Produto)
Lavra.busca(esq, "produtos", "[Produto!]!",
    resolve := lambda r, a, c => PRODUTOS)
Lavra.conferir(esq)

// O REST continua, e o Lavra entra ao lado dele.
action listar_rest(req):
    yield Kiln.json([{"id": p.id, "nome": p.nome} cycle p in PRODUTOS])

app := Kiln.app()
Kiln.get(app, "/api/produtos", listar_rest)
Lavra.montar(app, esq, "/lavra")

// e os dois respondem
rest := Kiln.test(app, "GET", "/api/produtos")
assert rest["status"] is 200
grafo := Lavra.executar(esq, "busca:\\n    produtos:\\n        nome")
assert len(grafo["dados"]["produtos"]) is 2
out "REST em /api/produtos e Lavra em /lavra, no mesmo app"`, lang: 'df' },
  {"h2": "O que o Lavra NÃO resolve"},
  {"list": ["**Cache de HTTP.** Uma consulta é um POST com corpo; nenhum CDN a cacheia sozinho. Quem quer cache de borda continua no REST, ou usa consulta guardada com GET.", "**Upload de arquivo.** Há convenções (multipart com um mapa de variáveis), e todas são mais complicadas que um `POST /upload`.", "**Autorização.** Ela continua sendo sua — e agora por **campo**, não por rota, o que é mais trabalho e mais preciso.", "**O N+1.** Ele piora: o cliente é quem decide a profundidade. Sem lote, a primeira tela de alguém derruba o banco.", "**Versionamento.** \"Não precisa versionar\" só vale enquanto ninguém remove campo — e `Lavra` marca `obsoleto` justamente porque remover é inevitável."]},
  {"h2": "O campo que vai sumir avisa antes"},
  { code: `adopt Arcane.Lavra as Lavra

record Produto:
    id: Integer
    nome: String
    titulo: String

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Produto)
Lavra.campo(esq, "Produto", "titulo", "String",
    resolve := lambda p, a, c => p.nome,
    obsoleto := "use 'nome'; 'titulo' sai na 3.0")
Lavra.busca(esq, "produto", "Produto",
    resolve := lambda r, a, c => Produto(1, "café", "café"))
Lavra.conferir(esq)

// Ele continua RESPONDENDO — quebrar no dia do aviso não é aviso.
r := Lavra.executar(esq, "busca:\\n    produto:\\n        titulo")
assert r["dados"]["produto"]["titulo"] is "café"
assert len(r["erros"]) is 0

// …e o aviso viaja em 'extensoes.avisos', que é onde um cliente
// procura o que vai quebrar depois.
avisos := r["extensoes"]["avisos"]
assert len(avisos) is 1
out avisos[0]["mensagem"]

// E o esquema diz que ele está de saída.
assert "obsoleto" in Lavra.texto_do_esquema(esq)`, lang: 'df' },
  {"p": "Um campo obsoleto que **para de funcionar** no dia do aviso não é um aviso, é uma quebra com aviso prévio de zero. O valor do marcador está em ele continuar respondendo enquanto a ferramenta do cliente já reclama."},
];

const headings = [{ id: 'os-dois-no-mesmo-servidor', text: "Os dois no mesmo servidor", level: 2 as const }, { id: 'o-que-o-lavra-nao-resolve', text: "O que o Lavra NÃO resolve", level: 2 as const }, { id: 'o-campo-que-vai-sumir-avisa-antes', text: "O campo que vai sumir avisa antes", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Do REST para o Lavra"}
      description={"O que muda, o que não muda, e o caminho de migração que não exige parar."}
      href={"/docs/lavra/do-rest"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
