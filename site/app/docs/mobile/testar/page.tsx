// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/mobile.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testar",
  description: "A Sonda toca, volta e confere sem navegador — e o PWA é conferido servindo, como o Android o veria.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V
adopt Arcane.Crucible as Crucible

tarefas := [{"id": 1, "titulo": "Estudar", "feita": no}]
app := Br.app("Tarefas")

action inicio():
    Br.topo("Tarefas")
    Br.lista([t cycle t in tarefas given not t["feita"]],
             titulo := "titulo", destino := "/tarefa?id={id}")

action tarefa():
    t := tarefas[int(V.parametro("id")) - 1]
    Br.topo(t["titulo"], voltar := yes)
    given V.botao("Concluir"):
        t["feita"] := yes
        V.navegar("/")

Br.tela("/", inicio, titulo := "Tarefas", icone := "conferir", aba := yes)
Br.tela("/tarefa", tarefa)

crucible "o aplicativo":
    trial "concluir tira da lista":
        s := Br.testar(app)
        s.tocar("Estudar")
        s.clicar("Concluir")
        s.ir("/")
        expect len(s.itens()) is 0

    trial "o PWA tem tudo que o Android exige":
        falhas := [c cycle c in Br.conferir_pwa(app) given not c["ok"]]
        expect falhas is []

Crucible.run()`, lang: 'df' },
  {"h2": "A Sonda"},
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`s.tocar(rotulo)`", "toca numa linha da lista, numa aba ou no botão flutuante"], ["`s.voltar()` · `s.ir(caminho)`", "o gesto de voltar, e abrir uma tela"], ["`s.localizacao(lat, lon)`", "o que o navegador responderia"], ["`s.clicar` · `s.digitar`", "os da Vitrine, nos componentes dela"], ["`s.titulo()` · `s.itens()` · `s.abas()` · `s.caminho()`", "o que a tela desenhou, como dado"], ["`s.texto()` · `s.tem(texto)` · `s.html()`", "o conteúdo"]]}},
  {"p": "A Sonda não analisa o HTML: cada componente da Brasa **anota** o que desenhou (título, itens, abas, destinos), e é essa anotação que ela lê. Por isso `s.tocar(\"café\")` acha a linha pelo que o programa passou, e não por uma expressão regular."},
  {"h2": "`Br.conferir_pwa`: o que o Android exige"},
  {"p": "Ele **não** confere a configuração: sobe o aplicativo, pede cada arquivo por HTTP e olha o que chegou. Um manifesto certo servido com o tipo errado não instala — e só pedindo se descobre isso."},
  {"table": {"head": ["Conferido", "Por quê"], "rows": [["a página liga o manifesto, declara `theme-color` e registra o service worker", "sem os três, o \"instalar\" não aparece"], ["o manifesto vem como `application/manifest+json` e tem nome, `start_url`, `display` e ícones", "o que o Chrome lê para oferecer a instalação"], ["`display: standalone`", "abrir sem barra de endereço"], ["ícones PNG de 192 e 512 px, e um **maskable** de 512", "o Android recorta o ícone; o maskable deixa a margem"], ["o service worker na raiz, como JavaScript, tratando `fetch`", "fora da raiz ele não cobre o aplicativo inteiro"], ["`viewport-fit=cover`", "o conteúdo respeitar o entalhe"]]}},
];

const headings = [{ id: 'a-sonda', text: "A Sonda", level: 2 as const }, { id: 'brconferirpwa-o-que-o-android-exige', text: "`Br.conferir_pwa`: o que o Android exige", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testar"}
      description={"A Sonda toca, volta e confere sem navegador — e o PWA é conferido servindo, como o Android o veria."}
      href={"/docs/mobile/testar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
