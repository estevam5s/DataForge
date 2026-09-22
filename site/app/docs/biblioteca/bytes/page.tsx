// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/plataforma.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Bytes",
  description: "Dados binários: empacotar com a ordem declarada, um cursor que anda, e a janela que olha sem copiar.",
};

const blocos: Bloco[] = [
  {"p": "A linguagem tem o tipo `Bytes`, e não havia o que fazer com ele. Ler um arquivo binário, falar um protocolo, montar um cabeçalho de quatro bytes — tudo isso pedia sair da linguagem."},
  {"h2": "A ordem dos bytes é obrigatória"},
  {"p": "`empacotar(\"i32\", 1)` **não existe** aqui. O formato sempre diz a ordem:"},
  { code: `Bytes.empacotar(">i32", 1)     // 00 00 00 01   ordem de rede
Bytes.empacotar("<i32", 1)     // 01 00 00 00   ordem do Intel`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "Por que ela não pode ser opcional", "texto": "Um inteiro escrito na ordem da **máquina** e lido na ordem da rede dá um número diferente, o programa **não falha**, e o dado sai errado do outro lado. É a falha mais cara desta área inteira, e um padrão silencioso a esconderia até o dia em que o servidor mudasse de arquitetura."}},
  {"h2": "Os tipos"},
  {"table": {"head": ["Escrita", "O quê", "Bytes"], "rows": [["`i8` `u8`", "inteiro de 8 bits, com e sem sinal", "1"], ["`i16` `u16`", "16 bits", "2"], ["`i32` `u32`", "32 bits", "4"], ["`i64` `u64`", "64 bits", "8"], ["`f32` `f64`", "ponto flutuante", "4 / 8"], ["`bool`", "verdadeiro ou falso", "1"], ["`bytesN`", "um bloco de tamanho fixo", "N"]]}},
  {"p": "Os nomes dizem o **tamanho em bits**, e não uma letra. `i32` é um inteiro de 32 bits em qualquer máquina; o `int` do C não é — e descobrir isso depois de gravar um arquivo é caro."},
  {"h2": "Um cabeçalho de protocolo"},
  { code: `adopt Arcane.Bytes as Bytes

// versão (1), tipo (1), tamanho (4) — escrito assim, e não com contas
cabecalho := Bytes.empacotar(">u8 u8 u32", 1, 7, 1024)
out Bytes.hex(cabecalho, " ")          // mostra 01 07 00 00 04 00

partes := Bytes.desempacotar(">u8 u8 u32", cabecalho)
assert partes is [1, 7, 1024]`, lang: 'df' },
  {"h2": "O cursor anda sozinho"},
  {"p": "Ler com fatias exige calcular o deslocamento de cada campo, e **um erro num deles desalinha tudo o que vem depois** — com o programa entregando números plausíveis e errados."},
  { code: `leitor := Bytes.ler(mensagem)

versao := leitor.ler("u8")
tipo := leitor.ler("u8")
tamanho := leitor.ler("u32")
corpo := leitor.ler_bytes(tamanho)

assert leitor.acabou`, lang: 'df' },
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`leitor.ler(tipo)`", "um campo, e anda"], ["`leitor.ler(tipo, n)`", "`n` campos iguais"], ["`leitor.ler_bytes(n)`", "um bloco"], ["`leitor.ler_texto(n)`", "um bloco, como texto"], ["`leitor.ler_ate_zero()`", "texto terminado em zero, como num formato antigo"], ["`leitor.espiar(n)`", "olha **sem** andar, para decidir o que vem"], ["`leitor.pular(n)` · `leitor.ir_para(p)`", "move o cursor"], ["`leitor.resto()`", "tudo o que sobrou"], ["`leitor.sobrou` · `leitor.acabou`", "onde estamos"]]}},
  {"p": "Ler além do fim diz **quanto falta**, em vez de estourar calado:"},
  { code: `erro: faltam bytes para ler 'u32': o cursor está em 1, o campo pede 4
      e só há 1 até o fim.`, lang: 'text' },
  {"h2": "Escrever"},
  { code: `e := Bytes.escrever()
e.escrever("u8", 2)
e.escrever("u32", 99)
e.escrever_texto("fim", com_zero := yes)
bloco := e.finalizar()`, lang: 'df' },
  {"h2": "A janela não copia"},
  {"p": "Copiar um arquivo de 200 MB para ler 8 bytes é o jeito mais fácil de estourar a memória. A janela aponta para os mesmos bytes:"},
  { code: `pedaco := Bytes.janela(arquivo_inteiro, 100, 108)   // não copia
guardado := Bytes.copiar(pedaco)                    // agora sim`, lang: 'df' },
  {"h2": "Ver o que está errado"},
  {"p": "O despejo é o que se olha quando o protocolo não bate — posição, hexadecimal e o texto legível, lado a lado:"},
  { code: `out Bytes.despejo(mensagem)`, lang: 'df' },
  { code: `00000000  01 07 00 00 04 00 44 61 74 61 46 6f 72 67 65     |......DataForge|`, lang: 'text' },
  {"h2": "Segredo se compara em tempo fixo"},
  { code: `given Bytes.igual_em_tempo_fixo(token_recebido, token_certo):
    out "ok"`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "Por que não `is`", "texto": "Uma comparação comum para no primeiro byte diferente, e o **tempo** conta quantos bateram. Com isso, um atacante descobre um token byte a byte — sem nunca acertar o token inteiro por sorte."}},
  {"h2": "O resto"},
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`hex(dados[, sep])` · `de_hex(texto)`", "hexadecimal, ida e volta"], ["`base64(dados)` · `de_base64(texto)`", "base64"], ["`bits(dados)` · `de_bits(texto)`", "a representação em bits"], ["`de_texto(t)` · `para_texto(d)`", "texto ⇄ bytes"], ["`concatenar(...)` · `fatiar(d, i, f)`", "juntar e cortar"], ["`ou_exclusivo(a, b)`", "XOR byte a byte"], ["`preencher(d, n, com, a_esquerda)`", "completa até o tamanho"], ["`achar(d, agulha)` · `dividir(d, sep)`", "procurar"], ["`inverter(d)`", "de trás para frente"]]}},
  {"cards": [{"href": "/docs/exercicios/34-binario-e-rede", "title": "O exercício 235", "desc": "Monta e lê um cabeçalho de protocolo, e prova cada afirmação desta página."}]},
];

const headings = [{ id: 'a-ordem-dos-bytes-e-obrigatoria', text: "A ordem dos bytes é obrigatória", level: 2 as const }, { id: 'os-tipos', text: "Os tipos", level: 2 as const }, { id: 'um-cabecalho-de-protocolo', text: "Um cabeçalho de protocolo", level: 2 as const }, { id: 'o-cursor-anda-sozinho', text: "O cursor anda sozinho", level: 2 as const }, { id: 'escrever', text: "Escrever", level: 2 as const }, { id: 'a-janela-nao-copia', text: "A janela não copia", level: 2 as const }, { id: 'ver-o-que-esta-errado', text: "Ver o que está errado", level: 2 as const }, { id: 'segredo-se-compara-em-tempo-fixo', text: "Segredo se compara em tempo fixo", level: 2 as const }, { id: 'o-resto', text: "O resto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Bytes"}
      description={"Dados binários: empacotar com a ordem declarada, um cursor que anda, e a janela que olha sem copiar."}
      href={"/docs/biblioteca/bytes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
