// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Os tipos de um campo",
  description: "Inteiros com e sem sinal, ponto flutuante, booleano, texto e bytes de tamanho fixo — e a faixa que cada um aceita.",
};

const blocos: Bloco[] = [
  {"p": "Um campo binário não tem \"um número\": tem um número de **N bits**, com ou sem sinal. Escolher o tipo é escolher a faixa — e um valor fora dela, num formato binário, não dá erro sozinho: ele é **truncado**, e o arquivo sai com outro número. `Arcane.Estrutura` confere a faixa na escrita."},
  {"table": {"head": ["Tipo", "Bytes", "Faixa", "Uso típico"], "rows": [["`u8` / `i8`", "1", "0 a 255 / −128 a 127", "byte cru, flag, contador pequeno"], ["`u16` / `i16`", "2", "0 a 65.535 / ±32.767", "porta de rede, amostra de áudio"], ["`u32` / `i32`", "4", "0 a 4,29 bi / ±2,1 bi", "tamanho de arquivo, id, cor RGBA"], ["`u64` / `i64`", "8", "0 a 1,8×10¹⁹", "timestamp em ns, deslocamento em arquivo grande"], ["`f32` / `f64`", "4 / 8", "~7 / ~15 dígitos", "medida física, coordenada"], ["`bool`", "1", "`yes` / `no`", "flag isolada"], ["`char` N", "N", "texto de até N bytes em UTF-8", "nome fixo, código de 4 letras"], ["`bytes` N", "N", "N bytes crus", "assinatura mágica, hash, chave"]]}},
  { code: `adopt Arcane.Estrutura as Est

Leitura := Est.definir("Leitura", [
    ["sensor", "u16"], ["temperatura", "f32"], ["ok", "bool"], ["rotulo", "char", 6]])

b := Leitura({"sensor": 7, "temperatura": 21.5, "ok": yes, "rotulo": "sala"})
assert Leitura.ler(b) is {"sensor": 7, "temperatura": 21.5, "ok": yes, "rotulo": "sala"}
assert Est.tamanho_de("u16") is 2 and Est.tamanho_de("f64") is 8

estourou := no
monitor:
    Leitura({"sensor": 70000})             // u16 vai até 65535
handle BufferOverflowError as e:
    estourou := yes
    out e.message
assert estourou`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`f32` perde precisão", "texto": "`21.5` volta 21.5 porque é exato em binário; `0.1` gravado em `f32` volta `0.10000000149011612`. Para dinheiro, nunca ponto flutuante: `i64` em centavos."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Os tipos de um campo"}
      description={"Inteiros com e sem sinal, ponto flutuante, booleano, texto e bytes de tamanho fixo — e a faixa que cada um aceita."}
      href={"/docs/estruturas/tipos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
