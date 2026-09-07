import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Pipeline ETL",
  description: "Extração, transformação e carga com generators encadeados — sem carregar tudo na memória.",
};

const blocos: Bloco[] = [
  {"p": "Este é o código completo do exercício `150_projeto_etl.df`, que roda e verifica a si mesmo."},
  { code: `adopt Arcane.Serialization as Serde
adopt Arcane.Collections as Col

// ── EXTRACAO: a origem dos dados brutos ──
stream action extrair():
    linhas := [
        "  ANA SILVA ,ana@Exemplo.COM , 30, vendas , 5500",
        "bruno costa,bruno@teste.org,25,ti,7200",
        "linha malformada",
        "CARLA DIAS , carla@x.com ,41, vendas ,9100",
        "diego alves,invalido,29,ti,6300",
        "elena rocha,elena@y.com,abc,rh,4800"
    ]
    cycle l in linhas:
        emit l

// ── TRANSFORMACAO: um estagio por responsabilidade ──
stream action separar(fonte):
    cycle linha in fonte:
        campos := linha.split(",")
        given len(campos) is 5:
            emit campos
        otherwise:
            emit {"__erro__": $"campos de menos: '{linha.trim()}'"}

stream action limpar(fonte):
    cycle item in fonte:
        match item:
            point {"__erro__": e}:
                emit item
            point [nome, email, idade, setor, salario]:
                emit {
                    "nome": nome.trim().title(),
                    "email": email.trim().lower(),
                    "idade": idade.trim(),
                    "setor": setor.trim().lower(),
                    "salario": salario.trim()
                }
            default:
                emit {"__erro__": "formato inesperado"}

stream action validar(fonte):
    cycle registro in fonte:
        given "__erro__" in registro:
            emit registro
        otherwise:
            problemas := []
            given "@" not in registro["email"]:
                problemas.append("email invalido")
            given not registro["idade"].isdigit():
                problemas.append("idade nao numerica")
            given len(problemas) bigger 0:
                emit {"__erro__": $"{registro["nome"]}: {problemas.join(", ")}"}
            otherwise:
                emit {
                    "nome": registro["nome"],
                    "email": registro["email"],
                    "idade": cast registro["idade"] as Integer,
                    "setor": registro["setor"],
                    "salario": cast registro["salario"] as Integer
                }

// ── CARGA: separa o que passou do que falhou ──
validos := []
rejeitados := []

observe registro in validar(limpar(separar(extrair()))):
    given "__erro__" in registro:
        rejeitados.append(registro["__erro__"])
    otherwise:
        validos.append(registro)

out "── carregados ──"
cycle v in validos:
    out $"  {v["nome"].pad_end(12)} {v["setor"].pad_end(8)} R$ {v["salario"]}"

out ""
out "── rejeitados ──"
cycle r in rejeitados:
    out $"  {r}"

// ── RELATORIO ──
out ""
out "── por setor ──"
por_setor := Col.group_by(validos, "setor")
cycle setor in por_setor.keys():
    salarios := por_setor[setor] >> morph p: p["salario"]
    out $"  {setor.pad_end(8)} n={len(salarios)}  media=R$ {round(mean(salarios), 2)}"

folha := validos >> morph v: v["salario"] >> distill acc, s: acc + s 0
out ""
out $"folha total: R$ {folha}"
out $"aproveitamento: {len(validos)}/{len(validos) + len(rejeitados)}"

assert len(validos) is 3, "tres registros validos"
assert len(rejeitados) is 3, "tres rejeitados"
assert folha is 21800, "5500 + 9100 + 7200"
assert por_setor["vendas"].length() is 2, "duas pessoas em vendas"`, title: `150_projeto_etl.df` },
  {"h2": "A arquitetura"},
  { code: `extrair()  →  separar()  →  limpar()  →  validar()  →  observe
   ↓             ↓            ↓            ↓             ↓
 origem      estrutura    normaliza     verifica     carrega`, lang: 'text' },
  {"p": "Cada estágio é um `stream action` que consome o anterior. Montar a cadeia **não lê nada** — cada linha atravessa os quatro estágios individualmente."},
  {"h2": "Erros que atravessam o pipeline"},
  {"p": "O ponto mais delicado: **uma linha ruim não pode derrubar as outras**. A solução é fazer o erro viajar como dado, com um marcador que cada estágio reconhece e repassa intacto."},
  {"p": "Um `monitor` em volta de tudo não resolveria: ele abortaria o pipeline inteiro na primeira linha torta."},
  {"h2": "Normalizar na entrada"},
  {"p": "Dados de fora chegam sujos. Limpar **uma vez**, na fronteira, evita ter que lembrar disso em cada consulta depois."},
  {"h2": "Converter só depois de validar"},
  {"p": "`cast \"abc\" as Integer` dispara erro. Verificar primeiro transforma uma exceção num registro rejeitado com mensagem clara."},
  {"p": "Mais sobre isso em [Streams](/tecnicas/streams)."},
];

const headings = [{ id: 'a-arquitetura', text: "A arquitetura", level: 2 as const }, { id: 'erros-que-atravessam-o-pipeline', text: "Erros que atravessam o pipeline", level: 2 as const }, { id: 'normalizar-na-entrada', text: "Normalizar na entrada", level: 2 as const }, { id: 'converter-so-depois-de-validar', text: "Converter só depois de validar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Pipeline ETL"}
      description={"Extração, transformação e carga com generators encadeados — sem carregar tudo na memória."}
      href={"/receitas/etl"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
