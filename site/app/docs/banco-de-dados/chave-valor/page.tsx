// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Redis e MongoDB",
  description: "Os dois que não são SQL: o que cada um resolve, o que não resolve, e por que o driver cabe em poucas linhas.",
};

const blocos: Bloco[] = [
  {"p": "Os dois entram pela mesma porta (`Forge.conectar`) e respondem a perguntas diferentes das do SQL. Usá-los como banco principal é o erro mais caro dos dois."},
  {"h2": "Redis"},
  {"p": "Memória, com persistência opcional. O que ele faz melhor que qualquer banco: **expirar sozinho**. Cache, sessão, limite de taxa, fila simples — tudo isso é um valor com prazo."},
  { code: `adopt Arcane.Forge as Forge

// Comentado porque exige o conteiner:
//
//   r := Forge.conectar("redis://localhost:6379")
//   Forge.executar(r, "SET sessao:abc {\\"id\\": 7}")
//   Forge.executar(r, "EXPIRE sessao:abc 3600")
//   out Forge.consultar(r, "GET sessao:abc")
//
// O protocolo (RESP) e texto, e e por isso que o driver cabe em
// poucas linhas: cada comando e uma lista de strings, e cada
// resposta tem um prefixo de um caractere dizendo o que ela e.

out "veja o exemplo acima; ele precisa de um Redis no ar"`, lang: 'df' },
  {"table": {"head": ["Use Redis para", "Não use para"], "rows": [["cache com prazo", "o dado que não pode ser perdido"], ["sessão", "relação entre entidades"], ["limite de taxa compartilhado entre processos", "relatório"], ["fila simples", "fila com garantia forte — isso é um broker"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Sem prazo, o Redis vira um vazamento com nome bonito", "texto": "Uma chave sem `EXPIRE` fica para sempre, e a memória é o recurso finito dali. O padrão que funciona é: **toda** chave nasce com prazo, e a exceção é escrita e justificada. O contrário — pôr prazo depois — é o que enche a instância às três da manhã."}},
  {"h2": "MongoDB"},
  {"p": "Documentos, sem esquema declarado. O driver fala o *wire protocol* com BSON — e `bson.py` existe aqui pelo mesmo motivo dos outros: sem `pymongo`."},
  {"table": {"head": ["Use Mongo para", "Pense duas vezes"], "rows": [["documento cuja forma varia de verdade", "dado com relações — `join` não é o forte dele"], ["esquema que muda toda semana no começo", "quando a forma estabilizar, o SQL volta a ser melhor"], ["agregação sobre eventos", "transação entre coleções"]]}},
  {"callout": {"tipo": "dica", "titulo": "“Sem esquema” não quer dizer “sem forma”", "texto": "O esquema continua existindo — ele só deixou de estar no banco e passou a estar espalhado pelo código, em cada lugar que lê o documento. Quando isso incomoda, a resposta aqui é validar na fronteira: [`Objetos.de_vault`](/docs/biblioteca/objetos) com a lista de tipos, ou um [`record`](/docs/oop) com os campos declarados."}},
  {"p": "Continue em [Cada motor](/docs/banco-de-dados/motores) e [O banco em contêiner](/docs/banco-de-dados/docker)."},
];

const headings = [{ id: 'redis', text: "Redis", level: 2 as const }, { id: 'mongodb', text: "MongoDB", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Redis e MongoDB"}
      description={"Os dois que não são SQL: o que cada um resolve, o que não resolve, e por que o driver cabe em poucas linhas."}
      href={"/docs/banco-de-dados/chave-valor"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
