// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/vitrine.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Layout",
  description: "Colunas, abas, cartões, barra lateral e formulários — e por que a área é um objeto.",
};

const blocos: Bloco[] = [
  {"h2": "A área é um objeto"},
  {"p": "Em Python isto seria um `with`. A DataForge não tem bloco de contexto, e inventar um só para o layout significaria acrescentar uma palavra reservada à linguagem inteira para resolver um problema de um módulo."},
  {"p": "A saída é o idioma que a linguagem já tem: **a área é um objeto, e os componentes são métodos dele**."},
  { code: `colunas := V.colunas(3)
colunas[0].metrica("Vendas", "R$ 100K")
colunas[1].metrica("Clientes", "2.500")
colunas[2].metrica("Pedidos", "8.400")`, lang: 'df' },
  {"p": "Lê-se melhor, aninha sem indentação extra, e a área pode ser guardada numa variável e passada adiante — o que um `with` não permite:"},
  { code: `action cartao_de_metrica(area, rotulo, valor):
    caixa := area.cartao(rotulo)
    caixa.metrica(rotulo, valor)
    caixa.texto("atualizado agora")

colunas := V.colunas(2)
cartao_de_metrica(colunas[0], "Receita", "R$ 850K")
cartao_de_metrica(colunas[1], "Custo", "R$ 310K")`, lang: 'df' },
  {"p": "Toda área oferece os **mesmos** componentes que `V`, mais os layouts aninhados. Aprender um ensina todos."},
  {"h2": "Colunas"},
  { code: `V.colunas(3)              // três iguais
V.colunas([2, 1])         // a primeira com o dobro da largura
V.colunas(2, espacamento := "grande")`, lang: 'df' },
  {"p": "Abaixo de 860 px cada coluna ocupa a largura inteira — o layout é responsivo sem que você faça nada."},
  {"h2": "Barra lateral"},
  {"p": "`V.lateral()` devolve sempre a mesma área, chamada de onde for. É o lugar dos filtros:"},
  { code: `lado := V.lateral()
lado.cabecalho("Filtros", 4)
regiao := lado.escolha("Região", ["Sul", "Norte"])
de     := lado.data("De")
ate    := lado.data("Até")
lado.divisor()
given lado.botao("Limpar", tipo := "secundario"):
    V.estado.limpar()`, lang: 'df' },
  {"p": "Se nada for posto nela, a barra não aparece."},
  {"h2": "Abas"},
  { code: `abas := V.abas(["Resumo", "Detalhe", "Sobre"])
abas[0].metrica("Total", 128400)
abas[1].frame(linhas)
abas[2].markdown("Feito com **Arcane.Vitrine**.")`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Todas as abas são montadas", "texto": "Só a escolhida aparece, mas **todas** rodam. É uma decisão consciente: montar apenas a visível deixaria o programa com um caminho diferente por aba, e um erro escondido atrás de um clique é um erro que só aparece em produção."}},
  {"h2": "Cartões, seções e containers"},
  { code: `cartao := V.cartao("Vendas", subtitulo := "primeiro semestre")
cartao.metrica("Receita", "R$ 850K")

secao := V.expandir("Detalhes técnicos", aberto := no)
secao.codigo(consulta_sql, linguagem := "sql")

caixa := V.container(borda := yes, altura := 320)
cycle item in muitos:
    caixa.texto(item)

barra := V.linha(alinhar := "entre")
barra.texto("Resultados")
barra.botao("Exportar", tipo := "secundario")`, lang: 'df' },
  {"p": "`V.expandir` guarda o estado de aberto ou fechado entre execuções. `V.linha` põe os filhos lado a lado, e `V.espacador()` empurra o que vem depois para a outra ponta."},
  {"h2": "Espaço reservado"},
  {"p": "`V.vazio()` reserva um lugar para ser preenchido depois — serve para escrever \"Calculando…\" e substituir pelo resultado sem que a página salte:"},
  { code: `lugar := V.vazio()
lugar.carregando("Consultando…")
dados := consulta_demorada()
lugar.frame(dados)`, lang: 'df' },
];

const headings = [{ id: 'a-area-e-um-objeto', text: "A área é um objeto", level: 2 as const }, { id: 'colunas', text: "Colunas", level: 2 as const }, { id: 'barra-lateral', text: "Barra lateral", level: 2 as const }, { id: 'abas', text: "Abas", level: 2 as const }, { id: 'cartoes-secoes-e-containers', text: "Cartões, seções e containers", level: 2 as const }, { id: 'espaco-reservado', text: "Espaço reservado", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Layout"}
      description={"Colunas, abas, cartões, barra lateral e formulários — e por que a área é um objeto."}
      href={"/docs/vitrine/layout"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
