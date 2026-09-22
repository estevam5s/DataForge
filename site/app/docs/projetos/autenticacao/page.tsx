// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Serviço de autenticação",
  description: "Cadastro, login com scrypt, bloqueio progressivo e token assinado com prazo.",
};

const blocos: Bloco[] = [
  {"p": "Autenticação é onde um projeto pequeno mais facilmente fica inseguro: a senha guardada com SHA-256, o login que diz *“usuário não existe”* (e com isso confirma quais e-mails têm conta), e o token que nunca vence. Este projeto faz as três coisas do jeito certo, com o que a biblioteca já tem."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`Crypto.hash_password`", "scrypt, com sal por senha"], ["`Crypto.hmac`", "o token assinado"], ["tentativas por conta", "o bloqueio progressivo"], ["a mesma resposta nos dois erros", "não confirmar quais contas existem"]]}},
  {"h2": "Estrutura"},
  { code: `auth/
  src/
    senhas.df      forca, hash, conferencia
    contas.df      cadastro e login
    tokens.df      emitir e conferir
  tests/
    login_test.df`, lang: 'text' },
  { code: `[project]
name = "auth"
version = "0.1.0"
description = "Autenticação"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `adopt Arcane.Crypto as Crypto

steady CHAVE := "troque-por-uma-variavel-de-ambiente"
contas := {}
falhas := {}

action cadastrar(email, senha):
    given len(senha) smaller 10:
        trigger "a senha precisa de pelo menos 10 caracteres"
    given email in contas:
        trigger "nao foi possivel cadastrar"
    contas[email] := Crypto.hash_password(senha)

// A MESMA mensagem para "nao existe" e "senha errada": a diferenca e
// exatamente o que quem ataca quer descobrir.
action entrar(email, senha, agora):
    f := falhas[email] ?? {"n": 0, "ate": 0}
    given agora smaller f["ate"]:
        yield {"ok": no, "motivo": "tente mais tarde"}
    guardada := contas[email] ?? void
    given guardada is void or not Crypto.verify_password(senha, guardada):
        n := f["n"] + 1
        // 1, 2, 4, 8... segundos a partir da terceira falha
        espera := 0 given n smaller 3 otherwise 2 ** (n - 3)
        falhas[email] := {"n": n, "ate": agora + espera}
        yield {"ok": no, "motivo": "email ou senha incorretos"}
    falhas[email] := {"n": 0, "ate": 0}
    yield {"ok": yes, "token": emitir(email, agora + 3600)}

action emitir(email, vence):
    carga := $"{email}|{vence}"
    yield $"{carga}|{Crypto.hmac(CHAVE, carga)}"

action conferir(token, agora):
    partes := token.split("|")
    given len(partes) is not 3:
        yield void
    carga := $"{partes[0]}|{partes[1]}"
    given not Crypto.hmac_verify(CHAVE, carga, partes[2]):
        yield void
    given int(partes[1]) smaller_eq agora:
        yield void
    yield partes[0]

cadastrar("ana@exemplo.com", "cavalo-bateria-grampo")
ok := entrar("ana@exemplo.com", "cavalo-bateria-grampo", 1000)
assert ok["ok"]
assert conferir(ok["token"], 1001) is "ana@exemplo.com"
assert conferir(ok["token"], 99999) is void
assert conferir(ok["token"].replace("ana", "eva"), 1001) is void

a := entrar("ana@exemplo.com", "errada", 2000)
b := entrar("ninguem@exemplo.com", "errada", 2000)
assert a["motivo"] is b["motivo"]

cycle i in range(0, 4):
    entrar("ana@exemplo.com", "errada", 3000)
assert entrar("ana@exemplo.com", "cavalo-bateria-grampo", 3000)["motivo"] is "tente mais tarde"
assert entrar("ana@exemplo.com", "cavalo-bateria-grampo", 3100)["ok"]
out "autenticacao verde"`, lang: 'df', title: `src/contas.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/contas as C

crucible "login":
    trial "o token adulterado nao vale":
        C.cadastrar("bia@exemplo.com", "uma-senha-longa")
        t := C.entrar("bia@exemplo.com", "uma-senha-longa", 0)["token"]
        expect C.conferir(t + "x", 1) is void`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["scrypt, e não SHA-256", "uma GPU testa bilhões de SHA-256 por segundo"], ["mesma resposta nos dois erros", "o formulário vira um oráculo de quais e-mails têm conta"], ["espera **progressiva**, não bloqueio fixo", "quem ataca bloqueia a conta da vítima de propósito"], ["`hmac_verify`, não `is`", "comparar a assinatura com `is` vaza, pelo tempo, quantos caracteres acertaram"], ["o prazo **dentro** da carga assinada", "trocar o prazo não invalida a assinatura"]]}},
  {"h2": "Para ir além"},
  {"list": ["O token padrão da indústria: `Crypto.jwt_*` — [Autenticação](/docs/seguranca/autenticacao).", "2FA com TOTP: [Arcane.Seguranca](/docs/biblioteca/seguranca).", "Quem pode o quê depois de entrar: [Arcane.Politica](/docs/biblioteca/politica)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Serviço de autenticação"}
      description={"Cadastro, login com scrypt, bloqueio progressivo e token assinado com prazo."}
      href={"/docs/projetos/autenticacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
