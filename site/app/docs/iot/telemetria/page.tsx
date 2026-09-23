// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Telemetria: guardar o que o sensor leu",
  description: "Do pino ao banco, ao quadro e ao gráfico — e a decisão de quanto guardar.",
};

const blocos: Bloco[] = [
  {"p": "Um sensor que não guarda nada responde \"quanto é agora?\". Guardar transforma isso em \"o que aconteceu de madrugada?\", que costuma ser a pergunta que importa."},
  {"h2": "Do pino para o banco"},
  { code: `adopt Arcane.IoT as IoT
adopt Arcane.Database as DB
adopt Arcane.OS as OS
adopt Arcane.IO as IO

pasta := $"{OS.temp_dir()}/df-doc-tel-{randint(100000, 999999)}"
IO.mkdir(pasta)
db := DB.connect($"{pasta}/estufa.db")
DB.execute(db, "CREATE TABLE leituras (quando TEXT, canal INTEGER, valor INTEGER)")

placa := IoT.conectar_simulada("uno")
placa.modo(14, "analogico")
placa.relatar_analogico(0)

cycle i from 1 to 5:
    placa.simulador.definir_analogico(0, 400 + i * 30)
    sleep(60)
    DB.insert(db, "leituras", {"quando": $"t{i}", "canal": 0,
                               "valor": placa.analogico(0)})

linhas := DB.query(db, "SELECT * FROM leituras ORDER BY quando")
assert len(linhas) is 5
placa.fechar()
DB.close(db)
IO.remove_tree(pasta)`, lang: 'df' },
  {"h2": "O quadro, e a pergunta"},
  { code: `adopt Arcane.Quadro as Q

leituras := Q.de_vaults([
    {"hora": 0, "canal": 0, "valor": 430},
    {"hora": 1, "canal": 0, "valor": 460},
    {"hora": 2, "canal": 0, "valor": 512},
    {"hora": 0, "canal": 1, "valor": 210},
    {"hora": 1, "canal": 1, "valor": 205},
])

por_canal := leituras >> agrupar "canal" >> resumir {"valor": "media"}
assert len(por_canal) is 2
out por_canal.para_vaults()`, lang: 'df' },
  {"h2": "Quanto guardar"},
  {"p": "Um sensor a cada segundo dá 86.400 linhas por dia, e 31 milhões por ano. Quase sempre o que se quer é **agregado**: a média por minuto para a semana passada, o valor cru só para as últimas horas."},
  {"table": {"head": ["Idade do dado", "Resolução que costuma bastar"], "rows": [["últimas 6 h", "cru — é onde se investiga um incidente"], ["últimos 7 dias", "1 minuto"], ["últimos 6 meses", "1 hora, com mínimo e máximo"], ["mais que isso", "1 dia, ou nada"]]}},
  {"p": "A agregação e a limpeza são trabalho de `supabase-cron`/`pg_cron` ou de um laço próprio — o ponto é decidir isso no começo. Um banco de sensor que cresce sem política sempre termina cheio, e a descoberta vem quando a escrita falha."},
  {"h2": "E se o painel some"},
  {"p": "Um sensor que publica em MQTT com testamento avisa que caiu; um que grava direto no banco, não. Para saber que o dado **parou de chegar**, a pergunta é sobre a última linha:"},
  { code: `adopt Arcane.IoT as IoT

ultima := 0
agora := 120

action saudavel(ultima_leitura, momento, prazo):
    yield momento - ultima_leitura smaller prazo

assert saudavel(115, agora, 30) is yes
assert saudavel(40, agora, 30) is no       // 80 s sem notícia: alerta`, lang: 'df' },
];

const headings = [{ id: 'do-pino-para-o-banco', text: "Do pino para o banco", level: 2 as const }, { id: 'o-quadro-e-a-pergunta', text: "O quadro, e a pergunta", level: 2 as const }, { id: 'quanto-guardar', text: "Quanto guardar", level: 2 as const }, { id: 'e-se-o-painel-some', text: "E se o painel some", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Telemetria: guardar o que o sensor leu"}
      description={"Do pino ao banco, ao quadro e ao gráfico — e a decisão de quanto guardar."}
      href={"/docs/iot/telemetria"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
