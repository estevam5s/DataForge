// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_extra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O que dá para compartilhar",
  description: "Quais peças da biblioteca aguentam duas threads — e quais não, com o número medido.",
};

const blocos: Bloco[] = [
  {"p": "A pergunta prática de todo programa concorrente: **isto aqui pode ser tocado por duas threads?** A resposta não é uniforme, e supor que é dá os dois erros — travar o que não precisa, e compartilhar o que não pode."},
  {"table": {"head": ["Peça", "Compartilhar?", "Observação"], "rows": [["`Cluster.append`", "**sim**", "medido: 20.000 de 20.000 com quatro threads — o GIL protege a operação inteira"], ["`v[\"n\"] := v[\"n\"] + 1`", "**não**", "medido: 33.740 de 40.000 — ler-modificar-escrever não é atômico"], ["`remove`, `pop`, `insert`, `sort`", "**não**", "elas **leem para decidir** o que escrever"], ["`Arcane.Database`", "sim", "o módulo serializa o acesso à conexão"], ["uma conexão de banco crua", "**não**", "e ela não atravessa processo — ver a travessia"], ["`Arcane.Stm`", "sim", "é o ponto dele"], ["um `record`", "sim", "imutável"], ["uma instância de `blueprint`", "**não**", "estado mutável sem trava"]]}},
  { code: `adopt Arcane.Concurrent as C

// 'append' de quatro threads: o GIL protege a operação inteira.
lista := []
action empilhar():
    cycle i from 1 to 2000:
        lista.append(i)

parallel:
    empilhar()
    empilhar()
    empilhar()
    empilhar()

assert len(lista) is 8000
out $"append: {len(lista)} de 8000 — nenhum perdido"`, lang: 'df' },
  {"h2": "E o que o `check` avisa"},
  {"p": "O analisador **avisa** (`escrita-concorrente`) quando um `thread`, um `parallel` ou uma `route` escreve num nome que vem de fora — inclusive na forma `v[\"n\"] := …`, que é a que mais engana. A lista de métodos que disparam o aviso foi **medida**, e não presumida: `append` ficou de fora de propósito, porque avisar sobre ele seria falso alarme em código que funciona."},
  { code: `adopt Arcane.Concurrent as C

// A forma protegida passa pelo aviso igual — e está certa. O aviso é
// aviso, e não erro: recusar proibiria o uso correto com mutex.
trava := C.mutex()
contador := {"n": 0}

action somar_um():
    contador["n"] := contador["n"] + 1
    yield yes

action muitas():
    cycle i from 1 to 2000:
        C.com_trava(trava, somar_um)

parallel:
    muitas()
    muitas()
    muitas()
    muitas()

assert contador["n"] is 8000
out $"com mutex: {contador['n']} de 8000"`, lang: 'df' },
  {"h2": "A rota é o caso que mais importa"},
  {"p": "O Kiln atende **um pedido por thread**, e ali a concorrência é **invisível**: quem escreve a rota não vê thread nenhuma. Medido neste repositório: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram **1 de 6**."},
  { code: `adopt Arcane.Concurrent as C
adopt Arcane.Kiln as Kiln

// O estado de uma rota, protegido — porque duas rotas rodam juntas.
trava := C.mutex()
visitas := {"n": 0}

action contar():
    visitas["n"] := visitas["n"] + 1
    yield visitas["n"]

action rota_home(req):
    yield Kiln.json({"visitas": C.com_trava(trava, contar)})

app := Kiln.app()
Kiln.get(app, "/", rota_home)

primeira := Kiln.test(app, "GET", "/")
assert primeira["status"] is 200
out "o estado da rota mora fora dela, e a trava é de quem escreve"`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "A análise para na fronteira da ação", "texto": "Seguir a chamada exigiria um grafo, e um aviso que depende disso seria impreciso nos dois sentidos. Por isso ele olha o corpo do `thread`/`parallel`/`route` e para ali — e por isso é aviso."}},
];

const headings = [{ id: 'e-o-que-o-check-avisa', text: "E o que o `check` avisa", level: 2 as const }, { id: 'a-rota-e-o-caso-que-mais-importa', text: "A rota é o caso que mais importa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O que dá para compartilhar"}
      description={"Quais peças da biblioteca aguentam duas threads — e quais não, com o número medido."}
      href={"/docs/concorrencia/biblioteca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
