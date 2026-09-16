// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_etl.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "ETL: extrair, transformar, carregar",
  description: "O formato de um pipeline que roda todo dia — idempotência, falha parcial, reprocessamento e linhagem.",
};

const blocos: Bloco[] = [
  {"p": "Um ETL é um programa que roda **de novo**, todo dia, sobre dados que mudam. Isso é tudo o que o distingue de um script de análise, e é o que cria os problemas dele: o que acontece quando roda duas vezes? E quando falha no meio?"},
  {"h2": "As três etapas, separadas de propósito"},
  { code: `adopt Arcane.IO as IO

// EXTRAIR — só lê. Nenhuma regra de negócio aqui.
action extrair(caminho):
    yield IO.read_csv(caminho, yes)

// TRANSFORMAR — só calcula. Nada de arquivo, nada de banco.
action transformar(linhas):
    limpas := [l cycle l in linhas given (l["valor"] ?? "") isnt ""]
    yield [l with {"valor": float(l["valor"])} cycle l in limpas]

// CARREGAR — só escreve.
action carregar(linhas, destino):
    IO.write_csv(destino, linhas)
    yield len(linhas)
`, lang: 'df' },
  {"p": "A separação não é estética. `transformar` **não toca em disco**, e por isso ela é a única das três que se testa sem preparar ambiente — e é onde mora toda a regra que pode estar errada."},
  {"h2": "Rodar duas vezes tem de dar o mesmo resultado"},
  {"p": "É a propriedade que mais falta num ETL: **idempotência**. Sem ela, reprocessar um dia que falhou duplica tudo o que já tinha entrado."},
  {"table": {"head": ["Forma de carregar", "Rodar duas vezes"], "rows": [["`insert`", "**duplica**"], ["`insert_or_ignore`", "ignora o repetido — seguro"], ["`upsert` por chave", "atualiza — seguro, e corrige o que mudou"], ["apagar a partição e reinserir", "seguro, e o mais simples de entender"]]}},
  { code: `adopt Arcane.Database as DB

action carregar(db, linhas, dia):
    DB.transacao(db, lambda:
        [DB.upsert(db, "vendas", l, ["id"]) cycle l in linhas])
    yield len(linhas)
`, lang: 'df' },
  {"p": "A transação é o que torna \"carregou tudo\" e \"não carregou nada\" as duas únicas saídas possíveis. Sem ela, uma falha no meio deixa metade dentro — e a segunda execução não tem como saber qual metade."},
  {"h2": "Falhar bem"},
  {"p": "Um ETL que quebra às três da manhã precisa dizer **onde** parou e **o que** já tinha feito:"},
  { code: `adopt Arcane.Logging as Log

action rodar(caminho, destino):
    Log.info($"etl: comecando {caminho}")
    monitor:
        brutas := extrair(caminho)
        Log.info($"etl: {len(brutas)} linhas lidas")

        limpas := transformar(brutas)
        Log.info($"etl: {len(limpas)} linhas apos limpeza")

        gravadas := carregar(limpas, destino)
        Log.info($"etl: {gravadas} gravadas em {destino}")
        yield gravadas
    handle Error as e:
        Log.erro($"etl falhou em {caminho}: {e.message}")
        trigger $"o ETL de {caminho} nao terminou"
`, lang: 'df' },
  {"p": "O `trigger` de fora preserva o erro original em `.causa` — o relatório mostra as duas camadas, e quem lê o log de manhã vê tanto o que o pipeline tentava fazer quanto o que o impediu."},
  {"h2": "A linha que não entra"},
  {"p": "Descartar silenciosamente uma linha ruim é a forma mais comum de um relatório ficar errado sem ninguém notar. Separe, conte e **guarde**:"},
  { code: `action separar(linhas):
    boas := []
    ruins := []
    cycle l in linhas:
        given (l["valor"] ?? "") is "":
            ruins.append(l with {"motivo": "valor vazio"})
        otherwise:
            boas.append(l)
    yield {"boas": boas, "ruins": ruins}

resultado := separar(brutas)
given len(resultado["ruins"]) > 0:
    IO.write_csv("rejeitadas.csv", resultado["ruins"])
    out $"atencao: {len(resultado['ruins'])} linha(s) rejeitadas"
`, lang: 'df' },
  {"p": "O arquivo de rejeitadas é o que transforma \"os números não batem\" numa investigação de cinco minutos."},
  {"h2": "Ordem, dependência e paralelismo"},
  {"p": "Quando um pipeline tem etapas independentes, elas não precisam esperar umas às outras. Mas o ganho depende de onde está o custo:"},
  {"table": {"head": ["O gargalo é", "Use", "Ganho"], "rows": [["**rede ou disco** (baixar, consultar API)", "`parallel:` ou `async`", "real — o GIL é solto na espera"], ["**CPU** (transformar milhões de linhas)", "`P.map_processos`", "real — medido 4,71× em 10 núcleos"], ["**o banco**", "nenhum dos dois", "agregue **no** banco em vez de trazer"]]}},
  { code: `adopt Arcane.Concurrent as P

// as três fontes são independentes: baixam juntas
parallel:
    vendas := baixar("vendas")
    clientes := baixar("clientes")
    produtos := baixar("produtos")

// a transformação é CPU: processos de verdade
limpas := P.map_processos(transformar_lote, em_lotes(vendas, 10000))
`, lang: 'df' },
  {"h2": "Agendar"},
  {"p": "O pipeline em si não deveria saber a que horas roda. Quem agenda é de fora — `cron`, um orquestrador, ou `Arcane.Concurrent.repetir_a_cada` num processo que fica de pé:"},
  { code: `dataforge run etl/diario.df --data=2026-09-16
`, lang: 'bash' },
  {"p": "Receber a data como **argumento** é o que torna o reprocessamento possível: rodar o dia 3 de novo é trocar um número, e não mexer no código."},
  {"h2": "A lista de conferência de um ETL"},
  {"list": ["Rodar duas vezes dá o mesmo resultado?", "A carga está dentro de uma transação?", "As linhas rejeitadas são contadas **e** gravadas?", "O log diz quantas linhas entraram em cada etapa?", "A data é argumento, e não `hoje()` no meio do código?", "A transformação é testável sem disco e sem banco?"]},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/dados/qualidade", "title": "Qualidade de dados", "desc": "as regras que rodam junto do pipeline"}, {"href": "/docs/tecnicas/pipeline", "title": "Pipelines e orquestração", "desc": "o módulo Arcane.Pipeline"}, {"href": "/docs/tecnicas/lago", "title": "Data Lake", "desc": "quando o volume passa do arquivo"}, {"href": "/docs/big-o/dados", "title": "Custo em dados", "desc": "N+1, índice e paginação"}]},
];

const headings = [{ id: 'as-tres-etapas-separadas-de-proposito', text: "As três etapas, separadas de propósito", level: 2 as const }, { id: 'rodar-duas-vezes-tem-de-dar-o-mesmo-resultado', text: "Rodar duas vezes tem de dar o mesmo resultado", level: 2 as const }, { id: 'falhar-bem', text: "Falhar bem", level: 2 as const }, { id: 'a-linha-que-nao-entra', text: "A linha que não entra", level: 2 as const }, { id: 'ordem-dependencia-e-paralelismo', text: "Ordem, dependência e paralelismo", level: 2 as const }, { id: 'agendar', text: "Agendar", level: 2 as const }, { id: 'a-lista-de-conferencia-de-um-etl', text: "A lista de conferência de um ETL", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"ETL: extrair, transformar, carregar"}
      description={"O formato de um pipeline que roda todo dia — idempotência, falha parcial, reprocessamento e linhagem."}
      href={"/docs/dados/etl"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
