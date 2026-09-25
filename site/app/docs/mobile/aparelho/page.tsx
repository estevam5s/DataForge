// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/mobile.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O aparelho",
  description: "Compartilhar, ligar, abrir no mapa e a localização — pelo navegador, com a permissão do usuário.",
};

const blocos: Bloco[] = [
  {"p": "O aplicativo alcança o aparelho **pelo navegador**, com as APIs da web e a permissão do usuário. Nada disso é nativo, e cada recurso diz o que acontece onde ele não existe."},
  {"table": {"head": ["Chamada", "No celular", "Onde não há"], "rows": [["`Br.compartilhar(texto)`", "a folha do sistema (WhatsApp, e-mail…)", "copia para a área de transferência e diz \"Copiado\""], ["`Br.ligar(numero)`", "abre o discador", "o computador pergunta que aplicativo usar"], ["`Br.mapa(lat, lon)`", "abre o aplicativo de mapas", "abre o mapa no navegador"], ["`Br.localizacao()`", "pede a posição ao usuário", "exige **HTTPS** — sem ele, o botão diz isso"]]}},
  { code: `adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V

app := Br.app("Entregas")

action tela():
    Br.topo("Entrega 42")
    Br.ligar("+55 11 99999-0000", "Ligar para o cliente")
    Br.mapa(-23.5505, -46.6333, "Ver o endereço")
    Br.compartilhar("Entrega 42 a caminho")
    onde := Br.localizacao("Registrar minha posição")
    given onde isnt void:
        V.texto($"posição: {onde["lat"]}, {onde["lon"]} (±{onde["precisao"]} m)")

Br.tela("/", tela)

s := Br.testar(app)
assert not s.tem("posição:")
s.localizacao(-23.5505, -46.6333, 12)      // o que o navegador responderia
assert s.tem("posição: -23.5505, -46.6333 (±12.0 m)")`, lang: 'df' },
  {"h2": "Como a localização chega"},
  {"p": "O botão pede a posição ao navegador, que pergunta ao usuário. A resposta volta como parâmetro, a tela roda de novo com ela, e ela **fica na sessão** — a próxima tela não pede outra vez. `Br.localizacao()` devolve `{lat, lon, precisao}` ou `void`, e na Sonda `s.localizacao(lat, lon)` faz o papel do navegador."},
  {"callout": {"tipo": "atencao", "titulo": "HTTPS, de novo", "texto": "O navegador só oferece `navigator.geolocation` num contexto seguro: HTTPS ou `localhost`. Pela rede local em `http://192.168…` o botão diz \"Precisa de HTTPS para localizar\" em vez de ficar mudo."}},
  {"h2": "A câmera"},
  {"p": "É o `V.camera` da Vitrine: o navegador do celular abre a câmera traseira, e a foto chega à tela como arquivo. Ver [Vitrine](/docs/vitrine)."},
];

const headings = [{ id: 'como-a-localizacao-chega', text: "Como a localização chega", level: 2 as const }, { id: 'a-camera', text: "A câmera", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O aparelho"}
      description={"Compartilhar, ligar, abrir no mapa e a localização — pelo navegador, com a permissão do usuário."}
      href={"/docs/mobile/aparelho"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
