// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_e_seguranca.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Hardware, bare-metal e assembly: o mapa",
  description: "As partes 9, 14 e 16 da referência Deep Tech — e por que nenhuma delas se aplica a uma linguagem interpretada.",
};

const blocos: Bloco[] = [
  {"p": "Três partes de uma referência Deep Tech tratam do que está **abaixo** de uma linguagem interpretada: SIMD e cache, bare-metal e kernel, assembly e microarquitetura."},
  {"p": "A resposta honesta para quase tudo aqui é **não se aplica** — e esta página existe porque um silêncio seria lido como \"ainda não fizemos\", quando o certo é \"isto não é uma lacuna: é o que a escolha de ser interpretada significa\"."},
  {"h2": "42–46 · Otimização de hardware (parte 9)"},
  {"table": {"head": ["Item", "Resposta", "O que existe no lugar"], "rows": [["SIMD, AVX2, AVX-512, ARM Neon", "**não se aplica**: não há registrador vetorial alcançável do CPython", "[a ponte](/docs/tecnicas/ponte) para o `numpy`, que **é** vetorizado — `a * 2` ali é a conta do numpy, não um laço"], ["auto-vectorization", "**não se aplica**", "—"], ["cache L1/L2/L3, locality, prefetch", "**não se aplica**: o custo de um interpretador de árvore domina qualquer efeito de cache em três ordens de grandeza", "o que **paga** é tirar despacho do caminho quente — e isso está [medido](/docs/compilador/otimizacao)"], ["false sharing, cache-line padding", "**não se aplica**", "—"], ["AoS vs SoA", "**não se aplica** à memória, mas a **ideia** transfere: o [`Quadro`](/docs/dados/quadro) é colunar por dentro, e é o que torna `descrever` e `correlacao` uma passada por coluna", "[Quadro](/docs/dados/quadro)"], ["branch prediction, branchless, pipeline stalls", "**não se aplica**: quem prevê desvio é a CPU rodando o laço do CPython, não o seu `given`", "—"], ["**bit manipulation, popcount, rotate, byteswap**", "**parcial**: `Arcane.Bytes` faz `bits`, `de_bits`, `ou_exclusivo`, `inverter` e empacotamento com endianness", "[Bytes](/docs/biblioteca)"], ["fences, atomic primitives", "existem, e são de verdade: `C.atomico` com CAS", "[Sem trava](/docs/concorrencia/sem-trava)"], ["cycle counters, hardware performance counters", "**não se aplica**: o CPython não os expõe", "[percentis e pausas](/docs/observabilidade/perfil)"]]}},
  {"h2": "62–64 · Bare-metal e embarcados (parte 14)"},
  {"table": {"head": ["Item", "Resposta"], "rows": [["ausência de sistema operacional, entry points, linker scripts", "**não se aplica**: o DataForge precisa de um Python, e um Python precisa de um sistema operacional"], ["memory maps, interrupt vectors, MMIO, volatile", "**não se aplica**"], ["kernel entry, page tables, syscalls, context switching", "**não se aplica**. A única troca de contexto aqui é a das [fibras](/docs/runtime/fibras), e ela é um quadro de gerador"], ["microcontroladores, ARM Cortex-M, RISC-V MCU, RTOS", "**não se aplica**. Existe MicroPython para essa faixa, e ele não é esta linguagem"], ["device drivers, DMA, low-power", "**não se aplica** — mas falar com uma biblioteca C que fale com o dispositivo, sim: é [`Arcane.C`](/docs/ffi/c)"]]}},
  {"h2": "67–68 · Assembly e microarquitetura (parte 16)"},
  {"table": {"head": ["Item", "Resposta"], "rows": [["inline assembly, external assembly, registers, CPU flags", "**não se aplica**"], ["**calling conventions, ABI, stack frames**", "existem, e são reais — mas **só na fronteira com o C**: [`Arcane.C`](/docs/ffi/c) declara a assinatura e o `ctypes` aplica a ABI da plataforma, com tamanho, alinhamento e padding de verdade"], ["atomic instructions", "`C.atomico` (CAS), sobre as primitivas do Python"], ["pipeline, superscalar, out-of-order, register renaming", "**não se aplica**: isso acontece na CPU, abaixo do CPython, abaixo do interpretador"], ["TLB, memory ordering, hardware prefetching", "**não se aplica**"], ["speculative execution", "**não se aplica** — e vale notar que a ausência de ponteiro cru na linguagem tira o DataForge da superfície de ataque de Spectre por construção"]]}},
  {"h2": "O resumo honesto"},
  {"p": "Das três partes, **nenhuma tem implementação a fazer**, e duas coisas transferiram: a **ideia** de layout colunar (que o `Quadro` já usa) e as **convenções de chamada**, que são reais na fronteira com o C."},
  {"callout": {"tipo": "nota", "titulo": "Por que escrever um mapa de coisas que não existem", "texto": "Porque a pergunta aparece, e um silêncio é lido como \"ainda não\". Dizer **não se aplica, e aqui está o porquê** custa uma página e evita que alguém procure por semanas uma opção que não pode existir. O teto da compilação para fechamentos está [medido em ~6,5×](/docs/compilador/backend): passar disso exige sair do Python, e aí não é mais esta linguagem."}},
];

const headings = [{ id: '4246-otimizacao-de-hardware-parte-9', text: "42–46 · Otimização de hardware (parte 9)", level: 2 as const }, { id: '6264-bare-metal-e-embarcados-parte-14', text: "62–64 · Bare-metal e embarcados (parte 14)", level: 2 as const }, { id: '6768-assembly-e-microarquitetura-parte-16', text: "67–68 · Assembly e microarquitetura (parte 16)", level: 2 as const }, { id: 'o-resumo-honesto', text: "O resumo honesto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Hardware, bare-metal e assembly: o mapa"}
      description={"As partes 9, 14 e 16 da referência Deep Tech — e por que nenhuma delas se aplica a uma linguagem interpretada."}
      href={"/docs/hardware/mapa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
