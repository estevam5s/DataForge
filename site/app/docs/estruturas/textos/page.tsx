// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Texto de tamanho fixo",
  description: "O char[N] do C: completado com zeros, lido até o primeiro zero — e o acento que não cabe.",
};

const blocos: Bloco[] = [
  {"p": "Muitos formatos guardam texto num espaço de **tamanho fixo**: o código `IHDR` de um chunk PNG, o nome de 16 caracteres de um registro antigo. O campo `char` com N bytes é esse espaço: escreve completando com zeros, e lê até o primeiro zero."},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

Registro := Est.definir("Registro", [["codigo", "char", 4], ["nome", "char", 8]], "rede", yes)
b := Registro({"codigo": "AB", "nome": "Joana"})

assert Bytes.hex(b.bytes()) is "414200004a6f616e61000000"   // os zeros completam
assert Registro.ler(b) is {"codigo": "AB", "nome": "Joana"} // e somem na leitura`, lang: 'df' },
  {"h2": "O limite é em bytes, não em letras"},
  {"p": "O campo mede **bytes em UTF-8**, e um acento ocupa dois. \"João\" tem 4 letras e 5 bytes: não cabe num `char` de 4. Cortar em silêncio gravaria \"Jo\\xc3\" — metade de um caractere, e um texto inválido. O molde recusa:"},
  { code: `adopt Arcane.Estrutura as Est

Nome := Est.definir("Nome", [["n", "char", 4]])
recusado := no
monitor:
    Nome({"n": "João"})
handle BufferOverflowError as e:
    recusado := yes
assert recusado
assert Nome.ler(Nome({"n": "Joã"}))["n"] is "Joã"          // quatro bytes: cabe`, lang: 'df' },
  {"h2": "Bytes crus"},
  {"p": "`bytes` com N é o mesmo espaço, sem interpretação: a assinatura mágica de um arquivo, um hash, uma chave. Lê e escreve `Bytes`, e nunca corta no primeiro zero — porque ali o zero é dado."},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

Cab := Est.definir("Cab", [["magica", "bytes", 4], ["versao", "u8"]], "rede", yes)
b := Cab({"magica": Bytes.de_hex("7f454c46"), "versao": 2})   // a assinatura do ELF
assert Bytes.hex(Cab.ler(b)["magica"]) is "7f454c46"`, lang: 'df' },
];

const headings = [{ id: 'o-limite-e-em-bytes-nao-em-letras', text: "O limite é em bytes, não em letras", level: 2 as const }, { id: 'bytes-crus', text: "Bytes crus", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Texto de tamanho fixo"}
      description={"O char[N] do C: completado com zeros, lido até o primeiro zero — e o acento que não cabe."}
      href={"/docs/estruturas/textos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
