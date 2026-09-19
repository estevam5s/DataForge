// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_backend.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O backend, e o que ele não é",
  description: "Não há LLVM, não há código de máquina e não há target triple. O que existe no lugar, e por que a troca é essa.",
};

const blocos: Bloco[] = [
  {"p": "Esta página existe porque a pergunta aparece, e porque a resposta certa é um **não** com o motivo — não um silêncio."},
  {"h2": "O que não existe"},
  {"table": {"head": ["Pedido", "Resposta"], "rows": [["emitir LLVM IR", "**não existe**. Emitir texto de IR é fácil; o que vem depois não é — seria preciso `llc` ou `clang` instalado, e aí a linguagem passaria a **depender** de um compilador C para rodar"], ["`llvmlite`, `cffi`, qualquer backend em pacote", "**recusado por regra**: `dataforge/` não tem dependência externa, e é isso que faz `pip install dataforge-lang` bastar"], ["passes LLVM em C++", "**não se aplica**: não há IR para um passe transformar"], ["target triple, cross compiler, RISC-V, WebAssembly, bare-metal", "**não existe**. Não há código de máquina a produzir para alvo nenhum"], ["debug info (DWARF), intrinsics", "**não se aplica**. A informação de depuração existe, mas é a da linguagem: linha, coluna e o [DAP](/docs/tecnicas/editor)"]]}},
  {"callout": {"tipo": "nota", "titulo": "O teto está medido", "texto": "A compilação para fechamentos rende **1,5× a 1,8×** conforme a carga, e o teto da técnica — o mesmo de uma VM de bytecode escrita em Python — é **~6,5×**. Passar disso exige sair do Python, e aí não é mais esta linguagem. O número está medido, não estimado: `tests/test_desempenho.py`."}},
  {"h2": "O que existe no lugar"},
  {"table": {"head": ["Em vez de", "O DataForge tem"], "rows": [["backend de código de máquina", "`compilador.py` — a árvore vira fechamentos Python, uma vez, com a cobertura **medida** pelo [LIR](/docs/compilador/analises)"], ["passes customizados em C++", "[plugins do `check`](/docs/metaprogramacao/plugins) escritos **em DataForge**, que agora veem o MIR e o SSA por `Arcane.Compilador`"], ["calling convention e ABI lowering", "existem, e são de verdade — mas só na fronteira com o C: [`Arcane.C`](/docs/ffi/c) declara a assinatura e o `ctypes` aplica a ABI da plataforma"], ["cross compilation", "o **release** constrói nas quatro plataformas (Linux, macOS Intel, macOS ARM, Windows), com `.deb`, PKGBUILD e instalador do Windows; e `dataforge devops` gera Dockerfile e manifesto para outra arquitetura"], ["instrumentação", "o [MIR](/docs/compilador/mir) e o [SSA](/docs/compilador/ssa) como dado, e `Arcane.Macro` para reescrever corpo de ação"]]}},
  {"h2": "Um passe próprio, escrito na linguagem"},
  {"p": "É o análogo honesto de \"custom pass\": não um `.so` carregado no otimizador, mas uma regra que lê as mesmas representações e devolve diagnóstico."},
  { code: `adopt Arcane.Compilador as K

// A regra: acusar ramo que nunca roda, com o corpo e a linha.
action verificar(fonte):
    achados := []
    cycle morto in K.ramos_mortos(fonte):
        achados.append($"{morto["corpo"]}:{morto["linha"]} ramo {morto["rotulo"]} nao roda")
    yield achados

suspeito := "x := 1\\ngiven x bigger 5:\\n    out 1\\notherwise:\\n    out 2\\n"
assert len(verificar(suspeito)) bigger 0
assert len(verificar("given entrada:\\n    out 1\\n")) is 0`, lang: 'df' },
  {"p": "A diferença entre isso e um passe do LLVM é real e vale dizer: um passe do LLVM **transforma** o IR que vai gerar código; isto **relata**. Transformar a árvore também é possível — é o que os [passes de otimização](/docs/compilador/otimizacao) fazem —, mas o ganho medido ali é 1,01×, e essa é a razão pela qual a instrumentação é o uso que paga."},
];

const headings = [{ id: 'o-que-nao-existe', text: "O que não existe", level: 2 as const }, { id: 'o-que-existe-no-lugar', text: "O que existe no lugar", level: 2 as const }, { id: 'um-passe-proprio-escrito-na-linguagem', text: "Um passe próprio, escrito na linguagem", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O backend, e o que ele não é"}
      description={"Não há LLVM, não há código de máquina e não há target triple. O que existe no lugar, e por que a troca é essa."}
      href={"/docs/compilador/backend"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
