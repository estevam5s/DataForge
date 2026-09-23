// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_engenharia.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Observar um pipeline",
  description: "O que medir para saber que ele está certo — e não só que ele terminou.",
};

const blocos: Bloco[] = [
  {"p": "Um pipeline que termina com código zero **não** está necessariamente certo. As quatro perguntas que um painel de pipeline precisa responder são outras:"},
  {"table": {"head": ["Pergunta", "Métrica", "Alerta quando"], "rows": [["rodou?", "última execução bem-sucedida", "passou do intervalo esperado"], ["trouxe dado?", "linhas por execução", "cai fora da faixa histórica"], ["o dado presta?", "taxa de linhas válidas", "abaixo do mínimo do contrato"], ["está fresco?", "idade do dado mais novo", "mais velho que o acordado"]]}},
  { code: `adopt Arcane.Pipeline as Pipe
adopt Arcane.OS as OS
adopt Arcane.IO as IO

pasta := $"{OS.temp_dir()}/df-obs-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)

fluxo := Pipe.fluxo("diario", $"{pasta}/estado.json")
Pipe.etapa(fluxo, "extrair", lambda ctx => [1, 2, 3])
Pipe.etapa(fluxo, "transformar", lambda ctx => 3, ["extrair"])

r := Pipe.rodar(fluxo)
out $"ok: {r['ok']}   etapas: {sorted(keys(r['resultados']))}"
assert r["ok"] is yes

// O histórico é o que responde "quando foi a última vez que deu certo".
h := Pipe.historico(fluxo, 5)
assert len(h) >= 1
out $"execuções registradas: {len(h)}"`, lang: 'df' },
  {"h2": "A falha de uma etapa não pode virar sucesso do fluxo"},
  { code: `adopt Arcane.Pipeline as Pipe

fluxo := Pipe.fluxo("t")
Pipe.etapa(fluxo, "boa", lambda ctx => 1)
Pipe.etapa(fluxo, "ruim", lambda ctx => 1 / 0, ["boa"])
Pipe.etapa(fluxo, "depois", lambda ctx => 2, ["ruim"])

r := Pipe.rodar(fluxo)
assert r["ok"] is no
out $"ok: {r['ok']}"
// E o que dependia da etapa quebrada NÃO rodou: rodar com a entrada
// pela metade é o que produz o relatório errado.
out $"etapas que rodaram: {sorted(keys(r['resultados']))}"`, lang: 'df' },
  {"h2": "Etapa opcional é uma decisão, e ela é declarada"},
  { code: `adopt Arcane.Pipeline as Pipe

fluxo := Pipe.fluxo("t")
Pipe.etapa(fluxo, "principal", lambda ctx => 1)
// 'opcional' diz que a falha dela não derruba o fluxo — é para o
// que é enriquecimento, e nunca para o que é o dado.
Pipe.etapa(fluxo, "enriquecer", lambda ctx => 1 / 0, ["principal"],
           1, 0, void, yes)

r := Pipe.rodar(fluxo)
assert r["ok"] is yes
out "o enriquecimento falhou, e o fluxo seguiu — porque alguém declarou isso"`, lang: 'df' },
  {"h2": "Tentar de novo, com espera"},
  { code: `adopt Arcane.Pipeline as Pipe

tentativas := {"n": 0}

action instavel(ctx):
    tentativas["n"] := tentativas["n"] + 1
    given tentativas["n"] < 3:
        trigger "a rede caiu"
    yield "pronto"

fluxo := Pipe.fluxo("t")
Pipe.etapa(fluxo, "buscar", instavel, void, 3, 0)

r := Pipe.rodar(fluxo)
assert r["ok"] is yes
assert tentativas["n"] is 3
out $"precisou de {tentativas['n']} tentativas"`, lang: 'df' },
  {"p": "Repetir só serve para falha **passageira**. Repetir uma credencial errada por quarenta segundos troca um erro claro por um travamento — é a mesma regra do `Forge.esperar`, e ela vale aqui: o que não vai melhorar com o tempo não entra na retentativa."},
];

const headings = [{ id: 'a-falha-de-uma-etapa-nao-pode-virar-sucesso-do-fluxo', text: "A falha de uma etapa não pode virar sucesso do fluxo", level: 2 as const }, { id: 'etapa-opcional-e-uma-decisao-e-ela-e-declarada', text: "Etapa opcional é uma decisão, e ela é declarada", level: 2 as const }, { id: 'tentar-de-novo-com-espera', text: "Tentar de novo, com espera", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Observar um pipeline"}
      description={"O que medir para saber que ele está certo — e não só que ele terminou."}
      href={"/docs/dados/observar-pipeline"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
