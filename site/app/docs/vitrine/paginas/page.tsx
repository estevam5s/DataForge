// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/vitrine.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Páginas e segurança",
  description: "Multipágina, rotas com parâmetro, autenticação, permissões e os cabeçalhos que toda resposta leva.",
};

const blocos: Bloco[] = [
  {"h2": "Várias páginas"},
  { code: `V.app("Painel")

V.pagina("/", inicio, titulo := "Início", icone := "🏠")
V.pagina("/vendas", vendas, titulo := "Vendas", icone := "📊")
V.pagina("/produto/:id", produto, oculta := yes)

V.rodar(porta := 8501)`, lang: 'df' },
  {"p": "Também funciona como decorador:"},
  { code: `mark @V.pagina("/vendas")
action vendas():
    V.titulo("Vendas")`, lang: 'df' },
  {"p": "`V.menu()` desenha o menu das páginas registradas na barra lateral, na ordem do registro. Uma página `oculta` continua alcançável pela URL e não aparece no menu."},
  {"h2": "Parâmetros"},
  { code: `action produto():
    id := V.parametro("id")              // da rota: /produto/:id
    ordem := V.parametro("ordem", "asc")  // da query: ?ordem=desc
    V.titulo($"Produto {id}")`, lang: 'df' },
  {"p": "`V.parametros()` devolve os dois juntos; `V.caminho()` devolve onde a página está."},
  {"h2": "Navegar e parar"},
  { code: `V.navegar("/entrar")      // vai para outra página, e para aqui
V.parar()                 // acaba a página neste ponto, sem erro
V.recarregar()            // roda de novo, do começo, jogando fora a árvore`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "V.recarregar() tem teto", "texto": "Quatro reexecuções por interação. Um `V.recarregar()` sem `given` em volta vira uma mensagem na página — e não um servidor travado."}},
  {"h2": "Autenticação"},
  {"p": "Registre a ação que confere usuário e senha. Ela recebe os dois e devolve o vault do usuário, ou `void`:"},
  { code: `action conferir(usuario, senha):
    linha := Banco.um("SELECT * FROM usuarios WHERE email = ?", [usuario])
    given linha is not void and Crypto.conferir_senha(senha, linha["hash"]):
        yield {"nome": linha["nome"], "papel": linha["papel"]}
    yield void

V.autenticacao(conferir, {
    "admin":  ["ver", "editar", "apagar"],
    "leitor": ["ver"]
})`, lang: 'df' },
  {"p": "E a barreira, na primeira linha de cada página protegida:"},
  { code: `action relatorio():
    V.exigir_login()
    V.titulo($"Olá, {V.usuario()["nome"]}")

action edicao():
    V.exigir_permissao("editar")
    V.titulo("Edição")`, lang: 'df' },
  {"p": "`V.exigir_login()` desenha o formulário de entrada e **para** a página. Quando já há alguém logado, ela devolve o usuário e não desenha nada — o que permite chamá-la sempre na primeira linha."},
  {"callout": {"tipo": "dica", "titulo": "O login reexecuta a página do começo", "texto": "Continuar de onde parou parece mais barato e não funciona: quem escreveu `given V.autenticado(): …` já passou por esse teste com a resposta antiga, e a tela sairia vazia no instante em que a pessoa acertou a senha."}},
  {"table": {"head": ["Chamada", "Devolve"], "rows": [["`V.usuario()`", "o vault de quem está logado, ou `void`"], ["`V.autenticado()`", "`yes`/`no`"], ["`V.pode(permissão)`", "`yes`/`no`, pelo papel"], ["`V.entrar(usuario, senha)`", "o vault, ou `void`"], ["`V.sair()`", "derruba a sessão de quem está logado"]]}},
  {"h2": "Segurança"},
  {"p": "Toda resposta HTML leva estes cabeçalhos, sem configuração:"},
  {"table": {"head": ["Cabeçalho", "Contra"], "rows": [["`X-Content-Type-Options: nosniff`", "o navegador adivinhar o tipo do conteúdo"], ["`X-Frame-Options: SAMEORIGIN`", "clickjacking"], ["`Referrer-Policy`", "vazar a URL inteira para terceiros"], ["`Content-Security-Policy`", "script de outra origem"]]}},
  {"p": "O cookie de sessão é `HttpOnly` e `SameSite=Lax`. Com `V.configurar(\"https\", yes)` ele também ganha `Secure`."},
  {"p": "Todo texto que vai à página é escapado — o único que não é passa por `V.html`, que avisa disso. E `V.markdown` escapa **antes** de reconhecer a marcação, além de recusar link `javascript:`."},
  {"p": "Para limite de taxa e CORS, use o middleware do Kiln sobre `V.montar()` — ver [Middleware do Kiln](/docs/kiln/middleware)."},
];

const headings = [{ id: 'varias-paginas', text: "Várias páginas", level: 2 as const }, { id: 'parametros', text: "Parâmetros", level: 2 as const }, { id: 'navegar-e-parar', text: "Navegar e parar", level: 2 as const }, { id: 'autenticacao', text: "Autenticação", level: 2 as const }, { id: 'seguranca', text: "Segurança", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Páginas e segurança"}
      description={"Multipágina, rotas com parâmetro, autenticação, permissões e os cabeçalhos que toda resposta leva."}
      href={"/docs/vitrine/paginas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
