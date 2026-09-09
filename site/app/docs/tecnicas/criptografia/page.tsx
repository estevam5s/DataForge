import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Criptografia",
  description: "Hashes, senhas, HMAC, aleatoriedade segura e cifragem de arquivo com Arcane.Crypto.",
};

const blocos: Bloco[] = [
  {"h2": "O escopo"},
  {"p": "`Arcane.Crypto` traz primitivas da biblioteca padrão do Python — hashes, HMAC, derivação de senha, codificações e aleatoriedade criptográfica — mais **cifragem de arquivo** com ChaCha20-Poly1305, escrita aqui."},
  {"callout": {"tipo": "atencao", "texto": "Ele **não** implementa criptografia de chave pública (RSA, curvas elípticas) nem TLS. Para falar com um servidor com segurança, use `Arcane.Http`, que já usa o TLS do sistema."}},
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
  {"h2": "Cifrar um arquivo"},
  {"p": "Guardar um contrato, um backup ou um `.env` em disco pede uma cifra de verdade — e não o `xor_cipher` que também mora neste módulo, que é brinquedo educativo."},
  { code: `adopt Arcane.Crypto as Cofre

Cofre.cifrar_arquivo("contrato.pdf", "contrato.dfv", "minha senha")
Cofre.decifrar_arquivo("contrato.dfv", "de-volta.pdf", "minha senha")

Cofre.cifrar_pasta("relatorios", "relatorios.dfv", "minha senha")
Cofre.e_cifrado("contrato.dfv")              # yes
Cofre.informacao_do_cofre("contrato.dfv")    # o cabeçalho, sem a senha` },
  {"p": "É **ChaCha20-Poly1305** (RFC 8439): a cifra embaralha, e o Poly1305 assina. Sem a assinatura, cifrar não bastaria — quem intercepta pode virar bits do texto cifrado, e como a cifra é XOR, isso vira bits do texto claro. A chave sai da senha por PBKDF2-SHA256 com 600 mil iterações."},
  {"h2": "O formato"},
  { code: `DFVAULT1 | iterações | sal (16) | nonce (12) | etiqueta (16) | dados`, lang: 'text' },
  {"p": "O cabeçalho **não é segredo** — ele diz como decifrar, e precisa ser lido antes de haver chave. Mas é autenticado junto com os dados: baixar as iterações para 1, na esperança de enfraquecer a derivação, invalida a etiqueta e o arquivo é recusado."},
  {"callout": {"tipo": "nota", "titulo": "Senha errada e arquivo adulterado dão a mesma mensagem", "texto": "É de propósito. Um erro que distinguisse os dois casos diria ao atacante que a senha está certa e só o conteúdo mudou — e com isso ele testa senhas mais depressa."}},
  {"h2": "Por que escrever a cifra foi defensável"},
  {"p": "O conselho de não escrever a própria criptografia vale principalmente contra dois riscos: errar o algoritmo, e vazar o segredo pelo **tempo** que a operação leva."},
  {"list": [
    "**Errar o algoritmo** — os vetores oficiais do RFC 8439 estão na suíte de testes. Uma implementação que os reproduz byte a byte está certa; não há meio-termo.",
    "**Vazar pelo tempo** — é o motivo de a escolha ser ChaCha20 e não AES. O AES em software depende de tabelas, e o tempo de ler uma tabela varia com o que está em cache — que depende da chave. ChaCha20 não tem tabela nenhuma: é soma, rotação e XOR, sempre nas mesmas posições."]},
  {"callout": {"tipo": "atencao", "titulo": "O que ele não promete", "texto": "O Poly1305 multiplica inteiros grandes, e a multiplicação do Python não é de tempo constante. Para cifrar um arquivo no seu disco isso não importa. Para um canal em rede contra um adversário ativo, use TLS."}},
  {"h2": "Apagar de verdade"},
  { code: `Cofre.apagar_seguro("contrato.pdf")      # sobrescreve, depois remove` },
  {"callout": {"tipo": "atencao", "texto": "Em disco magnético, sobrescrever dificulta a recuperação. Em **SSD não garante nada**: o controlador escreve em outro bloco, e o antigo continua lá, fora do alcance do sistema."}},
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

const headings = [{ id: 'o-escopo', text: "O escopo", level: 2 as const }, { id: 'hashes', text: "Hashes", level: 2 as const }, { id: 'senhas', text: "Senhas", level: 2 as const }, { id: 'hmac--autenticar-mensagens', text: "HMAC — autenticar mensagens", level: 2 as const }, { id: 'comparacao-em-tempo-constante', text: "Comparação em tempo constante", level: 2 as const }, { id: 'cifrar-um-arquivo', text: "Cifrar um arquivo", level: 2 as const }, { id: 'o-formato', text: "O formato", level: 2 as const }, { id: 'por-que-escrever-a-cifra-foi-defensavel', text: "Por que escrever a cifra foi defensável", level: 2 as const }, { id: 'apagar-de-verdade', text: "Apagar de verdade", level: 2 as const }, { id: 'aleatoriedade-segura', text: "Aleatoriedade segura", level: 2 as const }, { id: 'codificacoes', text: "Codificações", level: 2 as const }, { id: 'mascarar-para-exibir', text: "Mascarar para exibir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Criptografia"}
      description={"Hashes, senhas, HMAC, aleatoriedade segura e cifragem de arquivo com Arcane.Crypto."}
      href={"/docs/tecnicas/criptografia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
