// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Operações de bits",
  description: "E, OU, OU exclusivo, NÃO com largura, deslocamento e contagem — como funções, e por que não operadores.",
};

const blocos: Bloco[] = [
  {"p": "Máscara, flag, permissão em octal, cor num inteiro, soma de conferência: tudo isso é conta **bit a bit**. As funções moram em `Arcane.Estrutura`, com nomes que dizem o que fazem:"},
  {"table": {"head": ["Função", "Faz", "No C"], "rows": [["`bits_e(a, b)`", "1 só onde os dois têm 1 — a máscara", "`a & b`"], ["`bits_ou(a, b)`", "liga o que estiver ligado em qualquer um", "`a | b`"], ["`bits_xou(a, b)`", "1 onde diferem; aplicado duas vezes, desfaz", "`a ^ b`"], ["`bits_nao(a, largura)`", "inverte dentro da largura", "`~a` (com o tipo dando a largura)"], ["`deslocar(a, n)`", "esquerda com n positivo, direita com negativo", "`a << n` / `a >> -n`"], ["`contar_uns(a)`", "quantos bits ligados", "`__builtin_popcount`"], ["`bit_ligado(a, i)` · `ligar_bit` · `desligar_bit`", "um bit só, contando de 0 embaixo", "máscara na mão"]]}},
  { code: `adopt Arcane.Estrutura as Est

// permissões do Unix: rwx para o dono, r-x para o grupo, r-- para os outros
steady LER := 4
steady ESCREVER := 2
steady EXECUTAR := 1
dono := Est.bits_ou(Est.bits_ou(LER, ESCREVER), EXECUTAR)
modo := Est.bits_ou(Est.bits_ou(Est.deslocar(dono, 6), Est.deslocar(5, 3)), 4)
assert modo is 0o754

grupo := Est.bits_e(Est.deslocar(modo, -3), 7)
assert grupo is 5
assert not Est.bit_ligado(grupo, 1)                // o grupo não escreve

assert Est.bits_nao(0b10110000, 8) is 0b01001111    // dentro de um byte
assert Est.contar_uns(0xFF) is 8
assert Est.bits_xou(Est.bits_xou(1234, 0xABCD), 0xABCD) is 1234`, lang: 'df' },
  {"h2": "Por que não operadores"},
  {"p": "Os três símbolos que toda linguagem usa já têm dono aqui: `>>` é o **pipeline**, `|` é a união de tipos e `&` a interseção. Um `a >> 2` que deslocasse bits mudaria o sentido de todo pipeline já escrito, e `a & b` numa anotação seria lido como tipo. Funções com nome não disputam nada — e `deslocar(x, -4)` diz o sentido, que é a dúvida de sempre com `>>`."},
  {"callout": {"tipo": "atencao", "titulo": "O NÃO precisa de largura", "texto": "O inteiro da linguagem não tem tamanho, e o NÃO de um número sem tamanho é negativo: `~5` no Python dá −6. `bits_nao(5, 8)` dá 250, que é o que quem inverte um byte quer — e recusa um número que não cabe na largura."}},
  {"p": "Para campos com nome dentro de um inteiro — versão e tamanho no mesmo byte —, [Campos de bits](/docs/estruturas/bits) é mais legível que máscara na mão."},
];

const headings = [{ id: 'por-que-nao-operadores', text: "Por que não operadores", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Operações de bits"}
      description={"E, OU, OU exclusivo, NÃO com largura, deslocamento e contagem — como funções, e por que não operadores."}
      href={"/docs/estruturas/operacoes-de-bits"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
