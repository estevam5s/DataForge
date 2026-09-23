// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/posse_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O que o `check` prova",
  description: "Três diagnósticos, e — mais importante — os quatro silêncios.",
};

const blocos: Bloco[] = [
  {"p": "O analisador acusa uso depois de mover, recurso que não é solto e empréstimo que escapa. Como em todo o resto da linguagem, **o que o faz calar é tão importante quanto o que o faz falar**."},
  {"table": {"head": ["Código", "Severidade", "O quê"], "rows": [["`posse-movida`", "**erro**", "usar um dono depois de `mover()` — é provável em um arquivo só"], ["`recurso-vazado`", "aviso", "um dono criado e nunca solto naquele caminho"], ["`emprestimo-escapa`", "aviso", "o valor emprestado é guardado fora do escopo do empréstimo"]]}},
  {"p": "Os dois últimos são **aviso**, e por um motivo: a análise vê **um arquivo**, e o recurso pode ser solto por um caminho que ela não enxerga — passado para uma ação de outro módulo, guardado num escopo que fecha depois. Um erro ali reprovaria código correto."},
  {"h2": "Os quatro silêncios"},
  {"table": {"head": ["Ele cala quando", "Porque"], "rows": [["o nome **não nasceu** de `Arcane.Posse`", "o exercício 118 tem um `mover()` de máquina de estados, e a primeira versão o acusou"], ["você **pergunta o estado** (`movido`, `vivo`, `contar`)", "`assert a.movido()` depois do `mover` é justamente o que se escreve"], ["o dono é **devolvido** pela ação", "quem recebe passa a ser o dono, e o arquivo não vê isso"], ["o dono entra num **escopo**", "o escopo solta, e ele pode fechar em outro lugar"]]}},
  { code: `adopt Arcane.Posse as Posse

// Perguntar o estado é sempre legítimo — inclusive depois de mover.
d := Posse.dono({"x": 1})
novo := d.mover()
assert d.movido() is yes
assert novo.vivo() is yes

// E devolver o dono é o padrão de uma fábrica de recurso: quem
// chamou vira o dono, e o 'check' não acusa vazamento aqui.
action abrir_conexao(nome):
    yield Posse.dono({"nome": nome}, lambda v => void, nome)

c := abrir_conexao("loja")
assert c.usar(lambda v => v["nome"]) is "loja"
c.soltar()`, lang: 'df' },
  {"h2": "Silenciar de propósito"},
  {"p": "Quando o analisador está certo e o código também — um recurso solto por um caminho que ele não vê —, a saída é **nomear** a regra:"},
  { code: `adopt Arcane.Posse as Posse

action guardar_em_algum_lugar(d):
    yield d

d := Posse.dono({"x": 1})       // df: permitir recurso-vazado
guardar_em_algum_lugar(d)
out "o dono foi adiante, e quem recebe solta"`, lang: 'df' },
  {"p": "A regra tem de ser **nomeada**: um `permitir` solto esconderia o erro seguinte, que ninguém pediu para esconder. Um analisador sem escape obriga a escolher entre conviver com um alarme e desligar a verificação inteira — e a segunda é o que acontece."},
];

const headings = [{ id: 'os-quatro-silencios', text: "Os quatro silêncios", level: 2 as const }, { id: 'silenciar-de-proposito', text: "Silenciar de propósito", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O que o `check` prova"}
      description={"Três diagnósticos, e — mais importante — os quatro silêncios."}
      href={"/docs/memoria/posse/analise"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
