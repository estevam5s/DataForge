import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Criptografia",
  description: "Hashes, senhas, HMAC e aleatoriedade segura com Arcane.Crypto.",
};

const blocos: Bloco[] = [
  {"h2": "O escopo"},
  {"p": "`Arcane.Crypto` traz primitivas da biblioteca padrão do Python: hashes, HMAC, derivação de senha, codificações e aleatoriedade criptográfica."},
  {"callout": {"tipo": "atencao", "texto": "Ele **não** implementa criptografia de chave pública nem cifras de bloco. Para isso, use uma biblioteca dedicada."}},
  {"h2": "Hashes"},
  { code: `adopt Arcane.Crypto as Crypto

Crypto.sha256("DataForge")
Crypto.sha512(dados)    Crypto.blake2b(dados)
Crypto.md5(dados)       Crypto.sha1(dados)
Crypto.hash(dados, "sha384")
Crypto.hash_file(caminho, "sha256")` },
  {"callout": {"tipo": "atencao", "texto": "`md5` e `sha1` estão disponíveis para compatibilidade (checksums, integridade de arquivo), mas **não use para senhas nem assinaturas** — os dois são quebrados para fins de segurança."}},
  {"h2": "Senhas"},
  {"p": "Este é o uso mais importante do módulo, e o que mais se erra:"},
  { code: `guardada := Crypto.hash_password("minha-senha")
# pbkdf2_sha256$200000$<sal>$<derivada>

Crypto.verify_password("minha-senha", guardada)     # yes
Crypto.verify_password("outra", guardada)           # no` },
  {"p": "`hash_password` deriva a senha com **sal aleatório** e 200 mil iterações de PBKDF2. Guarde a string inteira — ela contém o algoritmo, o número de iterações e o sal."},
  {"callout": {"tipo": "perigo", "titulo": "Nunca guarde senha em hash simples", "texto": "`sha256(senha)` é rápido demais: uma GPU testa bilhões por segundo. O PBKDF2 é lento **de propósito**, e o sal impede tabelas pré-computadas."}},
  {"h2": "HMAC — autenticar mensagens"},
  { code: `assinatura := Crypto.hmac(chave, mensagem)
Crypto.hmac_verify(chave, mensagem, assinatura)     # yes/no` },
  {"p": "Use para verificar que uma mensagem veio de quem diz ter vindo — webhooks, tokens, cookies assinados."},
  {"h2": "Comparação em tempo constante"},
  { code: `Crypto.constant_time_equals(recebido, esperado)` },
  {"p": "Comparar segredos com `is` vaza informação pelo **tempo**: uma comparação que falha no primeiro caractere retorna mais rápido que uma que falha no último. `hmac_verify` já faz isso internamente."},
  {"h2": "Aleatoriedade segura"},
  { code: `Crypto.random_token(32)       # URL-safe, para links e sessões
Crypto.random_hex(32)
Crypto.random_bytes(32)
Crypto.random_password(16)
Crypto.uuid()
Crypto.short_id(12)` },
  {"p": "Todas usam `secrets`, não `random`. A diferença: `random` é previsível a partir de saídas anteriores — inaceitável para tokens de sessão ou reset de senha."},
  {"h2": "Codificações"},
  { code: `Crypto.base64_encode(dados)     Crypto.base64_decode(texto)
Crypto.base64url_encode(dados)  # sem padding, para URLs
Crypto.hex_encode(dados)        Crypto.hex_decode(texto)` },
  {"callout": {"tipo": "nota", "texto": "Base64 **não é criptografia** — é codificação. Qualquer um decodifica. Use para transportar bytes em texto, nunca para esconder."}},
  {"h2": "Mascarar para exibir"},
  { code: `Crypto.mask("4111111111111111")     # ************1111
Crypto.mask(cpf, 3)                  # mostra os 3 últimos` },
];

const headings = [{ id: 'o-escopo', text: "O escopo", level: 2 as const }, { id: 'hashes', text: "Hashes", level: 2 as const }, { id: 'senhas', text: "Senhas", level: 2 as const }, { id: 'hmac--autenticar-mensagens', text: "HMAC — autenticar mensagens", level: 2 as const }, { id: 'comparacao-em-tempo-constante', text: "Comparação em tempo constante", level: 2 as const }, { id: 'aleatoriedade-segura', text: "Aleatoriedade segura", level: 2 as const }, { id: 'codificacoes', text: "Codificações", level: 2 as const }, { id: 'mascarar-para-exibir', text: "Mascarar para exibir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Criptografia"}
      description={"Hashes, senhas, HMAC e aleatoriedade segura com Arcane.Crypto."}
      href={"/tecnicas/criptografia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
