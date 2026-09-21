// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_ddd.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Agregados e invariantes",
  description: "A única porta de escrita, a invariante cobrada na saída, e o comando que desfaz.",
};

const blocos: Bloco[] = [
  {"p": "Um agregado é a única porta de escrita de um grupo de objetos. Três cobranças sustentam isso, e cada uma evita um defeito diferente."},
  {"h2": "1. O estado só muda por comando"},
  { code: `pedido := D.agregado("Pedido", "PED-7", total := 0, itens := 0)
pedido.invariante("o total nunca e negativo",
    lambda p => p.ler("total", 0) bigger_eq 0)
pedido.invariante("um pedido tem no maximo 3 itens",
    lambda p => p.ler("itens", 0) smaller_eq 3)

pedido.mudar(total := -1)
// erro: 'Pedido' so muda dentro de um comando.`, lang: 'df' },
  {"p": "Se qualquer um escreve, a invariante não vale nada — porque não há onde cobrá-la. O comando é o lugar."},
  {"h2": "2. A invariante é cobrada na SAÍDA"},
  {"p": "Cobrar na entrada deixa o objeto quebrado quando o comando falha no meio. Cobrar na saída garante que ninguém observa um estado inválido — e é isso que faz o agregado ser a única porta."},
  { code: `mark @pedido.comando("descontar")
action descontar(p, quanto):
    p.mudar(total := p.ler("total", 0) - quanto)

monitor:
    pedido.descontar(999)
handle Error as e:
    out e.message      // 'Pedido' violou: o total nunca e negativo`, lang: 'df' },
  {"h2": "3. O comando que falha no meio é desfeito por inteiro"},
  {"p": "Estado e eventos voltam ao que eram, e a versão **não** avança. Sem isso, metade da mudança fica aplicada e a próxima leitura vê um agregado que nunca deveria existir — inclusive um evento de um comando que não aconteceu, que é a pior classe de fato."},
  { code: `assert pedido.ler("total") is 50      // como antes da tentativa
assert pedido.versao() is 2           // a versao tambem voltou
assert len(pedido.eventos()) is 2     // nada novo foi anotado`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "`versao()` serve a travas otimistas", "texto": "Ela conta quantos comandos já rodaram. Gravar comparando a versão lida é como dois usuários editando o mesmo pedido deixam de sobrescrever um ao outro em silêncio."}},
  {"h2": "A invariante que estoura é um bug dela"},
  {"p": "Como na regra de um valor: um erro dentro da condição vira uma mensagem dizendo que a **invariante** quebrou, e não que o estado é inválido. As duas coisas exigem correções em lugares diferentes."},
];

const headings = [{ id: '1-o-estado-so-muda-por-comando', text: "1. O estado só muda por comando", level: 2 as const }, { id: '2-a-invariante-e-cobrada-na-saida', text: "2. A invariante é cobrada na SAÍDA", level: 2 as const }, { id: '3-o-comando-que-falha-no-meio-e-desfeito-por-inteiro', text: "3. O comando que falha no meio é desfeito por inteiro", level: 2 as const }, { id: 'a-invariante-que-estoura-e-um-bug-dela', text: "A invariante que estoura é um bug dela", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Agregados e invariantes"}
      description={"A única porta de escrita, a invariante cobrada na saída, e o comando que desfaz."}
      href={"/docs/dominio/agregados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
