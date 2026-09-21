// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_informacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Criptografia e chaves",
  description: "Simétrica, autenticada, assimétrica, hashing, assinatura e o ciclo de vida da chave — com o que existe aqui e o que não existe.",
};

const blocos: Bloco[] = [
  {"p": "Criptografia erra em silêncio: o programa roda, o arquivo fica cifrado, e a falha só aparece quando alguém tenta explorá-la. Esta página diz o que a linguagem oferece, e — com a mesma clareza — o que ela não oferece."},
  {"h2": "O que existe"},
  {"table": {"head": ["Categoria", "Aqui", "Observação"], "rows": [["**Cifra autenticada (AEAD)**", "ChaCha20-Poly1305, RFC 8439 — `Crypto.cifrar`", "a etiqueta vem junto: adulterar um byte é **recusa**, não texto ilegível"], ["**Cifra simétrica pura**", "só via AEAD", "oferecer ChaCha20 ou AES sem autenticação seria oferecer a forma de errar"], ["**AES**", "**não existe**", "o ChaCha20 é mais rápido em software sem AES-NI e mais difícil de implementar errado"], ["**Resumo**", "SHA-2, SHA-3, BLAKE2 — `Crypto.algorithms()`", "MD5 e SHA-1 existem para *checksum*, e o linter acusa o uso em assinatura"], ["**HMAC**", "`Crypto.hmac`, `hmac_verify`", "integridade e origem **entre duas partes**"], ["**Senha derivada**", "scrypt (padrão) e PBKDF2", "ver [Autenticação](/docs/seguranca/autenticacao)"], ["**Assimétrica** (RSA, ECC, Ed25519)", "**não existe**", "em Python puro é lenta e é onde um erro vira falha silenciosa"], ["**Assinatura com não-repúdio**", "**não existe**", "consequência da linha acima — HMAC não serve"], ["**TLS**", "o `ssl` do Python; no Kiln, um nginx na frente", "`Rede.certificado_de` inspeciona um certificado"], ["**Aleatoriedade**", "`Crypto.random_bytes`, `random_token`", "`os.urandom`; `randint` **não** serve para segredo"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Por que não há AES", "texto": "Não é limitação de esforço. Sem instruções de hardware (AES-NI), uma implementação de AES em Python puro é lenta **e** é difícil de fazer em tempo constante — e uma cifra que vaza tempo vaza a chave. O ChaCha20-Poly1305 foi desenhado para ser rápido e seguro em software puro, e é a escolha certa para uma linguagem sem dependência externa."}},
  {"h2": "A chave tem ciclo de vida"},
  {"p": "`Crypto` gera bytes e cifra com eles. O que faltava era o resto: de onde a chave veio, até quando vale, para que serve, e o que fazer com o dado cifrado pela versão anterior. Sem isso, o que acontece é sempre o mesmo — uma chave nasce numa variável de ambiente, é usada para tudo, e nunca é trocada."},
  { code: `adopt Arcane.Chaves as Ch

cofre := Ch.cofre()
cofre.gerar("mestra", proposito := "cifrar")

envelope := cofre.envelopar("um terabyte de dados", "mestra")

// Rotacionar nao torna ilegivel o passado: o envelope carrega o
// 'kid', e a chave aposentada continua abrindo o que ela fechou.
nova := cofre.rotacionar("mestra", "cifrar")
assert cofre.desenvelopar(envelope) isnt void

// E recifrar troca a chave sem tocar nos DADOS — so na DEK.
assert cofre.recifrar(envelope, "mestra")["kid"] is nova.kid

out "rotacionado, e o passado continua legivel"`, lang: 'df' },
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["a chave tem **propósito**", "a que assina token também decifra arquivo, e um comprometimento vira todos"], ["a rotação **mantém as antigas**", "trocar a chave torna ilegível o que já foi cifrado — então ninguém troca"], ["o dado carrega o **`kid`**", "na hora de decifrar não se sabe qual das cinco chaves usar"], ["o material **não aparece em texto**", "o vazamento mais comum é alguém imprimir o objeto para depurar"]]}},
  {"callout": {"tipo": "dica", "titulo": "Envelope, e por que todo KMS faz assim", "texto": "Cifrar um terabyte com a chave mestra significa que rotacioná-la é **reescrever o terabyte**. Com envelope, cada objeto tem a sua chave de dados (DEK), e o que a mestra (KEK) cifra é só a DEK — 32 bytes. Rotacionar passa a ser recifrar as DEKs."}},
  {"h2": "Gestão de segredo"},
  {"table": {"head": ["Pergunta", "Resposta aqui"], "rows": [["onde o segredo mora", "no ambiente, e nunca no repositório — `dataforge seguranca` acusa"], ["como ele não vaza em log", "`Seg.segredo` (opaco) e `Seg.redigir`"], ["como se guarda o cofre", "`cofre.exportar(senha)` devolve cifrado; **gravar é de quem chama**"], ["como se sabe que é hora de trocar", "`cofre.precisa_rotacionar()`"], ["cofre externo (Vault, KMS, Secrets Manager)", "**não há integração** — é serviço, e cada um tem a sua API"]]}},
  {"p": "Referência: [Arcane.Chaves](/docs/biblioteca/chaves) e [Arcane.Crypto](/docs/biblioteca/crypto)."},
];

const headings = [{ id: 'o-que-existe', text: "O que existe", level: 2 as const }, { id: 'a-chave-tem-ciclo-de-vida', text: "A chave tem ciclo de vida", level: 2 as const }, { id: 'gestao-de-segredo', text: "Gestão de segredo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Criptografia e chaves"}
      description={"Simétrica, autenticada, assimétrica, hashing, assinatura e o ciclo de vida da chave — com o que existe aqui e o que não existe."}
      href={"/docs/seguranca/criptografia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
