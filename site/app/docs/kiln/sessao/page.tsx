import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Sessão e cookies",
  description: "Login, cookie de sessão e tokens assinados.",
};

const blocos: Bloco[] = [
  {"h2": "Entrar e sair"},
  { code: `route POST "/entrar":
    usuario := body["usuario"] ?? ""
    senha := body["senha"] ?? ""
    given not confere(usuario, senha):
        respond 401 html pagina_de_login("Usuário ou senha não conferem.")
    pronto := Kiln.redirect("/painel")
    respond Kiln.session_start(loja, req, pronto, {"usuario": usuario})

route GET "/sair":
    respond Kiln.session_end(loja, req, Kiln.redirect("/"))

route GET "/painel":
    given (session["usuario"] ?? void) is void:
        redirect "/entrar"
    respond html painel(session["usuario"])` },
  {"p": "`session_start` gera um identificador aleatório, guarda os dados e devolve a resposta com o cookie `kiln_sid` — `HttpOnly`, `SameSite=Lax`, sete dias. Nos pedidos seguintes, `session` já vem preenchida."},
  {"h2": "Uma mensagem honesta no login"},
  {"p": "\"Usuário ou senha não conferem\" — nunca \"esse usuário não existe\". A segunda forma diz a quem está tentando **quais contas existem**, e isso é metade do trabalho de invadir uma."},
  {"h2": "Onde a sessão mora"},
  {"p": "Em memória, no processo. Isso significa três coisas concretas:"},
  {"table": {"head": ["Situação", "O que acontece"], "rows": [
    ["o processo reinicia", "todo mundo é deslogado"],
    ["dois processos atrás de um balanceador", "o visitante desloga a cada pedido"],
    ["muitas sessões abertas", "todas ocupam memória, sem expirar sozinhas"]
  ]}},
  {"p": "Para um site de um processo — que é a maioria — isso é exatamente o certo, e é a razão de não haver configuração nenhuma. Para mais de um processo, guarde a sessão no banco e use `Kiln.sign`."},
  {"h2": "Token assinado"},
  { code: `token := Kiln.sign({"usuario": "ana", "ate": 1790000000}, SEGREDO)
dados := Kiln.unsign(token, SEGREDO)     // void se foi adulterado` },
  {"p": "O conteúdo vai legível no token (base64, não criptografia) com uma assinatura HMAC-SHA256. Qualquer alteração invalida — a comparação é feita em tempo constante, para que o tempo de resposta não vaze o prefixo correto."},
  {"p": "**Não ponha segredo dentro do token.** Quem o tem, lê. Ponha o identificador do usuário e a validade; o resto vem do banco."},
  {"h2": "Um cookie qualquer"},
  { code: `pronto := Kiln.html(pagina)
Kiln.cookie(pronto, "tema", "escuro", 365)
respond pronto` },
  {"table": {"head": ["Parâmetro", "Padrão", "Para que"], "rows": [
    ["`dias`", "sessão do navegador", "`0` apaga o cookie"],
    ["`http_only`", "`yes`", "o JavaScript da página não lê"],
    ["`same_site`", "`\"Lax\"`", "não viaja em requisição de outro site"],
    ["`seguro`", "`no`", "ponha `yes` em produção com HTTPS"],
    ["`caminho`", "`\"/\"`", "limita o cookie a um trecho do site"]
  ]}},
  {"h2": "O que este framework não faz por você"},
  {"p": "Não há hash de senha embutido. Guardar senha em texto é o erro mais caro que um site comete — use `Arcane.Crypto` com um algoritmo lento e um sal por usuário, e nunca compare senhas com `is`."},
  {"p": "O Kiln também não expira sessões sozinho. Se a sua aplicação precisa disso, guarde o horário na sessão e confira no middleware."},
];

const headings = [{ id: 'entrar-e-sair', text: "Entrar e sair", level: 2 as const }, { id: 'uma-mensagem-honesta-no-login', text: "Uma mensagem honesta no login", level: 2 as const }, { id: 'onde-a-sessao-mora', text: "Onde a sessão mora", level: 2 as const }, { id: 'token-assinado', text: "Token assinado", level: 2 as const }, { id: 'um-cookie-qualquer', text: "Um cookie qualquer", level: 2 as const }, { id: 'o-que-este-framework-nao-faz-por-voce', text: "O que este framework não faz por você", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title={"Sessão e cookies"}
      description={"Login, cookie de sessão e tokens assinados."}
      href={"/docs/kiln/sessao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
