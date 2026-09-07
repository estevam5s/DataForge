import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Streams",
  description: "Processamento incremental de dados grandes com generators encadeados.",
};

const blocos: Bloco[] = [
  {"h2": "O problema"},
  {"p": "Um arquivo de log com um milhão de linhas. Você quer os erros. A forma ansiosa:"},
  { code: `linhas := IO.read("app.log").lines()        # 1 milhão de strings
registros := linhas >> morph interpretar     # mais 1 milhão de vaults
erros := registros >> sift e: e["nivel"] is "ERROR"` },
  {"p": "Três cópias completas dos dados na memória — e talvez você só queira ver o primeiro erro."},
  {"h2": "A forma incremental"},
  { code: `stream action linhas_do_log():
    cycle l in IO.read("app.log").lines():
        emit l

stream action interpretar(fonte):
    cycle linha in fonte:
        partes := linha.split(" ")
        emit {"data": partes[0], "nivel": partes[1],
              "mensagem": partes.slice(2).join(" ")}

stream action apenas(fonte, nivel):
    cycle registro in fonte:
        given registro["nivel"] is nivel:
            emit registro

erros := apenas(interpretar(linhas_do_log()), "ERROR")` },
  {"p": "Montar a cadeia **não lê nada**. Uma linha entra, atravessa os três estágios, sai — e só então a próxima começa. A memória usada é a de uma linha."},
  {"h2": "O ganho em first()"},
  { code: `primeiro := apenas(interpretar(linhas_do_log()), "ERROR").first()` },
  {"p": "Isso lê até o primeiro erro e **para**. Se ele estiver na linha 3, as outras 999.997 nunca são tocadas."},
  {"h2": "O padrão de três estágios"},
  {"table": {"head": ["Estágio", "Faz", "Não faz"], "rows": [["**Origem**", "produz os itens brutos", "não interpreta"], ["**Transformação**", "dá estrutura a cada item", "não valida"], ["**Filtro**", "descarta o que não interessa", "não decide o destino"]]}},
  {"p": "Separados assim, cada estágio é testável e reutilizável isoladamente. Quando o formato de entrada mudar de CSV para JSON, só o primeiro muda."},
  {"h2": "Erros que atravessam o pipeline"},
  {"p": "O ponto mais delicado de um ETL: **uma linha ruim não pode derrubar as outras**. A solução é fazer o erro viajar como um dado:"},
  { code: `stream action separar(fonte):
    cycle linha in fonte:
        campos := linha.split(",")
        given len(campos) is 5:
            emit campos
        otherwise:
            emit {"__erro__": $"campos de menos: '{linha.trim()}'"}` },
  {"p": "Cada estágio seguinte reconhece o marcador e o repassa intacto:"},
  { code: `match item:
    point {"__erro__": e}:
        emit item              # passa adiante sem tocar
    point [nome, email, idade, setor, salario]:
        emit {...}             # processa normalmente` },
  {"p": "No fim, o consumidor separa os dois fluxos. Ninguém perde dado e ninguém para o processamento por causa de uma linha torta. Um `monitor` em volta de tudo abortaria o pipeline inteiro na primeira falha."},
  {"h2": "Agregar sem materializar"},
  { code: `contagem := {}
cycle registro in interpretar(linhas_do_log()):
    nivel := registro["nivel"]
    contagem[nivel] := contagem.get(nivel, 0) + 1` },
  {"p": "O acumulador cresce com o número de **níveis distintos** (3), não com o número de linhas. Essa é a diferença entre um agregado e uma cópia."},
  {"h2": "Normalizar na entrada"},
  { code: `"nome": nome.trim().title(),        # "  ANA SILVA " → "Ana Silva"
"email": email.trim().lower(),      # " ana@X.COM " → "ana@x.com"` },
  {"p": "Dados de fora chegam sujos. Limpar **uma vez**, na fronteira, evita ter que lembrar disso em cada consulta depois."},
  {"h2": "Converter só depois de validar"},
  { code: `given not registro["idade"].isdigit():
    problemas.append("idade nao numerica")
...
"idade": cast registro["idade"] as Integer` },
  {"p": "A ordem importa: `cast \"abc\" as Integer` dispara erro. Verificar primeiro transforma uma exceção num registro rejeitado com mensagem clara."},
];

const headings = [{ id: 'o-problema', text: "O problema", level: 2 as const }, { id: 'a-forma-incremental', text: "A forma incremental", level: 2 as const }, { id: 'o-ganho-em-first', text: "O ganho em first()", level: 2 as const }, { id: 'o-padrao-de-tres-estagios', text: "O padrão de três estágios", level: 2 as const }, { id: 'erros-que-atravessam-o-pipeline', text: "Erros que atravessam o pipeline", level: 2 as const }, { id: 'agregar-sem-materializar', text: "Agregar sem materializar", level: 2 as const }, { id: 'normalizar-na-entrada', text: "Normalizar na entrada", level: 2 as const }, { id: 'converter-so-depois-de-validar', text: "Converter só depois de validar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Streams"}
      description={"Processamento incremental de dados grandes com generators encadeados."}
      href={"/docs/tecnicas/streams"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
