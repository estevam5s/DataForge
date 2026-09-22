// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Escopos e paginação",
  description: "O filtro com nome, reaproveitável e encadeável — e a página que traz o total que a tela precisa.",
};

const blocos: Bloco[] = [
  {"p": "Duas peças pequenas que decidem se uma listagem de verdade é escrita uma vez ou dez."},
  {"h2": "Escopo: o filtro com nome"},
  {"p": "`ativos`, `do_mes`, `sem_pagamento` — o filtro que aparece em dez lugares e, escrito dez vezes, **diverge em um deles**. Quando a regra muda (*“ativo agora exclui suspenso”*), há um lugar só para mudar; e o nome documenta a intenção, que um `onde` solto não faz."},
  { code: `adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()

Pedido := Forge.modelo("Pedido", {
    "id": "Serial", "cliente_id": "Inteiro",
    "status": "Texto", "total": "Decimal"
})
Forge.ligar(Pedido, db)
Pedido.migrar()

Pedido.escopo("abertos", lambda q => q.onde("status", "aberto"))
Pedido.escopo("grandes", lambda q => q.onde("total", ">", 100.0))

Pedido.criar({"cliente_id": 1, "status": "aberto", "total": 250.0})
Pedido.criar({"cliente_id": 1, "status": "aberto", "total": 30.0})
Pedido.criar({"cliente_id": 2, "status": "pago", "total": 900.0})

out $"abertos:  {len(Pedido.usar('abertos').buscar())}"
out $"grandes:  {len(Pedido.usar('grandes').buscar())}"

// Encadear e o que separa um escopo de um atalho.
ambos := Pedido.usar("grandes", Pedido.usar("abertos")).buscar()
out $"abertos E grandes: {len(ambos)}"
assert len(ambos) is 1

Forge.fechar(db)`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Um escopo desconhecido diz quais existem", "texto": "`Pedido.usar(\"abertoss\")` não devolve lista vazia — ele levanta, e a mensagem lista os escopos que o modelo tem. Devolver vazio silenciosamente é como um erro de digitação vira um relatório com zero linhas, e ninguém desconfia do relatório."}},
  {"h2": "Paginação"},
  {"p": "Uma listagem sem teto é a forma mais comum de uma aplicação travar. E uma paginação sem **total** não desenha: a tela não sabe quantos botões pôr, e a saída comum é buscar tudo para contar — exatamente o que a paginação existe para evitar."},
  { code: `adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()
Post := Forge.modelo("Post", {"id": "Serial", "titulo": "Texto"})
Forge.ligar(Post, db)
Post.migrar()

cycle i from 1 to 25:
    Post.criar({"titulo": $"Post {i}"})

p := Post.paginar(pagina := 2, tamanho := 10)

out $"pagina {p['pagina']} de {p['paginas']}"
out $"{len(p['linhas'])} linhas, de {p['total']} no total"
out $"anterior: {p['tem_anterior']}  proxima: {p['tem_proxima']}"

assert p["total"] is 25
assert p["paginas"] is 3

// Pagina fora da faixa e VAZIA, e nao erro: '?pagina=999' e um
// favorito de seis meses atras, e nao um ataque.
fora := Post.paginar(pagina := 999)
assert len(fora["linhas"]) is 0
assert fora["total"] is 25

Forge.fechar(db)`, lang: 'df' },
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["devolve `total` e `paginas`", "a tela busca tudo para contar"], ["página fora da faixa é **vazia**", "um link antigo quebra a listagem"], ["`tamanho` tem teto de 500", "`?tamanho=999999` derruba a página"], ["aceita uma consulta pronta", "paginar um escopo exigiria repetir o filtro"]]}},
  { code: `adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()
Post := Forge.modelo("Post", {"id": "Serial", "titulo": "Texto", "status": "Texto"})
Forge.ligar(Post, db)
Post.migrar()
Post.escopo("publicados", lambda q => q.onde("status", "publicado"))

cycle i from 1 to 12:
    Post.criar({"titulo": $"P{i}",
        "status": "publicado" given i % 2 is 0 otherwise "rascunho"})

// Paginar SOBRE um escopo: o total ja e o do escopo.
p := Post.paginar(pagina := 1, tamanho := 4,
    consulta := Post.usar("publicados"))

out $"publicados: {p['total']} em {p['paginas']} pagina(s)"
assert p["total"] is 6

Forge.fechar(db)`, lang: 'df' },
  {"p": "Continue em [Relações](/docs/orm/relacoes) e [Carga antecipada](/docs/orm/atraves)."},
];

const headings = [{ id: 'escopo-o-filtro-com-nome', text: "Escopo: o filtro com nome", level: 2 as const }, { id: 'paginacao', text: "Paginação", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Escopos e paginação"}
      description={"O filtro com nome, reaproveitável e encadeável — e a página que traz o total que a tela precisa."}
      href={"/docs/orm/escopos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
