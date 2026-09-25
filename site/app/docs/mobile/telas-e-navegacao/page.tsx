// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/mobile.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Telas e navegação",
  description: "Registrar telas, a barra de abas, o topo com voltar, e passar parâmetros de uma tela a outra.",
};

const blocos: Bloco[] = [
  {"p": "`Br.tela(caminho, acao, titulo, icone, aba)` registra uma tela. As que têm `aba := yes` aparecem na barra de baixo — até **cinco**: acima disso o rótulo não cabe numa tela de celular, e o Material e a Apple param em cinco. As outras são telas de detalhe, abertas por uma lista ou um botão."},
  { code: `adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V

app := Br.app("Clube", cor := "#2F6FED")

action inicio():
    Br.topo("Início")
    V.texto("bem-vindo")

action agenda():
    Br.topo("Agenda")
    Br.lista([{"id": 7, "nome": "Treino"}], destino := "/evento?id={id}")

action evento():
    Br.topo($"Evento {V.parametro("id")}", voltar := yes)

Br.tela("/", inicio, titulo := "Início", icone := "casa", aba := yes)
Br.tela("/agenda", agenda, titulo := "Agenda", icone := "calendario", aba := yes)
Br.tela("/evento", evento)

s := Br.testar(app)
assert s.abas() is [{"titulo": "Início", "ativa": yes}, {"titulo": "Agenda", "ativa": no}]
s.tocar("Agenda")
s.tocar("Treino")
assert s.titulo() is "Evento 7"
assert [a["ativa"] cycle a in s.abas()] is [no, no]   // no detalhe, nenhuma acesa
s.voltar()
assert s.titulo() is "Agenda"`, lang: 'df' },
  {"h2": "O topo e o voltar"},
  {"p": "`Br.topo(titulo, voltar := yes)` desenha a seta. Ela usa o **histórico do navegador** — é o que o gesto de voltar do Android faz — e cai em `destino_voltar` (padrão `/`) quando não há para onde voltar: o aplicativo foi aberto direto naquela tela, por um link compartilhado."},
  {"h2": "Parâmetros"},
  {"p": "O destino de uma lista leva os campos do item — `\"/produto?id={id}\"` —, e a tela de destino os lê com `V.parametro(\"id\")`. Cada valor é **codificado** na URL: um id com `&` dentro não vira um segundo parâmetro."},
  {"h2": "Os ícones"},
  { code: `adopt Arcane.Vitrine as V

out len(V.icones()), "ícones"
out V.icones()[0:8]`, lang: 'df' },
  {"p": "O ícone da aba é o **nome** de um dos ícones da Vitrine (SVG escrito na página, sem CDN) ou um **emoji**. Um nome que não existe é recusado na linha que registra a tela, com sugestão — `nao ha icone 'caixa'`, *você quis dizer: baixar, casa, faisca* —, em vez de desenhar a palavra na barra."},
];

const headings = [{ id: 'o-topo-e-o-voltar', text: "O topo e o voltar", level: 2 as const }, { id: 'parametros', text: "Parâmetros", level: 2 as const }, { id: 'os-icones', text: "Os ícones", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Telas e navegação"}
      description={"Registrar telas, a barra de abas, o topo com voltar, e passar parâmetros de uma tela a outra."}
      href={"/docs/mobile/telas-e-navegacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
