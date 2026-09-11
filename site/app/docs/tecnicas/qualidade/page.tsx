// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Qualidade de dados",
  description: "As seis dimensões, medidas e cobradas como parte do pipeline — não como um assert no fim.",
};

const blocos: Bloco[] = [
  {"p": "Qualidade não é uma etapa no fim: é parte do pipeline. `Arcane.Qualidade` cobre as seis dimensões clássicas — **completude, validade, unicidade, consistência, precisão e atualidade**."},
  {"h2": "Por que isto não é um `assert`"},
  { code: `assert todas(linhas, lambda l: l["id"] is not void)`, lang: 'df' },
  {"p": "Isso responde *passou?* e nada mais. Quando falha — e vai falhar, com dado de verdade — não diz **qual** linha, **quantas**, nem se é um caso isolado ou metade do arquivo. E é essa diferença que decide se o pipeline para ou segue."},
  { code: `✗ 40000 linha(s), 3 violação(ões), 99.9% boas

  email  —  3 (0.0%)
      linha 1204: 'ana@' — fora do formato email
      linha 8891: 'sem-arroba' — fora do formato email
      linha 30112: '@dominio.co' — fora do formato email`, lang: 'text' },
  {"p": "*3 de 40.000 com e-mail inválido* leva a uma decisão. *falhou* leva a abrir o arquivo no editor."},
  {"h2": "Regras"},
  { code: `REGRAS := {
    "id":       {"obrigatorio": yes, "tipo": "inteiro", "unico": yes},
    "produto":  {"obrigatorio": yes, "tipo": "texto", "minimo": 2, "maximo": 80},
    "valor":    {"tipo": "numero", "minimo": 0},
    "email":    {"formato": "email"},
    "situacao": {"em": ["ativo", "inativo"]},
    "score":    {"confere": lambda v: v % 2 is 0},
}

r := Q.conferir(linhas, REGRAS)`, lang: 'df' },
  {"table": {"head": ["Regra", "Cobra"], "rows": [["`obrigatorio`", "veio preenchido — `void`, `\"\"` e `\"   \"` contam como vazio"], ["`tipo`", "`inteiro`, `numero`, `texto`, `booleano`, `lista`, `vault`"], ["`formato`", "`email`, `url`, `uuid`, `data`, `data_hora`, `cpf`, `cnpj`, `cep`, `telefone` — ou o seu regex"], ["`minimo` / `maximo`", "o valor, se for número; o tamanho, se for texto ou lista"], ["`em`", "está na lista permitida"], ["`unico`", "a chave não se repete"], ["`confere`", "a sua própria regra, como ação"]]}},
  {"callout": {"tipo": "nota", "titulo": "`\"   \"` conta como vazio", "texto": "Um campo com três espaços passou por *não é void* e mesmo assim não tem dado. Tratar os dois como o mesmo caso é o que evita descobrir isso três etapas adiante."}},
  {"h2": "Dentro do pipeline"},
  { code: `action conferir(ctx):
    // levanta se a taxa boa ficar abaixo de 99%
    yield Q.esperar(ctx["limpar"], REGRAS, 0.99)`, lang: 'df' },
  {"p": "O mínimo existe porque nem todo dado precisa ser perfeito. Um arquivo com 0,1% de e-mails inválidos costuma poder seguir, e parar por isso seria pior que o problema. Quando ele levanta, a mensagem traz a taxa, quantas linhas e os cinco campos que mais falharam."},
  {"h2": "Perfil — quando o arquivo é desconhecido"},
  {"p": "Mede sem regra nenhuma. É por onde se começa, e é a partir daí que se escreve a regra:"},
  { code: `p := Q.perfil(linhas)

// por campo:
//   preenchidos, vazios, completude
//   distintos, tipos, tipo_misto
//   minimo, maximo, media, mediana   (quando numérico)
//   menor_texto, maior_texto          (quando texto)
//   parece_chave                      (quando todos distintos)`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`tipo_misto` quase sempre é defeito de origem", "texto": "Dois tipos no mesmo campo vêm de CSV lido sem esquema, ou de JSON de fonte instável. É o achado mais útil do perfil, e o que mais causa erro três etapas adiante."}},
  {"h2": "Limpar"},
  { code: `Q.sem_duplicadas(linhas, ["id"])     // mantém a PRIMEIRA de cada chave
Q.so_validas(linhas, REGRAS)         // só o que passa em tudo
Q.preencher(linhas, {"situacao": "ativo"})   // só o que está vazio`, lang: 'df' },
  {"p": "`sem_duplicadas` mantém a primeira, e não a última: em dado de origem a ordem costuma ser a de chegada, e a primeira é a original. É a mesma regra que faz `conferir` marcar o repetido na **segunda** ocorrência."},
  {"h2": "As dimensões, isoladas"},
  { code: `Q.completude(linhas)                   // proporção preenchida por campo
Q.unicidade(linhas, "id")              // 1.0 = é chave
Q.duplicadas(linhas, ["id"])           // as repetidas, agrupadas
Q.fora_da_faixa(linhas, "valor", 0, 1000)
Q.atualidade(linhas, "atualizado_em", 7)   // quantas passaram de 7 dias`, lang: 'df' },
  {"p": "**Atualidade** é a dimensão que mais escapa da validação. Dado antigo não é dado errado — é dado que passou a mentir sem avisar."},
];

const headings = [{ id: 'por-que-isto-nao-e-um-assert', text: "Por que isto não é um `assert`", level: 2 as const }, { id: 'regras', text: "Regras", level: 2 as const }, { id: 'dentro-do-pipeline', text: "Dentro do pipeline", level: 2 as const }, { id: 'perfil-quando-o-arquivo-e-desconhecido', text: "Perfil — quando o arquivo é desconhecido", level: 2 as const }, { id: 'limpar', text: "Limpar", level: 2 as const }, { id: 'as-dimensoes-isoladas', text: "As dimensões, isoladas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Qualidade de dados"}
      description={"As seis dimensões, medidas e cobradas como parte do pipeline — não como um assert no fim."}
      href={"/docs/tecnicas/qualidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
