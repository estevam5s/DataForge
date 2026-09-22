// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Detector em log",
  description: "Ler um log de acesso, correlacionar por IP e alertar força bruta com os eventos que a causaram.",
};

const blocos: Bloco[] = [
  {"p": "Gravar log é quase inútil sozinho: ninguém lê dez milhões de linhas. O que transforma log em segurança é a **regra** — cinco falhas do mesmo IP em um minuto — e o alerta que traz os eventos, para que quem investiga não precise voltar ao log para descobrir o que aconteceu."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`D.motor`", "as regras e a correlação"], ["`por := \"ip\"`", "cinco falhas de cinco IPs **não** são força bruta"], ["janela deslizante", "4 falhas às 23h59 e 4 às 00h01 contam juntas"], ["o alerta com os eventos", "investigável sem voltar ao log"]]}},
  {"h2": "Estrutura"},
  { code: `vigia-log/
  src/
    ler.df         linha de log -> evento
    regras.df      o catalogo
    main.df        segue o arquivo e alerta
  tests/`, lang: 'text' },
  { code: `[project]
name = "vigia-log"
version = "0.1.0"
description = "Detector de força bruta"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `adopt Arcane.Deteccao as D

LOG := """203.0.113.7 POST /login 401
198.51.100.2 POST /login 200
203.0.113.7 POST /login 401
203.0.113.7 POST /login 401
192.0.2.10 POST /login 401
203.0.113.7 POST /login 401
203.0.113.7 POST /login 401"""

action evento_de(linha):
    ip, metodo, caminho, status := linha.split(" ")
    given caminho is "/login" and status is "401":
        yield {"nome": "login.falhou", "ip": ip}
    yield void

m := D.motor()
m.regra("forca-bruta", quando := "login.falhou", vezes := 5,
    janela := 60.0, gravidade := "alto", attack := "T1110", por := "ip")

alertas := []
cycle linha in LOG.lines():
    e := evento_de(linha)
    given e is not void:
        alertas := [...alertas, ...m.evento(e["nome"], {"ip": e["ip"]})]

cycle a in alertas:
    out $"{a['gravidade']}: {a['regra']} ({a['attack']}) com {len(a['eventos'])} eventos"

assert len(alertas) is 1
assert len(alertas[0]["eventos"]) is 5`, lang: 'df', title: `src/main.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/main as L

crucible "leitura":
    trial "login bem-sucedido nao e evento":
        expect L.evento_de("1.2.3.4 POST /login 200") is void`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["correlação **por IP**", "cinco usuários errando a senha viram um ataque"], ["a regra fala de **evento**, não de linha", "trocar o formato do log reescreve as regras"], ["o alerta carrega os eventos", "quem investiga volta ao log de 10 GB"], ["o código ATT&CK (`T1110`)", "o alerta não se liga ao catálogo que o time de segurança usa"]]}},
  {"h2": "Para ir além"},
  {"list": ["Indicadores de comprometimento com prazo: [Detecção](/docs/seguranca/deteccao).", "Supressão, para mil alertas por minuto não virarem ruído: [Arcane.Deteccao](/docs/biblioteca/deteccao).", "Ler o log enquanto ele cresce: [Streams](/docs/tecnicas/streams)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Detector em log"}
      description={"Ler um log de acesso, correlacionar por IP e alertar força bruta com os eventos que a causaram."}
      href={"/docs/projetos/detector-de-intrusao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
