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
  {"h2": "Do campo ao formato de arquivo"},
  {"p": "Tipos e faixas, alinhamento, ordem dos bytes, texto de tamanho fixo, bits, varint, CRC — e PNG, WAV e um protocolo binário inteiros, lidos e escritos."},
  {"cards": [{"href": "/docs/estruturas/tipos", "title": "Os tipos de um campo", "desc": "Inteiros com e sem sinal, ponto flutuante, booleano, texto e bytes de tamanho fixo — e a faixa que cada um aceita."}, {"href": "/docs/estruturas/alinhamento", "title": "Alinhamento e enchimento", "desc": "Por que u8 + u32 + u16 ocupa 12 bytes e não 7, como reduzir, e quando empacotar."}, {"href": "/docs/estruturas/ordem-dos-bytes", "title": "A ordem dos bytes", "desc": "Big-endian, little-endian, a ordem da rede, e o bswap — com o mesmo número lido dos dois jeitos."}, {"href": "/docs/estruturas/textos", "title": "Texto de tamanho fixo", "desc": "O char[N] do C: completado com zeros, lido até o primeiro zero — e o acento que não cabe."}, {"href": "/docs/estruturas/bits", "title": "Campos de bits", "desc": "Versão e tamanho do IPv4 no mesmo byte, as flags do TCP em 16 bits — com máscara, e nunca com o bitfield do C."}, {"href": "/docs/estruturas/operacoes-de-bits", "title": "Operações de bits", "desc": "E, OU, OU exclusivo, NÃO com largura, deslocamento e contagem — como funções, e por que não operadores."}, {"href": "/docs/estruturas/varint", "title": "Varint e zigzag", "desc": "O inteiro de tamanho variável do Protocol Buffers e do WebAssembly: 7 bits por byte, e o truque para os negativos."}, {"href": "/docs/estruturas/png", "title": "Ler um PNG de verdade", "desc": "Assinatura, chunks, tamanho em big-endian e o CRC de cada um — o formato inteiro, sem biblioteca de imagem."}, {"href": "/docs/estruturas/wav", "title": "Escrever um WAV", "desc": "O cabeçalho RIFF de 44 bytes, em little-endian, e um segundo de onda senoidal escrito amostra por amostra."}, {"href": "/docs/estruturas/protocolo", "title": "Um protocolo binário", "desc": "Mensagens TLV — tipo, tamanho, valor — com varint: escrever, ler, e o campo desconhecido que não quebra ninguém."}, {"href": "/docs/estruturas/arquivo-mapeado", "title": "Arquivo mapeado em memória", "desc": "Um arquivo de gigabytes como um bloco, sem lê-lo inteiro: o sistema traz só as páginas tocadas."}, {"href": "/docs/estruturas/conferencia", "title": "CRC e soma de conferência", "desc": "CRC-32 do PNG e do ZIP, e a soma de complemento de um do cabeçalho IP — com o vetor da RFC."}, {"href": "/docs/estruturas/entrada-hostil", "title": "Ler entrada hostil", "desc": "Todo tamanho que vem do arquivo é suspeito: as cinco conferências antes de interpretar um byte."}, {"href": "/docs/estruturas/de-c-para-dataforge", "title": "De uma struct do C para um molde", "desc": "Traduzir uma struct, conferir o layout contra o próprio C, e o #pragma pack."}, {"href": "/docs/estruturas/receitas", "title": "Receitas binárias", "desc": "Hexdump, cor RGBA num u32, deslocamento de bits sem molde, e um vetor de registros ordenado no lugar."}]},
];

const headings = [{ id: 'a-ordem-dos-bytes-e-obrigatoria', text: "A ordem dos bytes é obrigatória", level: 2 as const }, { id: 'o-alinhamento-e-declarado-e-conferido', text: "O alinhamento é declarado, e conferido", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }, { id: 'do-campo-ao-formato-de-arquivo', text: "Do campo ao formato de arquivo", level: 2 as const }];

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
