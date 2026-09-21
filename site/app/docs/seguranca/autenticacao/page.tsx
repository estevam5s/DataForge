// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_informacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Autenticação",
  description: "Senha e hashing (scrypt, PBKDF2, bcrypt, Argon2id), MFA, 2FA, TOTP, WebAuthn e passkeys, OAuth 2.0, OIDC, SAML, LDAP, JWT, tokens e sessão — com o veredito de cada um.",
};

const blocos: Bloco[] = [
  {"p": "Autenticação responde **quem é você**. Esta página percorre os mecanismos usados na indústria e diz, para cada um, o que a linguagem entrega — e o que ela não entrega."},
  {"h2": "Senha: o hashing"},
  {"p": "Guardar senha é guardar um **derivado lento e salgado** dela. A lentidão é o recurso: ela não incomoda quem faz um login e inviabiliza quem faz bilhões."},
  {"table": {"head": ["Algoritmo", "Estado aqui", "O veredito"], "rows": [["**scrypt**", "**o padrão**, `Crypto.hash_password`", "*memory-hard*: exige ~32 MB por tentativa, e memória é o que a GPU não tem em abundância por núcleo"], ["**PBKDF2-SHA256**", "disponível, `algoritmo := \"pbkdf2\"`", "só encadeia hash — barato de acelerar em GPU. Fica para compatibilidade e para senhas antigas"], ["**Argon2id**", "**não existe**", "seria o melhor; em Python puro rodaria lento a ponto de exigir parâmetros fracos, o que o torna *pior* que o scrypt"], ["**bcrypt**", "**não existe**", "exige uma implementação de Blowfish; o `hashlib` não a traz, e escrevê-la em Python é o tipo de código criptográfico que não se deve escrever"]]}},
  { code: `adopt Arcane.Crypto as Crypto

// O sal e sorteado e vai DENTRO da string guardada: guarde-a inteira.
guardada := Crypto.hash_password("uma senha bem forte 2026")

out guardada[0:24]              // scrypt$32768$8$1$...

assert Crypto.verify_password("uma senha bem forte 2026", guardada)
assert Crypto.verify_password("outra senha", guardada) is no

// Duas vezes a MESMA senha dao strings diferentes — e o sal e o
// motivo: sem ele, senhas iguais teriam o mesmo resumo, e uma
// tabela pronta quebraria todas de uma vez.
assert Crypto.hash_password("igual") isnt Crypto.hash_password("igual")`, lang: 'df' },
  {"h3": "Rotação: o único momento em que dá para atualizar"},
  {"p": "Sem isto, um banco fica para sempre no algoritmo com que nasceu — ninguém sabe quais linhas estão velhas, e não há momento em que a senha em claro esteja disponível para regravar. Exceto **um**: o login bem-sucedido."},
  { code: `adopt Arcane.Crypto as Crypto

action entrar(senha, guardada):
    given Crypto.verify_password(senha, guardada) is no:
        yield {"ok": no}

    // Aqui — e so aqui — a senha em claro existe e ja foi conferida.
    given Crypto.precisa_rehash(guardada):
        yield {"ok": yes, "regravar": Crypto.hash_password(senha)}

    yield {"ok": yes}

// Uma senha guardada no formato antigo continua entrando...
antiga := Crypto.hash_password("segredo do usuario", algoritmo := "pbkdf2")
r := entrar("segredo do usuario", antiga)
assert r["ok"]
// ...e sai do login ja no formato novo.
assert "regravar" in keys(r)

out "o formato antigo entra, e e atualizado na saida"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Por que `verify_password` ainda aceita o formato antigo", "texto": "Um banco tem senhas guardadas de antes da troca de algoritmo. Se a conferência só entendesse o formato novo, o dia da atualização seria **o dia em que ninguém consegue entrar** — e a saída de emergência seria mandar todo mundo redefinir a senha. O formato é auto-descritivo: o primeiro campo diz qual é, e os parâmetros vêm junto. É o que torna a próxima troca barata."}},
  {"h3": "Força, política e vazamento"},
  {"p": "“Senha fraca” não diz o que fazer. O que vai para a tela é a **lista do que falta**."},
  { code: `adopt Arcane.Seguranca as Seg

fraca := Seg.forca_da_senha("Abcdef1!")
out $"{fraca['rotulo']} ({fraca['nota']}/100)"
cycle problema in fraca["problemas"]:
    out $"   - {problema}"

// A politica devolve; 'exigir_politica' levanta com a lista em
// 'e.nota', para quem escreve o caminho feliz.
r := Seg.politica("Tr0vao#Azul7291!x")
assert r["ok"]

// E a entropia, que e uma medida do TEXTO e nao de como ele foi
// escolhido: por isso ela e um dos criterios, e nunca o unico.
out $"entropia: {r['entropia']} bits"`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Verificar vazamento sem entregar a senha", "texto": "`Seg.vazada(senha)` consulta o *Have I Been Pwned* mandando os **cinco primeiros** caracteres do SHA-1 — nunca a senha. O serviço devolve centenas de resumos que começam com aquele prefixo, e a comparação é local: ele não tem como saber qual das centenas era a sua. É o k-anonimato, e é uma chamada de **rede** — está no nome da função. Ela devolve `-1` em vez de levantar quando a rede falha: uma política de senha que para de funcionar porque um serviço de terceiro caiu impede cadastro por um motivo que não é de segurança. Para conferir offline: `prefixo_vazamento` + `conferir_vazamento`."}},
  {"callout": {"tipo": "atencao", "titulo": "Rotação periódica de senha é má prática", "texto": "Obrigar a troca a cada 90 dias é contraproducente, e o **NIST SP 800-63B** recomenda contra desde 2017: as pessoas respondem com `Senha1!`, `Senha2!`, `Senha3!` — previsível e pior que a original. Troque **por evento**: vazamento conhecido, suspeita de comprometimento, saída de um administrador. O que `precisa_rehash` faz é outra coisa: rotacionar o **algoritmo**, sem incomodar ninguém."}},
  {"h2": "Múltiplos fatores"},
  {"p": "Um fator é algo que você **sabe** (senha), **tem** (telefone, chave física) ou **é** (biometria). MFA exige de categorias diferentes — duas senhas não são dois fatores."},
  {"table": {"head": ["Fator", "Estado aqui", "Observação"], "rows": [["**TOTP** (app autenticador)", "**existe**, RFC 6238 completo", "o segundo fator com melhor relação custo/benefício"], ["**HOTP** (por contador)", "**existe**, RFC 4226", "base do TOTP; serve para token físico de contador"], ["**Códigos de recuperação**", "**existe**", "devolve o código **e** o resumo — guarde só o resumo"], ["**SMS**", "não há integração", "desaconselhado: *SIM swap* e interceptação de SS7"], ["**WebAuthn / passkeys / FIDO2**", "**não existe**", "é um protocolo com CBOR, COSE e atestação, não uma função"], ["**Chave física (YubiKey)**", "**não existe**", "chega por WebAuthn"]]}},
  { code: `adopt Arcane.Seguranca as Seg

// Os vetores do RFC 4226. Uma implementacao de OTP que nao os
// reproduz esta errada mesmo que "funcione": o autenticador do
// usuario vai discordar dela.
assert Seg.hotp("GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", 0) is "755224"
assert Seg.hotp("GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", 1) is "287082"

// O cadastro: sorteie o segredo, mostre o QR, e guarde o segredo
// CIFRADO — ele vale tanto quanto a senha.
segredo := Seg.totp_segredo()
out Seg.totp_uri(segredo, "ana@loja.com", emissor := "Minha Loja")

// A conferencia aceita a janela vizinha: o relogio do telefone anda
// alguns segundos fora, e um codigo digitado no segundo 29 chega no
// 31. Sem tolerancia, uma fracao real dos logins legitimos falha —
// e o usuario aprende a desligar o segundo fator.
codigo := Seg.totp_agora(segredo)
assert Seg.totp_conferir(segredo, codigo)
assert Seg.totp_conferir(segredo, "000000") is no

// E os codigos de recuperacao, para quem perdeu o telefone.
r := Seg.codigos_de_recuperacao(10)
out $"{len(r['codigos'])} codigos; guarde apenas os {len(r['resumos'])} resumos"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Três detalhes que decidem se o TOTP protege", "texto": "**1.** A comparação é em tempo constante — comparar código com `is` vaza, pelo tempo, quantos dígitos iniciais estavam certos. **2.** O código usado precisa ser **marcado como usado**: sem isso, quem intercepta tem 30 segundos para reusá-lo. Isso é estado da sua aplicação, e a biblioteca não pode fazer por você. **3.** O segredo guardado em claro no banco anula tudo — quem ler a tabela gera os códigos."}},
  {"h2": "WebAuthn e passkeys — o veredito"},
  {"p": "São hoje o mecanismo mais forte disponível: a chave privada nunca sai do dispositivo, e a assinatura é ligada ao **domínio**, o que torna o phishing estruturalmente impossível."},
  {"callout": {"tipo": "atencao", "titulo": "Não existe nesta biblioteca, e o motivo", "texto": "WebAuthn não é uma função: é um protocolo entre navegador, autenticador e servidor, com CBOR, COSE, cadeias de atestação e verificação de assinatura **assimétrica** (ES256, RS256). Duas dessas peças — a criptografia assimétrica e o parser CBOR — não existem aqui, e escrevê-las em Python puro é exatamente o tipo de código criptográfico que não se deve escrever à mão. **O que fazer:** ponha um provedor de identidade na frente (Auth0, Keycloak, Clerk, Supabase Auth) e receba o resultado como [OIDC](/docs/seguranca/autenticacao) — e aí as peças que existem aqui (`pkce`, `estado_de_oauth`, `jwt_verificar`) são as que você usa."}},
  {"h2": "OAuth 2.0, OIDC, SAML, LDAP"},
  {"p": "São **integrações** com sistemas externos, e não primitivas. O que a biblioteca traz são as peças **locais** de cada fluxo — as que envolvem criptografia e que são justamente onde as implementações erram."},
  {"table": {"head": ["Protocolo", "Para quê", "Estado aqui"], "rows": [["**OAuth 2.0**", "autoriz**ação** delegada — acesso a um recurso", "as peças locais: `pkce`, `estado_de_oauth`; o HTTP é `Arcane.Malha`"], ["**OpenID Connect**", "autentic**ação** sobre OAuth — quem é a pessoa", "a verificação do `id_token` é `Crypto.jwt_verificar` *(HS\\*; para RS256 é preciso um serviço)*"], ["**SAML**", "SSO corporativo em XML", "**não existe** — exige XML-DSig e canonicalização, cheios de armadilhas"], ["**LDAP / Active Directory**", "diretório corporativo", "**não existe** — é um protocolo binário próprio"]]}},
  {"callout": {"tipo": "dica", "titulo": "OAuth autoriza; OIDC autentica", "texto": "É a confusão mais cara desta área. OAuth 2.0 entrega um *access token*: ele diz **o que pode ser feito**, e não quem é a pessoa. Usar um access token como prova de identidade é a falha conhecida por *confused deputy* — o token foi emitido para outro aplicativo e você o aceita como login. Quem responde “quem é” é o `id_token` do OIDC, e ele precisa ser **verificado**: assinatura, emissor (`iss`), destinatário (`aud`), prazo (`exp`) e o `nonce` que você mandou."}},
  { code: `adopt Arcane.Seguranca as Seg

// PKCE (RFC 7636) — o que o OAuth 2.0 exige hoje, e a peca que a
// biblioteca entrega. O 'code' volta pela URL do navegador; num app
// de celular ou numa SPA nao existe segredo do cliente para provar
// quem e, e quem interceptar o codigo o troca por um token.
par := Seg.pkce()

// Ao PEDIR o codigo, manda-se o desafio (o SHA-256 do verificador).
out $"code_challenge={par['desafio'][0:16]}... method={par['metodo']}"

// Ao TROCAR o codigo, manda-se o verificador. So quem sorteou o tem.
assert Seg.conferir_pkce(par["verificador"], par["desafio"])
assert Seg.conferir_pkce("outro-verificador-que-nao-e-o-certo-123456", par["desafio"]) is no

// E o 'state', que e a defesa de CSRF do fluxo: sem ele, um atacante
// inicia o proprio fluxo e faz a vitima completa-lo — a conta dela
// acaba ligada a conta dele no provedor.
estado := Seg.estado_de_oauth()
// guarde na sessao, e CONFIRA na volta. Guardar e nao conferir e o
// defeito mais comum deste fluxo.
assert len(estado) bigger 20

out "as pecas locais do OAuth, e a rede fica com o Arcane.Malha"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`plain` não é uma opção", "texto": "O RFC 7636 define dois métodos de PKCE: `S256` e `plain`. O `plain` manda o verificador **como** desafio — o que não protege de nada, porque quem intercepta a primeira ida já tem os dois. Ele existe no RFC por compatibilidade com clientes antigos, e não é oferecido aqui."}},
  {"h2": "JWT"},
  {"p": "Um JWT é um objeto JSON assinado. Ele é útil quando o receptor precisa validar **sem consultar um banco** — e é exatamente por isso que ele é difícil de revogar."},
  { code: `adopt Arcane.Crypto as Crypto

chave := Crypto.random_hex(32)

token := Crypto.jwt_assinar({"sub": "ana", "papel": "editor"}, chave,
    expira_em := 900)

// O ALGORITMO E DECIDIDO POR QUEM VERIFICA, e nao pelo token.
// Essa e a falha classica do JWT: aceitar o 'alg' que vem dentro
// permite 'alg: none' — e o token passa a ser texto assinado por
// ninguem. Aqui o algoritmo e argumento da verificacao.
r := Crypto.jwt_verificar(token, chave, algoritmo := "HS256")
assert r["valido"]
assert r["carga"]["sub"] is "ana"

// 'jwt_ler' le SEM verificar — para inspecionar, nunca para decidir.
out Crypto.jwt_ler(token)["papel"]

// Ele DEVOLVE o veredito em vez de levantar: o motivo entra no log,
// e quem chama decide o que responder ao cliente.
outra := Crypto.jwt_verificar(token, "outra chave", algoritmo := "HS256")
assert outra["valido"] is no
out $"recusado: {outra['motivo']}"`, lang: 'df' },
  {"table": {"head": ["A armadilha", "Como se fecha aqui"], "rows": [["`alg: none`", "o algoritmo é **argumento de quem verifica**, nunca lido do token"], ["confusão HS256/RS256", "idem — não há como o token escolher"], ["token que não expira", "`expira_em` é conferido na verificação"], ["revogação", "**não tem solução no formato**: use prazo curto + *refresh*"], ["dado sensível no corpo", "o corpo é base64, **não** é cifrado — qualquer um lê"]]}},
  {"h2": "Tokens e sessão"},
  {"table": {"head": ["Tipo", "Vida", "Onde guardar", "Como revogar"], "rows": [["**acesso**", "5–15 min", "memória do cliente", "não se revoga: expira"], ["**refresh**", "dias/semanas", "cookie `HttpOnly`", "no banco — e **rotacione a cada uso**"], ["**sessão**", "horas", "cookie `HttpOnly`", "apagar do armazém"], ["**API key**", "longa", "cofre do cliente", "no banco, por prefixo"], ["**de uso único** (e-mail, senha)", "minutos", "não se guarda", "propósito + prazo, e marcar usado"]]}},
  { code: `adopt Arcane.Seguranca as Seg

chave := Seg.chave_de_assinatura()

// Um link de redefinir senha: proposito E prazo. Sem o proposito, o
// token que confirma um e-mail SERVE para trocar a senha — os dois
// sao assinados com a mesma chave.
link := Seg.assinar({"usuario": 42}, chave, proposito := "trocar-senha")

monitor:
    Seg.ler_assinado(link, chave, prazo := 900, proposito := "confirmar-email")
    assert no
handle SignatureError as e:
    out "recusado: o proposito e outro"

lido := Seg.ler_assinado(link, chave, prazo := 900, proposito := "trocar-senha")
assert lido["valor"]["usuario"] is 42

// E a URL assinada, para download temporario: mudar QUALQUER
// parametro invalida a assinatura.
u := Seg.assinar_url("https://loja.com/baixar?id=9", chave, prazo := 60)
assert Seg.conferir_url(u, chave)["ok"]`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A ordem da verificação não é detalhe", "texto": "`ler_assinado` confere a **assinatura antes do prazo**. Conferir o prazo primeiro significa ler o corpo de um token que ainda não se sabe se é legítimo — e a data de dentro dele é dado de quem o mandou até a assinatura fechar. E `ExpiredTokenError` é separado de `SignatureError` de propósito: no primeiro caso o link era legítimo e caducou, e a ação certa é oferecer outro; num token adulterado, oferecer outro seria ajudar quem tenta."}},
  {"h3": "O cookie de sessão"},
  {"table": {"head": ["Atributo", "Porque"], "rows": [["`HttpOnly`", "o JavaScript não lê — um XSS deixa de virar roubo de sessão"], ["`Secure`", "não viaja em HTTP puro"], ["`SameSite=Lax`", "não vai numa requisição de outro site (defesa de CSRF)"], ["`Path=/`, sem `Domain`", "não vaza para subdomínio de terceiro"], ["id novo **após o login**", "impede fixação de sessão"]]}},
  {"callout": {"tipo": "dica", "titulo": "Fixação de sessão, e como a Vitrine a fecha", "texto": "O ataque: o atacante planta um id de sessão no navegador da vítima **antes** do login; se o servidor reaproveitar aquele id, os dois passam a compartilhar a sessão autenticada. Na Vitrine, um id desconhecido vira **sessão nova**, e só id de 32 hexadecimais chega ao armazém — o segundo detalhe também impede que `../x` vire nome de arquivo no armazém em disco."}},
];

const headings = [{ id: 'senha-o-hashing', text: "Senha: o hashing", level: 2 as const }, { id: 'rotacao-o-unico-momento-em-que-da-para-atualizar', text: "Rotação: o único momento em que dá para atualizar", level: 3 as const }, { id: 'forca-politica-e-vazamento', text: "Força, política e vazamento", level: 3 as const }, { id: 'multiplos-fatores', text: "Múltiplos fatores", level: 2 as const }, { id: 'webauthn-e-passkeys-o-veredito', text: "WebAuthn e passkeys — o veredito", level: 2 as const }, { id: 'oauth-20-oidc-saml-ldap', text: "OAuth 2.0, OIDC, SAML, LDAP", level: 2 as const }, { id: 'jwt', text: "JWT", level: 2 as const }, { id: 'tokens-e-sessao', text: "Tokens e sessão", level: 2 as const }, { id: 'o-cookie-de-sessao', text: "O cookie de sessão", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Autenticação"}
      description={"Senha e hashing (scrypt, PBKDF2, bcrypt, Argon2id), MFA, 2FA, TOTP, WebAuthn e passkeys, OAuth 2.0, OIDC, SAML, LDAP, JWT, tokens e sessão — com o veredito de cada um."}
      href={"/docs/seguranca/autenticacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
