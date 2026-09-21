// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_ddd.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Domínio e DDD",
  description: "Valor, entidade, agregado, evento, regra, repositório e unidade de trabalho — cobrados, e não só nomeados.",
};

const blocos: Bloco[] = [
  {"p": "**`Arcane.Dominio`** traz as peças do *Domain-Driven Design*. Ele não é um framework que obriga a modelar de um jeito, e não é uma camada sobre banco: DDD é um conjunto de **distinções**, e o valor delas está em serem cobradas."},
  {"p": "Um `blueprint` chamado `Pedido` com um comentário `// agregado` em cima não impede ninguém de mexer nos itens por fora — e é justamente isso que faz a modelagem se desfazer em seis meses. O que este módulo acrescenta é a recusa."},
  { code: `adopt Arcane.Dominio as D

pedido := D.agregado("Pedido", "PED-7", total := 0)
pedido.invariante("o total nunca e negativo",
    lambda p => p.ler("total", 0) bigger_eq 0)

mark @pedido.comando("acrescentar")
action acrescentar(p, nome, preco):
    p.mudar(total := p.ler("total", 0) + preco)
    p.aconteceu("ItemAcrescentado", {"item": nome, "preco": preco})

pedido.acrescentar("cafe", 32)
out pedido.ler("total")        // 32

pedido.mudar(total := 999999)  // recusado: so muda dentro de um comando`, lang: 'df' },
  {"h2": "As sete peças"},
  {"table": {"head": ["", "O que é", "O que ela recusa"], "rows": [["`valor`", "igualdade por **conteúdo**, imutável", "criar um valor que a regra não permite"], ["`entidade`", "igualdade por **identidade**, estado muda", "confundir duas pessoas de mesmo nome"], ["`agregado`", "a única porta de escrita", "escrever por fora, e sair de um comando inválido"], ["`evento`", "um fato no passado, imutável", "reescrever o que já aconteceu"], ["`regra`", "condição de negócio combinável", "um `given` que não dá para reaproveitar"], ["`repositorio`", "guarda agregados **inteiros**", "guardar algo sem identidade"], ["`unidade`", "confirma tudo, ou nada", "publicar um fato que a transação vai desfazer"]]}},
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/dominio/valores", "title": "Valores e entidades", "desc": "A distinção que decide metade da modelagem."}, {"href": "/docs/dominio/agregados", "title": "Agregados e invariantes", "desc": "A porta única, e o comando que desfaz."}, {"href": "/docs/dominio/eventos", "title": "Eventos e unidade de trabalho", "desc": "Por que o fato espera a confirmação."}, {"href": "/docs/dominio/contextos", "title": "Regras e contextos", "desc": "A regra como objeto, e a fronteira entre modelos."}]},
];

const headings = [{ id: 'as-sete-pecas', text: "As sete peças", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Domínio e DDD"}
      description={"Valor, entidade, agregado, evento, regra, repositório e unidade de trabalho — cobrados, e não só nomeados."}
      href={"/docs/dominio"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
