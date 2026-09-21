// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_informacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Segurança da informação: o mapa",
  description: "O currículo completo — da tríade CIA ao bloqueio progressivo — com o que a linguagem responde para cada item, e o que ela não responde.",
};

const blocos: Bloco[] = [
  {"p": "Segurança da informação não é uma biblioteca que se adota: é um conjunto de **decisões** que atravessam a linguagem, o código, o processo e a operação. Esta seção percorre o currículo inteiro e, para cada conceito, responde três coisas: **o que é**, **como o DataForge o atende**, e **o que ele não atende** — com o motivo."},
  {"callout": {"tipo": "atencao", "titulo": "Por que o veredito negativo está aqui", "texto": "Uma documentação de segurança que lista o que a ferramenta **não** faz é mais útil que uma que só lista o que faz. A segunda leva alguém a construir autenticação em cima de algo que não existe, e a descobrir no dia do incidente. Cada página aqui traz a linha *o que não existe*, e ela vem de `Arcane.Ecossistema.o_que_nao_existe()` ou está escrita com o motivo ao lado."}},
  {"h2": "O mapa"},
  {"table": {"head": ["Frente", "O que ela cobre", "Onde"], "rows": [["**Princípios**", "CIA, autenticação, autorização, responsabilização, não-repúdio, privilégio mínimo, defesa em profundidade, zero trust, seguro por desenho e por padrão", "[Princípios](/docs/seguranca/principios)"], ["**Ameaças**", "modelagem de ameaças (STRIDE), superfície de ataque, fronteiras de confiança e de segurança, gestão de risco, políticas", "[Ameaças e risco](/docs/seguranca/ameacas)"], ["**A linguagem**", "segurança de tipos, de memória, limites de índice, ausência segura, dados imutáveis, padrões seguros", "[O que a linguagem garante](/docs/seguranca/linguagem)"], ["**A entrada**", "validação, codificação de saída, serialização e desserialização seguras", "[Entrada e saída](/docs/seguranca/entrada)"], ["**Identidade**", "senha, hashing, MFA, TOTP, WebAuthn, OAuth, OIDC, SAML, LDAP, JWT, tokens, sessão", "[Autenticação](/docs/seguranca/autenticacao)"], ["**Permissão**", "autorização, RBAC, capacidades, módulos, dependências, sandbox", "[Autorização e capacidades](/docs/seguranca/autorizacao)"], ["**Ataques**", "força bruta, *credential stuffing*, bloqueio de conta, atrasos progressivos, limite de taxa", "[Ataques a credenciais](/docs/seguranca/ataques)"], ["**Ferramentas**", "detecção de segredos, linter de segurança, análise estática, verificações em execução, auditoria", "[As ferramentas](/docs/seguranca/ferramentas)"]]}},
  {"callout": {"tipo": "dica", "titulo": "A página irmã", "texto": "[Segurança](/docs/seguranca) responde uma pergunta diferente e complementar: **o que a linguagem e as ferramentas já garantem por construção** — injeção de SQL, XSS nos templates, travessia em pacotes, integridade do registro, TLS — e como relatar uma vulnerabilidade. Esta seção aqui é o currículo; aquela é o inventário das garantias."}},
  {"h2": "A tríade CIA, em uma tela"},
  {"p": "Todo o resto é meio para estes três fins. Um controle que não serve a nenhum deles é cerimônia."},
  {"table": {"head": ["", "A pergunta", "A resposta da linguagem"], "rows": [["**Confidencialidade**", "quem *não* deveria ver, não vê?", "`Crypto.cifrar` (ChaCha20-Poly1305), `Seg.segredo`, `Seg.redigir`, `Seg.mascarar_pii`"], ["**Integridade**", "o dado é o mesmo que foi gravado?", "`Crypto.hmac`, `Seg.assinar`, `Seg.auditoria` (cadeia encadeada), a etiqueta do AEAD"], ["**Disponibilidade**", "quem deveria usar, consegue?", "`Seg.limitador`, `Kiln.limite_de_corpo`, `Seg.json_seguro`, o teto da fila do `Arcane.Laco`"]]}},
  { code: `adopt Arcane.Crypto as Crypto
adopt Arcane.Seguranca as Seg
adopt Arcane.Bytes as Bytes

// CONFIDENCIALIDADE: o texto cifrado nao revela o conteudo.
// 'cifrar' e 'decifrar' trabalham em Bytes, e nao em texto.
cofre := Crypto.cifrar("saldo: 12345", "uma senha forte")
assert "12345" not in Crypto.hex_encode(cofre)

// INTEGRIDADE: a etiqueta do AEAD vem de graca junto com a cifra.
// Senha errada — ou um byte trocado — e RECUSA, e nao "texto
// ilegivel": e a diferenca entre saber e adivinhar.
assert Bytes.para_texto(Crypto.decifrar(cofre, "uma senha forte")) is "saldo: 12345"

monitor:
    Crypto.decifrar(cofre, "senha errada")
    assert no
handle Error as e:
    out "recusado: a etiqueta nao fecha"

// DISPONIBILIDADE: o limite e o que impede um cliente derrubar todos.
limite := Seg.limitador(100, periodo := 60.0)
assert limite.permitir("cliente-7")`, lang: 'df' },
  {"h2": "Os quatro que sustentam uma conta"},
  {"table": {"head": ["", "A pergunta", "Como se responde aqui"], "rows": [["**Autenticação**", "quem é você?", "senha derivada com `scrypt`, TOTP, token assinado com propósito"], ["**Autorização**", "você pode fazer isto?", "RBAC na aplicação, `Arcane.Capacidade` no módulo, `V.exigir_permissao` na tela"], ["**Responsabilização**", "quem fez, e quando?", "`Seg.auditoria` — uma linha por evento, com o resumo da anterior"], ["**Não-repúdio**", "dá para provar que foi você?", "assinatura com chave que só o autor tem. Um HMAC **não** dá isso: quem confere também consegue forjar"]]}},
  {"callout": {"tipo": "atencao", "titulo": "HMAC não é não-repúdio, e a diferença importa", "texto": "`Crypto.hmac` e `Seg.assinar` usam uma chave **simétrica**: as duas pontas têm a mesma, então quem verifica também consegue produzir. Isso prova **integridade e origem entre duas partes que confiam uma na outra** — e não serve como prova perante um terceiro. Não-repúdio de verdade pede assinatura **assimétrica** (a chave privada só do autor), e isso **não existe** nesta biblioteca: não há RSA nem curva elíptica em Python puro aqui. Quando o requisito for jurídico, use um serviço de assinatura."}},
  {"h2": "O que não existe — a lista curta"},
  {"table": {"head": ["Não há", "Porque", "O que fazer"], "rows": [["WebAuthn, passkeys, FIDO2", "exige CBOR, COSE, atestação e um navegador do outro lado — é um protocolo, não uma função", "um provedor de identidade na frente"], ["OAuth 2.0 / OIDC / SAML / LDAP **completos**", "são integrações com sistemas externos, não primitivas. O que existe são as **peças locais**: `Seg.pkce`, `Seg.estado_de_oauth`, `Crypto.jwt_verificar`", "[Autenticação](/docs/seguranca/autenticacao)"], ["Argon2id", "em Python puro rodaria lento a ponto de exigir parâmetros fracos — pior que o `scrypt` do `hashlib`, e não melhor", "`Crypto.hash_password` usa scrypt"], ["Assinatura assimétrica (RSA, ECDSA, Ed25519)", "implementá-las em Python puro é lento e é exatamente onde um erro de implementação vira falha silenciosa", "`ssl` do Python, ou um HSM/KMS"], ["TLS no Kiln", "ele roda sobre o `http.server`; TLS é do nginx ou do Caddy na frente", "[Kiln em produção](/docs/kiln/producao)"]]}},
  {"h2": "Privacidade não é o mesmo que segurança"},
  {"p": "Segurança pergunta *quem pode acessar*. Privacidade pergunta *se esse dado deveria existir*. Um sistema pode ser impecável na primeira e ilegal na segunda — e a LGPD cobra a segunda."},
  {"table": {"head": ["Princípio", "O que ele obriga", "A peça"], "rows": [["**Minimização**", "não coletar o que não se usa", "nenhuma ferramenta substitui a decisão; é de desenho"], ["**Privacidade por padrão**", "o estado inicial é o mais restritivo", "`Seg.limpar_html` com lista de permitidos, `Kiln.cabecalhos_seguros`"], ["**Mascaramento**", "o log e o relatório não carregam o dado pessoal", "`Seg.mascarar_pii` (CPF, CNPJ, cartão com Luhn, e-mail, telefone)"], ["**Descarte**", "apagar de verdade quando o prazo vence", "`Crypto.apagar_seguro`, e a política de retenção que ninguém automatiza por você"]]}},
  { code: `adopt Arcane.Seguranca as Seg

// Um corpo de pedido inteiro indo para o log — o caminho mais
// comum de um vazamento, e o mais inocente.
corpo := """{"cpf": "123.456.789-09", "email": "ana.silva@exemplo.com",
 "cartao": "4111111111111111", "pedido": 1234567890123456}"""

limpo := Seg.mascarar_pii(corpo)

assert "123.456.789-09" not in limpo
assert "ana.silva" not in limpo
assert "4111111111111111" not in limpo

// O numero do pedido NAO passa no Luhn, entao continua legivel:
// sem isso, todo numero de 16 digitos virava cartao e o relatorio
// ficava ilegivel — um falso positivo que faz desligar a mascara.
assert "1234567890123456" in limpo

out limpo`, lang: 'df' },
  {"h2": "Por onde começar"},
  {"cards": [{"href": "/docs/seguranca/principios", "title": "Princípios", "desc": "CIA, privilégio mínimo, defesa em profundidade, zero trust."}, {"href": "/docs/seguranca/ameacas", "title": "Ameaças e risco", "desc": "STRIDE, superfície de ataque, fronteiras de confiança."}, {"href": "/docs/seguranca/linguagem", "title": "O que a linguagem garante", "desc": "Tipos, memória, limites, ausência — e o que ela não garante."}, {"href": "/docs/seguranca/entrada", "title": "Entrada e saída", "desc": "Validar na entrada, codificar na saída, desserializar com lista."}, {"href": "/docs/seguranca/autenticacao", "title": "Autenticação", "desc": "Senha, scrypt, MFA, TOTP, OAuth, JWT, sessão."}, {"href": "/docs/seguranca/autorizacao", "title": "Autorização e capacidades", "desc": "RBAC, a fronteira de autoridade, dependências."}, {"href": "/docs/seguranca/ataques", "title": "Ataques a credenciais", "desc": "Força bruta, credential stuffing, bloqueio progressivo."}, {"href": "/docs/seguranca/ferramentas", "title": "As ferramentas", "desc": "Segredos, linter, análise estática, auditoria."}, {"href": "/docs/seguranca", "title": "Garantias por construção", "desc": "Injeção, XSS, pacotes, TLS — e como relatar uma falha."}]},
];

const headings = [{ id: 'o-mapa', text: "O mapa", level: 2 as const }, { id: 'a-triade-cia-em-uma-tela', text: "A tríade CIA, em uma tela", level: 2 as const }, { id: 'os-quatro-que-sustentam-uma-conta', text: "Os quatro que sustentam uma conta", level: 2 as const }, { id: 'o-que-nao-existe-a-lista-curta', text: "O que não existe — a lista curta", level: 2 as const }, { id: 'privacidade-nao-e-o-mesmo-que-seguranca', text: "Privacidade não é o mesmo que segurança", level: 2 as const }, { id: 'por-onde-comecar', text: "Por onde começar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Segurança da informação: o mapa"}
      description={"O currículo completo — da tríade CIA ao bloqueio progressivo — com o que a linguagem responde para cada item, e o que ela não responde."}
      href={"/docs/seguranca/mapa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
