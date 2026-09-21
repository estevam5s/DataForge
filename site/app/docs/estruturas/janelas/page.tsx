// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Blocos e janelas",
  description: "O bloco que sabe dizer quando acabou, e a janela que lê e escreve sem copiar.",
};

const blocos: Bloco[] = [
  {"h2": "O bloco"},
  { code: `b := Est.bloco(64)          // 64 bytes zerados
c := Est.de_bytes(dados)    // a partir do que já existe

out len(b)
b.liberar()                 // marca o fim`, lang: 'df' },
  {"p": "`liberar()` não devolve memória ao sistema — quem faz isso é o CPython. O que ele faz é **marcar**: a partir dali, toda janela e todo ponteiro sobre este bloco levantam em vez de ler. É idempotente, como o `soltar` do `Arcane.Posse`: um `liberar` no `defer` e no caminho de erro não pode virar erro."},
  {"h2": "A janela não copia"},
  { code: `j := Est.janela(arquivo, Registro, deslocamento := 8)

out j.ler("preco")
j.escrever("quantidade", 7)     // muda O BLOCO
j["ativo"] := yes               // o mesmo, por índice`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Por que não devolver um vault", "texto": "Copiar um registro de 4 KB para ler um campo de 2 bytes é o que faz um parser de arquivo grande levar minutos. `j.vault()` existe para quando a cópia é o que se quer — e ela deixa de acompanhar o bloco a partir dali."}},
  {"h2": "Percorrer um arquivo de registros"},
  { code: `linhas := Est.janelas(arquivo, Registro,
    deslocamento := Cabecalho.tamanho)

cycle linha in linhas:
    out linha.ler("id"), linha.ler("preco")`, lang: 'df' },
  {"p": "Sem `quantos`, ele devolve quantos couberem. Pedir mais do que cabe é **erro**, com a conta na mensagem: `cabem 2 registro(s) de 'Par' aqui, e foram pedidos 5`. E `j.proxima()` anda um registro, para quem prefere o laço explícito."},
  {"h2": "O que é recusado"},
  {"table": {"head": ["", "Sem a recusa"], "rows": [["ler além do fim do bloco", "o resultado é um número plausível, e o defeito aparece três camadas adiante"], ["um valor fora da faixa do tipo", "ele é truncado em silêncio, e o arquivo sai com outro número"], ["um campo que não existe", "a escrita iria para lugar nenhum — a mensagem sugere o nome parecido"], ["escrever num bloco somente leitura", "`bytes` não muda; a queixa sairia do Python, sobre outra coisa"], ["usar um bloco liberado", "lê-se o que ocupou o espaço depois"]]}},
  {"p": "A faixa vem do **tipo declarado**, e não do `struct` do Python: `um u8 vai de 0 a 255`, e não `'B' format requires 0 <= number <= 255` — quem escreveu `u8` não tem como ligar uma coisa à outra."},
];

const headings = [{ id: 'o-bloco', text: "O bloco", level: 2 as const }, { id: 'a-janela-nao-copia', text: "A janela não copia", level: 2 as const }, { id: 'percorrer-um-arquivo-de-registros', text: "Percorrer um arquivo de registros", level: 2 as const }, { id: 'o-que-e-recusado', text: "O que é recusado", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Blocos e janelas"}
      description={"O bloco que sabe dizer quando acabou, e a janela que lê e escreve sem copiar."}
      href={"/docs/estruturas/janelas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
