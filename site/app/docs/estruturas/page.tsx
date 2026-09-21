// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Estruturas e ponteiros",
  description: "Layout binário com campos nomeados, alinhamento conferido, janela que não copia e ponteiro com aritmética por elemento.",
};

const blocos: Bloco[] = [
  {"p": "A linguagem já tinha duas respostas para bytes, e faltava a do meio."},
  {"table": {"head": ["", "O que resolve", "O que falta"], "rows": [["`Arcane.Bytes`", "empacota e desempacota por **formato**: `'>i32 u16'`", "não tem **nome** — o resultado é posicional, e `dados[3]` três meses depois não diz nada"], ["`Arcane.C`", "`estrutura` e `ponteiro` de verdade", "é **FFI**: exige uma biblioteca nativa carregada"], ["`Arcane.Estrutura`", "campos nomeados, alinhamento, janela, ponteiro", "não fala com o C — para isso é o `Arcane.C`"]]}},
  {"p": "Ler o cabeçalho de um PNG não deveria exigir `ctypes`."},
  { code: `adopt Arcane.Estrutura as Est

steady Cabecalho := Est.definir("Cabecalho", [
    ["magia", "u32"],
    ["versao", "u16"],
    ["registros", "u16"]
], ordem := "rede")

c := Cabecalho.ler(dados)
out c["versao"]`, lang: 'df' },
  {"h2": "A ordem dos bytes é obrigatória"},
  {"callout": {"tipo": "atencao", "titulo": "Sem ela, o mesmo arquivo dá dois valores", "texto": "E nenhuma das duas máquinas falha. É a mesma cobrança do `Arcane.Bytes`, e pelo mesmo motivo. `\"rede\"` é big-endian — o de todo formato de arquivo e todo protocolo; `\"intel\"` é little-endian."}},
  {"h2": "O alinhamento é declarado, e conferido"},
  { code: `Alinhado := Est.definir("Pacote", [["a", "u8"], ["b", "u32"]])
Junto := Est.definir("Pacote", [["a", "u8"], ["b", "u32"]],
    empacotado := yes)

out Alinhado.deslocamento("b")     // 4 — o C insere 3 bytes de enchimento
out Alinhado.tamanho               // 8
out Junto.deslocamento("b")        // 1
out Junto.tamanho                  // 5`, lang: 'df' },
  {"p": "Um `u32` começa num múltiplo de 4; um `u64`, num múltiplo de 8. Adivinhar aqui é o que faz o mesmo `.struct` sair com 12 bytes de um lado e 16 do outro. E o **registro inteiro** também é alinhado ao maior campo — sem isso, um cluster deles sai torto a partir do segundo."},
  {"p": "`molde.mapa()` devolve a tabela do layout (campo, tipo, deslocamento, bytes) e `molde.enchimento()` diz quantos bytes são só alinhamento."},
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/estruturas/janelas", "title": "Blocos e janelas", "desc": "Ler e escrever no lugar, sem copiar."}, {"href": "/docs/estruturas/ponteiros", "title": "Ponteiros", "desc": "Aritmética por elemento, cast, distância e o nulo."}]},
];

const headings = [{ id: 'a-ordem-dos-bytes-e-obrigatoria', text: "A ordem dos bytes é obrigatória", level: 2 as const }, { id: 'o-alinhamento-e-declarado-e-conferido', text: "O alinhamento é declarado, e conferido", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Estruturas e ponteiros"}
      description={"Layout binário com campos nomeados, alinhamento conferido, janela que não copia e ponteiro com aritmética por elemento."}
      href={"/docs/estruturas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
