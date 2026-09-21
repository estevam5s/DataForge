// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_informacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ataques a credenciais",
  description: "Força bruta, credential stuffing, pulverização de senha, bloqueio de conta, atrasos progressivos e limite de taxa — com o que cada defesa quebra.",
};

const blocos: Bloco[] = [
  {"p": "As três formas de atacar um login são diferentes, e a defesa que serve a uma não serve às outras. Confundi-las é como um sistema fica com bloqueio de conta e continua sendo invadido."},
  {"table": {"head": ["Ataque", "O que o atacante tem", "A forma", "O que o detecta"], "rows": [["**Força bruta**", "um usuário", "muitas senhas nele", "tentativas por **conta**"], ["**Credential stuffing**", "listas vazadas de usuário+senha", "uma tentativa em cada conta", "taxa por **IP** e por dispositivo"], ["**Pulverização**", "muitos usuários", "uma senha comum em todos", "taxa **global** de falhas"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Por que bloquear a conta não resolve — e cria um problema", "texto": "Bloquear após N erros protege contra força bruta e **cria uma negação de serviço**: quem ataca passa a errar de propósito para trancar a conta alheia. Contra *credential stuffing* ele não faz nada — lá é **uma** tentativa por conta, e o limite nunca é atingido. A defesa que cobre os três é **atraso progressivo por conta** somado a **limite de taxa por origem**."}},
  {"h2": "Atraso progressivo"},
  {"p": "A espera dobra a cada bloqueio, até um teto. Um limite fixo é contornado esperando o período; o crescimento torna a força bruta cara sem nunca trancar de vez quem só errou a senha."},
  { code: `adopt Arcane.Seguranca as Seg

// Depois de 3 falhas, espera 30s. Depois de mais 3, 60s. Depois,
// 120s — ate o teto. 'sucesso()' zera: sem isso, quem erra duas
// vezes por mes fica perto do bloqueio para sempre.
porta := Seg.tentativas(limite := 3, base := 30.0, teto := 3600.0)

cycle i from 1 to 2:
    r := porta.falha("ana@loja.com")
    out $"   falha {i}: faltam {r['restantes']} tentativa(s)"

terceira := porta.falha("ana@loja.com")
assert terceira["bloqueado"]
out $"   bloqueado por {terceira['segundos']}s"

// E o estado e POR CHAVE: outra conta nao e afetada.
assert porta.bloqueado("bruno@loja.com") is no

// O login certo zera a contagem.
porta.sucesso("ana@loja.com")
assert porta.bloqueado("ana@loja.com") is no

out "progressivo por conta, e nao um bloqueio duro"`, lang: 'df' },
  {"h2": "Limite de taxa"},
  {"p": "O limitador usa **balde de fichas**: o balde enche continuamente, e não de uma vez por janela. Com janela fixa, um cliente gasta o limite no último segundo de uma e no primeiro da seguinte — o dobro do limite num instante, que é exatamente o que se queria evitar."},
  { code: `adopt Arcane.Seguranca as Seg

// 5 tentativas por minuto, por origem.
porta := Seg.limitador(5, periodo := 60.0)

cycle i from 1 to 5:
    assert porta.permitir("203.0.113.7")

assert porta.permitir("203.0.113.7") is no

// 'espera' e o valor que vai no cabecalho 'Retry-After'.
out $"   Retry-After: {porta.espera('203.0.113.7')}s"

// Outra origem nao e afetada — a chave e o que separa.
assert porta.permitir("198.51.100.4")`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O limitador é por processo, e isso muda a conta", "texto": "Ele vive na memória. Num servidor com quatro processos, cada um tem o seu balde, e **o limite efetivo é quatro vezes maior**. Para limite compartilhado é preciso um armazém comum (Redis, banco), e este módulo não pretende ser nenhum dos dois — mas quem calibra o número precisa saber disso, senão o limite que está escrito não é o que acontece."}},
  {"h2": "A camada completa de um login"},
  { code: `adopt Arcane.Seguranca as Seg
adopt Arcane.Crypto as Crypto

steady POR_IP := Seg.limitador(20, periodo := 60.0)
steady POR_CONTA := Seg.tentativas(limite := 5, base := 30.0)

action entrar(email, senha, ip, guardada):
    // 1. Taxa por origem — pega credential stuffing e pulverizacao.
    given POR_IP.permitir(ip) is no:
        yield {"ok": no, "motivo": "muitas tentativas", "espere": POR_IP.espera(ip)}

    // 2. Atraso progressivo por conta — pega forca bruta.
    given POR_CONTA.bloqueado(email):
        yield {"ok": no, "motivo": "conta temporariamente bloqueada",
               "espere": POR_CONTA.falta(email)}

    // 3. A conferencia em si, em tempo constante por dentro.
    given Crypto.verify_password(senha, guardada) is no:
        POR_CONTA.falha(email)
        // A MESMA mensagem para usuario inexistente e senha errada:
        // distingui-las entrega quais contas existem.
        yield {"ok": no, "motivo": "usuario ou senha invalidos"}

    POR_CONTA.sucesso(email)
    yield {"ok": yes}

guardada := Crypto.hash_password("uma senha bem forte 2026")

assert entrar("ana@loja.com", "errada", "203.0.113.7", guardada)["ok"] is no
assert entrar("ana@loja.com", "uma senha bem forte 2026", "203.0.113.7", guardada)["ok"]

out "taxa por origem, atraso por conta, mensagem unica"`, lang: 'df' },
  {"h2": "Enumeração de usuários"},
  {"p": "Se “usuário não existe” e “senha incorreta” são respostas diferentes, o atacante descobre **quais contas existem** antes de tentar qualquer senha — e passa a usar as listas vazadas só onde elas valem."},
  {"table": {"head": ["Onde vaza", "Como fechar"], "rows": [["mensagem de erro do login", "a mesma frase para os dois casos"], ["**tempo** de resposta", "derive a senha mesmo quando o usuário não existe"], ["cadastro (“e-mail já usado”)", "responda sempre igual e informe por e-mail"], ["redefinição de senha", "“se houver conta, enviamos um link”"], ["código HTTP diferente", "o mesmo 401 nos dois casos"]]}},
  {"callout": {"tipo": "dica", "titulo": "O vazamento por tempo é o que quase todo mundo esquece", "texto": "Se o usuário não existe, o código costuma voltar **sem** derivar a senha — e a resposta chega em 1 ms em vez de 45 ms. Isso é tão informativo quanto a mensagem. A correção é conferir contra um hash descartável quando a conta não existe, de modo que os dois caminhos custem o mesmo."}},
  {"h2": "Outras defesas, e o veredito"},
  {"table": {"head": ["Defesa", "Estado aqui", "Observação"], "rows": [["senha vazada recusada no cadastro", "**existe** — `Seg.vazada`", "k-anonimato; a senha não sai da máquina"], ["CAPTCHA", "**não existe**", "é serviço de terceiro; ponha-o depois de N falhas, não antes"], ["MFA", "**existe** — TOTP", "a defesa que sobrevive à senha vazada"], ["impressão digital de dispositivo", "**não existe**", "tem implicação de privacidade; avalie antes"], ["alerta de login novo", "seu e-mail + `Seg.auditoria`", "detecção, e não prevenção"], ["bloqueio por geografia", "**não existe**", "alta taxa de falso positivo"]]}},
];

const headings = [{ id: 'atraso-progressivo', text: "Atraso progressivo", level: 2 as const }, { id: 'limite-de-taxa', text: "Limite de taxa", level: 2 as const }, { id: 'a-camada-completa-de-um-login', text: "A camada completa de um login", level: 2 as const }, { id: 'enumeracao-de-usuarios', text: "Enumeração de usuários", level: 2 as const }, { id: 'outras-defesas-e-o-veredito', text: "Outras defesas, e o veredito", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ataques a credenciais"}
      description={"Força bruta, credential stuffing, pulverização de senha, bloqueio de conta, atrasos progressivos e limite de taxa — com o que cada defesa quebra."}
      href={"/docs/seguranca/ataques"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
