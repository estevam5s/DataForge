// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/crypto.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Crypto",
  description: "Hashes, HMAC, senhas, codificações, aleatoriedade segura e cifragem de arquivo (ChaCha20-Poly1305). Assina e verifica JWT (HS256/384/512), com o algoritmo decidido por quem verifica e não pelo token.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Crypto as Crypto

out Crypto.sha256("DataForge")[0:16]

guardada := Crypto.hash_password("minha-senha")
out Crypto.verify_password("minha-senha", guardada)
out Crypto.verify_password("outra", guardada)

out Crypto.mask("4111111111111111")
out Crypto.random_token(12)`, title: `exemplo` },
  {"callout": {"tipo": "atencao", "texto": "`md5` e `sha1` existem para compatibilidade (checksums), **não para senhas**. Para senha, use `hash_password` / `verify_password`, que aplicam PBKDF2 com sal."}},
  {"p": "Guia com contexto e boas práticas: [Crypto](/docs/tecnicas/criptografia)."},
  {"h2": "Funções (52)"},
  {"table": {"head": ["Assinatura"], "rows": [["`algorithms()`"], ["`apagar_seguro(caminho, passadas=1)`"], ["`base32_decode(v)`"], ["`base32_encode(v)`"], ["`base64_decode(texto)`"], ["`base64_encode(v)`"], ["`base64url_decode(texto)`"], ["`base64url_encode(v)`"], ["`blake2b(v)`"], ["`blake2s(v)`"], ["`chave_nova(tamanho=32)`"], ["`cifrar(dados, senha, iteracoes=None)`"], ["`cifrar_arquivo(origem, destino='', senha='', iteracoes=None)`"], ["`cifrar_pasta(pasta, destino='', senha='')`"], ["`constant_time_equals(a, b)`"], ["`decifrar(pacote, senha)`"], ["`decifrar_arquivo(origem, destino='', senha='')`"], ["`derivar_chave(senha, sal='', iteracoes=None)`"], ["`e_cifrado(caminho)`"], ["`hash(valor, algoritmo='sha256')`"], ["`hash_file(caminho, algoritmo='sha256')`"], ["`hash_password(senha, iteracoes=200000)`"], ["`hex_decode(v)`"], ["`hex_encode(v)`"], ["`hmac(chave, mensagem, algoritmo='sha256')`"], ["`hmac_verify(chave, mensagem, assinatura, algoritmo='sha256')`"], ["`informacao_do_cofre(caminho)`"], ["`jwt_algoritmos()`"], ["`jwt_assinar(carga, chave, algoritmo='HS256', expira_em=0)`"], ["`jwt_ler(token)`"], ["`jwt_verificar(token, chave, algoritmo='HS256')`"], ["`mask(texto, visiveis=4, caractere='*')`"], ["`md5(v)`"], ["`pbkdf2(senha, sal, iteracoes=200000, algoritmo='sha256')`"], ["`random_bytes(n=32)`"], ["`random_choice(itens)`"], ["`random_hex(n=32)`"], ["`random_int(a, b)`"], ["`random_password(tamanho=16, simbolos=True)`"], ["`random_token(n=32)`"], ["`rot13(t)`"], ["`sha1(v)`"], ["`sha224(v)`"], ["`sha256(v)`"], ["`sha384(v)`"], ["`sha512(v)`"], ["`short_id(n=12)`"], ["`uuid()`"], ["`uuid4()`"], ["`uuid_hex()`"], ["`verify_password(senha, guardada)`"], ["`xor_cipher(texto, chave)`"]]}},
];

const headings = [{ id: 'funcoes-52', text: "Funções (52)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Crypto"}
      description={"Hashes, HMAC, senhas, codificações, aleatoriedade segura e cifragem de arquivo (ChaCha20-Poly1305). Assina e verifica JWT (HS256/384/512), com o algoritmo decidido por quem verifica e não pelo token."}
      href={"/docs/biblioteca/crypto"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
