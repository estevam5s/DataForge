// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "CRC e soma de conferência",
  description: "CRC-32 do PNG e do ZIP, e a soma de complemento de um do cabeçalho IP — com o vetor da RFC.",
};

const blocos: Bloco[] = [
  {"p": "Um dado que atravessou disco ou rede pode chegar com um bit trocado, e um número com um bit trocado é **outro número válido**. A conferência é um resumo pequeno, gravado junto, que muda quando qualquer bit muda."},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

dados := Bytes.de_texto("DataForge")
crc := Est.crc32(dados)
alterado := Bytes.de_texto("DataForgf")       // um caractere de diferença
assert Est.crc32(alterado) is not crc
assert crc is Est.crc32(Bytes.de_texto("Forge"), Est.crc32(Bytes.de_texto("Data")))`, lang: 'df' },
  {"h2": "A soma do cabeçalho IPv4"},
  {"p": "O IP usa algo mais simples que o CRC: a soma, em complemento de um, das palavras de 16 bits do cabeçalho. Com o exemplo clássico (192.168.0.1 → 192.168.0.199), a soma tem de dar `b861` — e somar o cabeçalho **com** a soma tem de dar zero:"},
  { code: `adopt Arcane.Bytes as Bytes

adopt Arcane.Estrutura as Est

action soma_ip(cabecalho):
    total := 0
    cycle i in range(0, len(cabecalho), 2):
        total += Est.deslocar(cabecalho[i], 8) + cabecalho[i + 1]
    persist total bigger 0xFFFF:                 // dobra o "vai um" de volta
        total := Est.bits_e(total, 0xFFFF) + Est.deslocar(total, -16)
    yield Est.bits_nao(total, 16)                // o complemento de um

sem_soma := Bytes.de_hex("450000730000400040110000c0a80001c0a800c7")
assert soma_ip(sem_soma) is 0xb861

com_soma := Bytes.de_hex("45000073000040004011b861c0a80001c0a800c7")
assert soma_ip(com_soma) is 0              // o receptor confere assim`, lang: 'df' },
  {"table": {"head": ["", "Pega", "Não pega", "Onde"], "rows": [["soma de complemento de um", "um bit trocado", "duas palavras trocadas de lugar", "IP, TCP, UDP"], ["CRC-32", "rajadas de erro de até 32 bits", "adulteração intencional", "PNG, ZIP, gzip, Ethernet"], ["SHA-256 / HMAC", "qualquer mudança, inclusive proposital", "—", "`Arcane.Crypto`, `Arcane.Integridade`"]]}},
  {"callout": {"tipo": "perigo", "titulo": "CRC não é segurança", "texto": "Quem altera o arquivo de propósito recalcula o CRC em microssegundos. Para saber se alguém **mexeu**, é hash criptográfico com chave: [`Arcane.Integridade`](/docs/seguranca/integridade)."}},
];

const headings = [{ id: 'a-soma-do-cabecalho-ipv4', text: "A soma do cabeçalho IPv4", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"CRC e soma de conferência"}
      description={"CRC-32 do PNG e do ZIP, e a soma de complemento de um do cabeçalho IP — com o vetor da RFC."}
      href={"/docs/estruturas/conferencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
