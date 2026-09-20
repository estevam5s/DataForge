// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O que não existe, e o que está no lugar",
  description: "Cinco componentes do desenho não existem. Cada um com o que faz a diferença: o motivo, o que responde pela mesma pergunta, e o número medido do substituto.",
};

const blocos: Bloco[] = [
  {"p": "Esta é a página que uma referência técnica quase nunca tem, e é a mais útil de todas: **o que a linguagem não faz.**"},
  {"p": "Um mapa que marca tudo como pronto não é um mapa, é publicidade. Quem o lê descobre a ausência ao tentar — no pior momento, e depois de ter escolhido a linguagem por causa dele."},
  {"callout": {"tipo": "nota", "titulo": "A regra que este repositório segue", "texto": "Nomear a ausência **com o motivo** e, quando houver, com o número medido do que está no lugar. Publicar o número mesmo quando ele é decepcionante: a otimização que rendeu 1,01×, o laço de eventos que ficou em ~1,1× a versão com threads. Um número ruim publicado vale mais que um bom prometido."}},
  {"h2": "Backend LLVM, e gerador de código"},
  {"p": "As duas maiores ausências, e são a mesma: **não há compilação para código de máquina.**"},
  {"table": {"head": ["No desenho", "Aqui", "Medido"], "rows": [["`LLVM Backend`", "`compilador.py` — a árvore é percorrida uma vez e vira fechamentos Python, o que tira o despacho do caminho quente", "**1,5× a 1,8×** conforme a carga"], ["`Code Generator`", "não há. O que sai do compilador é um fechamento, e quem o executa é `interpreter.py`", "—"], ["`Machine Code / WASM`", "não há. O artefato é a árvore compilada, em memória", "—"]]}},
  {"p": "O motivo não é falta de tempo. Amarrar o LLVM tiraria **a única propriedade inegociável do projeto**: zero dependência externa no runtime. E o teto desta técnica é conhecido."},
  {"callout": {"tipo": "atencao", "titulo": "O teto é ~6,5×, e ele não é do compilador de fechamentos", "texto": "É o teto de **qualquer** técnica que fique dentro do Python — inclusive uma VM de bytecode escrita em Python. O resto exigiria sair do CPython, que é outra linguagem de implementação, não outra fase do compilador. Dizer \"ainda não temos backend\" sugeriria que ele vem depois; a verdade é que ele é uma decisão de arquitetura, e ela está tomada."}},
  {"p": "A fase continua **no mapa**, marcada como ausente. Uma fase apagada do desenho não deixa a ausência aparecer — e é em `dataforge ir --fase=lir` que ela fica visível, porque o LIR mostra o que desceu para fechamento e o que **recuou** para a árvore."},
  {"h2": "Gerenciador de versões, e workspace — eram ausências, e não são mais"},
  {"p": "Esta seção descrevia duas ausências. Elas foram fechadas, e o que ficou no lugar vale mais registrado que apagado — porque o **limite** de cada uma é o que decide se ela serve."},
  {"table": {"head": ["O que era ausência", "O que existe agora", "O limite"], "rows": [["não havia como manter versões lado a lado", "uma venv por versão em `~/.dataforge/versoes/<versao>`, e `dataforge versions` lista", "instalar precisa de rede e de `pip`"], ["não havia como fixar a versão por projeto", "`dataforge use <versao>` escreve `dataforge = \"…\"` no `[project]` do `forge.toml` — **linha a linha**, sem apagar comentários", "o campo já existia e ninguém o cobrava: `dataforge info` o mostrava, e era tudo"], ["trocar de versão era reinstalar", "`dataforge upgrade` instala **ao lado**: a versão que já roda não é tocada", "um upgrade que falha no meio não deixa a máquina sem DataForge"], ["nada olhava a árvore de pacotes inteira", "`dataforge workspace` acha todo `forge.toml` e acusa faixa incompatível, saindo com 2", "ele **lê e relata**: não instala"]]}},
  {"callout": {"tipo": "atencao", "titulo": "O pino é COBRADO — senão `use` seria um gesto", "texto": "`dataforge run` num projeto que exige outra versão **entrega a execução a ela** (`os.execve`), quando ela está instalada. Quando não está, **recusa** e diz o comando que a instala. Sem essa troca, `use` escreveria num arquivo e nada aconteceria — e um comando que finge é pior que um comando que falta. `DATAFORGE_SEM_TROCA=1` ignora o pino uma vez, e uma marca no ambiente impede a troca de acontecer duas vezes: um laço na partida é o defeito mais difícil de interromper."}},
  {"p": "O limite que fica: **não há um *shim* no PATH**. O `dataforge` que você chama é o que está instalado, e é ele que redireciona — ver [versões](/docs/cli/versoes)."},
  {"h2": "Alocador"},
  {"p": "O alocador é o do CPython, e trocá-lo exigiria estar do lado de fora dele. O que se pode fazer daqui — e se faz — é **mandar no coletor** e medir a pausa dele."},
  {"table": {"head": ["O que existe", "Onde"], "rows": [["arena: alocar em bloco e soltar de uma vez", "`Arcane.Memoria.Arena`"], ["ligar, desligar e rodar sem coletor num trecho", "`gc_ligar`, `gc_desligar`, `sem_gc`"], ["mudar os limiares das três gerações", "`gc_limiares`, `gc_geracoes`"], ["congelar o que já existe, para não ser varrido de novo", "`gc_congelar`"], ["**medir a pausa** de cada coleta", "`Arcane.Perfil.gc_pausas`"], ["referência fraca e mapa fraco", "`Arcane.Memoria`"]]}},
  {"p": "A diferença entre \"controlar memória\" e \"controlar o coletor\" é real, e o projeto prefere nomeá-la a fingir que são a mesma coisa."},
  {"h2": "Bare-metal, kernel, microcontrolador"},
  {"p": "Não há, e **não há caminho a partir daqui**: o runtime é o CPython."},
  {"p": "Isso não fica como um silêncio. [`Arcane.Alvo`](/docs/alvos/portabilidade) descreve o alvo `embarcado` e diz, capacidade por capacidade, o que falta — não há `threading` do CPython, não há `ctypes`, e não é o CPython: é outro interpretador, com outra biblioteca padrão."},
  {"callout": {"tipo": "nota", "titulo": "Por que a ausência é descrita em detalhe", "texto": "Para que ela apareça **antes** de alguém tentar. Uma ausência silenciosa custa a tarde de quem descobre; uma ausência descrita custa trinta segundos de leitura."}},
  { code: `adopt Arcane.Ecossistema as Eco

// As tres marcas, e o que cada uma quer dizer
assert "existe" in Eco.ESTADOS
assert "equivale" in Eco.ESTADOS
assert "nao-existe" in Eco.ESTADOS

faltam := Eco.o_que_nao_existe()
cycle f in faltam:
    assert f["porque"] is not ""       // toda ausencia tem motivo escrito

// e o que esta no lugar, quando ha algo no lugar
outra := Eco.equivalencias()
assert len(outra) bigger 0
out $"{len(faltam)} ausencias, {len(outra)} equivalencias"`, lang: 'df' },
  {"h2": "O `equivale` não é um consolo"},
  {"p": "Seis componentes estão marcados como `equivale`, e a distinção com `existe` é estrita: há **outra peça**, nomeada, que responde a mesma pergunta por outro mecanismo."},
  {"table": {"head": ["No desenho", "O que está no lugar", "Por que não é a mesma coisa"], "rows": [["`Borrow Checker`", "`Arcane.Posse` + três códigos do `check`", "não há tempo de vida declarado; o que se protege é o **protocolo** (soltar uma vez, não usar depois), e não a integridade da memória — essa nunca esteve em risco"], ["`Build System`", "`forge.toml` + `dataforge devops`", "não havendo compilação para binário, não há etapa de build a orquestrar: o artefato é o código mais o `forge.lock`"], ["`ABI` e símbolos", "`Arcane.Abi`", "não há layout binário a quebrar — e há **exatamente o mesmo problema**, com o mesmo sintoma cruel: não é erro de quem publicou, é de quem consome, depois"], ["`RISC-V`", "nada de arquitetura no projeto", "onde há CPython 3.10+, roda. **Não é testado**, e dizer \"suportado\" seria prometer o que ninguém verificou"], ["`WASM`", "Pyodide", "**compilar para** WASM não existe; **rodar em** WASM funciona, com o interpretador inteiro junto"], ["`Driver` (`dfc`)", "o próprio `dataforge`", "um segundo executável duplicaria a resolução de caminho e a leitura do `forge.toml`"]]}},
];

const headings = [{ id: 'backend-llvm-e-gerador-de-codigo', text: "Backend LLVM, e gerador de código", level: 2 as const }, { id: 'gerenciador-de-versoes-e-workspace-eram-ausencias-e-nao-sao-mais', text: "Gerenciador de versões, e workspace — eram ausências, e não são mais", level: 2 as const }, { id: 'alocador', text: "Alocador", level: 2 as const }, { id: 'bare-metal-kernel-microcontrolador', text: "Bare-metal, kernel, microcontrolador", level: 2 as const }, { id: 'o-equivale-nao-e-um-consolo', text: "O `equivale` não é um consolo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O que não existe, e o que está no lugar"}
      description={"Cinco componentes do desenho não existem. Cada um com o que faz a diferença: o motivo, o que responde pela mesma pergunta, e o número medido do substituto."}
      href={"/docs/ecossistema/ausencias"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
