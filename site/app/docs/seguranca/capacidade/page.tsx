// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_e_seguranca.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Fronteira de capacidade",
  description: "Rodar uma ação com os poderes que ela pode alcançar — e a lista honesta do que isto não é.",
};

const blocos: Bloco[] = [
  {"p": "O [`comptime`](/docs/metaprogramacao/comptime) já recusava `out`, `adopt`, `thread` e `parallel`: é uma fronteira de capacidade escrita à mão, para um caso só. E o [`--plugin=`](/docs/metaprogramacao/plugins) roda um `.df` arbitrário do projeto com **todos** os poderes — uma regra de lint que pode abrir soquete."},
  { code: `adopt Arcane.Capacidade as Cap

// a formula do usuario calcula, e so
action formula():
    adopt Arcane.Math as M
    yield M.sqrt(16) + len("abc")

assert Cap.executar(formula, []) is 7.0`, lang: 'df' },
  { code: `adopt Arcane.Capacidade as Cap

action ler_disco():
    adopt Arcane.IO as IO
    yield IO.exists(".")

// sem permissao, o adopt e recusado pelo NOME da capacidade
monitor:
    Cap.executar(ler_disco, [])
    assert no
handle Error as e:
    assert "arquivos" in e.message
    assert "Arcane.IO" in e.message

// com ela, o mesmo codigo passa
assert Cap.executar(ler_disco, ["arquivos"])`, lang: 'df' },
  {"h2": "As capacidades"},
  {"table": {"head": ["Capacidade", "O que libera"], "rows": [["`arquivos`", "`Arcane.IO`, `Archive`, `Excel`, `ArquivoSeguro`, `Lago`"], ["`rede`", "`Http`, `Rede`, `Web`, `Email`, `Malha`, `Kiln`, `Vitrine`"], ["`processo`", "`OS` e `Process` — o sistema e outros processos"], ["`banco`", "`Database`, `Forge`, e o que persiste"], ["`threads`", "`Concurrent`, `Async`, `Laco`, `Stm`"], ["`nativo`", "`Arcane.C` — memória sem rede de proteção, a fronteira mais insegura que existe aqui"], ["`python`", "a ponte, que alcança **tudo** o que o Python alcança"], ["`ambiente`", "variáveis de ambiente e argumentos"]]}},
  {"p": "Um nome inventado é **recusado com a lista**: um erro de digitação concederia silenciosamente nada, e a fronteira pareceria mais aberta do que é."},
  { code: `adopt Arcane.Capacidade as Cap

// descobrir de que uma acao precisa: rode sem nada e leia os negados
action tenta():
    monitor:
        adopt Arcane.OS as OS
        yield OS.name()
    handle Error:
        yield "negado"

r := Cap.observar(tenta, [])
assert r["negados"][0]["capacidade"] is "processo"
assert Cap.exige("Arcane.OS") is "processo"
assert Cap.exige("Arcane.Math") is void      // inofensivo`, lang: 'df' },
  {"h2": "O que isto NÃO é"},
  {"callout": {"tipo": "atencao", "titulo": "Não é uma caixa contra programa hostil", "texto": "Escrito assim de propósito: um módulo chamado *Sandbox* que prometesse contenção seria usado onde não pode ser usado, e a descoberta viria por incidente. `Cap.limites()` devolve esta lista em tempo de execução, para quem for ler pelo código."}},
  {"table": {"head": ["Limite", "Por quê"], "rows": [["**não tira o que foi ENTREGUE**", "passar o módulo é passar o poder junto. **Isso é o modelo**, não um defeito: numa linguagem de capacidade, poder é o que se passa, não o que está no ar — e é por isso que bloquear o `adopt` é a fronteira certa"], ["a ponte para o Python é capacidade **própria**", "ela alcança tudo o que o Python alcança; deixá-la junto de outra faria o resto da lista virar enfeite"], ["a lista de módulos é escrita à mão", "um erro nela é um furo. Contra código **que você escreveu e revisou** — plugin, fórmula de usuário, `comptime` — isto vale"], ["contra código malicioso, não use isto", "use processo separado, contêiner, ou o sistema operacional"]]}},
  { code: `adopt Arcane.Capacidade as Cap
adopt Arcane.IO as IO

// IO foi ENTREGUE por quem chamou: o cofre nao o retira
action com_o_que_recebeu(ferramenta):
    yield ferramenta.exists(".")

assert Cap.executar(com_o_que_recebeu, [], [IO])`, lang: 'df' },
  {"p": "E a fronteira **se desfaz sempre** — inclusive quando o corpo falha. Uma fronteira que não se desfizesse travaria o programa inteiro, e é o `finally` que garante isso."},
];

const headings = [{ id: 'as-capacidades', text: "As capacidades", level: 2 as const }, { id: 'o-que-isto-nao-e', text: "O que isto NÃO é", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Fronteira de capacidade"}
      description={"Rodar uma ação com os poderes que ela pode alcançar — e a lista honesta do que isto não é."}
      href={"/docs/seguranca/capacidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
