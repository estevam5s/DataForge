// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lago.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Data Lake",
  description: "Partições Hive, camadas bronze/prata/ouro e compactação — em disco, sem servidor.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Lago as L

lago := L.lago("dados/")

L.gravar(lago, "vendas", linhas, ["ano", "mes"])
L.ler(lago, "vendas", {"ano": 2026})`, lang: 'df' },
  {"h2": "O caminho carrega o filtro"},
  { code: `dados/vendas/ano=2026/mes=03/parte-20260910-084726-0000.parquet`, lang: 'text' },
  {"p": "Uma consulta por `ano=2026` não abre um arquivo sequer de 2025 — ela nem os lista. Com dois anos de dados isso é conveniência; com dez, é a diferença entre segundos e minutos."},
  {"callout": {"tipo": "dica", "titulo": "É o layout do Hive", "texto": "`chave=valor` na pasta não é invenção nossa: é o que Spark, DuckDB e pandas já sabem ler. Um lago escrito aqui é lido por eles sem conversão — `pd.read_parquet(\"dados/vendas\")` traz as partições como colunas."}},
  {"p": "O campo de partição **sai** das linhas antes de gravar: ele já está no caminho, e guardá-lo duas vezes é desperdício. Na leitura ele volta, vindo da pasta."},
  {"h2": "Gravar sempre acrescenta"},
  {"p": "Cada gravação cria um arquivo com instante e contador no nome. Sobrescrever exigiria saber que a gravação anterior terminou, e num lago ninguém garante isso — quem quer trocar um período remove a partição antes:"},
  { code: `L.remover_particao(lago, "vendas", {"ano": 2026, "mes": 3})
L.gravar(lago, "vendas", linhas_de_marco, ["ano", "mes"])`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Sem filtro, ele recusa", "texto": "`remover_particao` sem filtro apagaria a tabela inteira. Ele levanta em vez de fazer — apagar dado por engano não tem desfazer."}},
  {"h2": "Compactar"},
  {"p": "Um lago que recebe carga de hora em hora acumula 24 arquivos por dia por partição. Ler mil arquivos de 4 KB é muito mais lento que ler um de 4 MB — **o custo está em abrir, não em ler**."},
  { code: `L.compactar(lago, "vendas")
// {"particoes_compactadas": 12, "arquivos_removidos": 276}`, lang: 'df' },
  {"p": "Ele grava o arquivo novo **inteiro** antes de apagar os antigos. Apagar primeiro e falhar no meio perderia os dados."},
  {"h2": "As três camadas"},
  {"table": {"head": ["Camada", "O que guarda"], "rows": [["**bronze**", "o dado como chegou, sem tocar"], ["**prata**", "limpo, tipado, sem duplicata"], ["**ouro**", "agregado, pronto para consumo"]]}},
  { code: `action limpar(linhas):
    yield Q.so_validas(Q.sem_duplicadas(linhas, ["id"]), REGRAS)

L.gravar(L.camada(lago, "bronze"), "vendas", bruto, ["ano"])
L.promover(lago, "vendas", "bronze", "prata", limpar, ["ano"])
L.promover(lago, "vendas", "prata", "ouro", agregar, ["ano"])`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Bronze existe para poder reprocessar", "texto": "Quando a regra de limpeza estava errada — e vai estar — sem o bruto guardado a única saída é pedir os dados de novo à origem, que nem sempre os tem. `promover` **nunca** altera a camada de origem."}},
  {"h2": "Inspecionar"},
  { code: `L.tabelas(lago)                    // as tabelas que existem
L.particoes(lago, "vendas")        // as partições de uma delas
L.arquivos(lago, "vendas", {"ano": 2026})
L.esquema(lago, "vendas")          // colunas, tipos, e quais são de partição
L.tamanho(lago)                    // bytes e arquivos, legível
L.eventos(lago)                    // o que aconteceu com o lago
L.vacuo(lago)                      // tira pasta vazia e gravação interrompida`, lang: 'df' },
  {"h2": "O que este módulo não é"},
  {"p": "Não é Delta Lake nem Iceberg. **Não há transação ACID entre escritores concorrentes**, nem viagem no tempo por versão, nem evolução de esquema automática."},
  {"p": "Dois processos gravando na mesma partição ao mesmo tempo é o caso que ele não protege. Cada gravação cria um arquivo com nome próprio, então eles não se sobrescrevem — mas nada garante que os dois apareçam juntos para quem lê no meio."},
  {"callout": {"tipo": "atencao", "titulo": "O valor da partição vem do dado", "texto": "E dado vem de fora. Um campo com `../..` escreveria fora do lago — é o mesmo Zip Slip, por outra porta. Todo valor é higienizado antes de virar pasta, e há teste conferindo que nada escapa da raiz."}},
];

const headings = [{ id: 'o-caminho-carrega-o-filtro', text: "O caminho carrega o filtro", level: 2 as const }, { id: 'gravar-sempre-acrescenta', text: "Gravar sempre acrescenta", level: 2 as const }, { id: 'compactar', text: "Compactar", level: 2 as const }, { id: 'as-tres-camadas', text: "As três camadas", level: 2 as const }, { id: 'inspecionar', text: "Inspecionar", level: 2 as const }, { id: 'o-que-este-modulo-nao-e', text: "O que este módulo não é", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Data Lake"}
      description={"Partições Hive, camadas bronze/prata/ouro e compactação — em disco, sem servidor."}
      href={"/docs/tecnicas/lago"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
