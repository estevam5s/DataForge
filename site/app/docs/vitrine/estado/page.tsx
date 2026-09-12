// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/vitrine.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Estado e cache",
  description: "Os três lugares onde um valor pode morar numa aplicação Vitrine, e quem enxerga cada um.",
};

const blocos: Bloco[] = [
  {"p": "O programa roda inteiro a cada interação. Sem um lugar que sobreviva, um contador voltaria a zero a cada clique. Há três, e a diferença entre eles é **quem enxerga**:"},
  {"table": {"head": ["Onde", "Quem vê", "Some quando"], "rows": [["`V.estado`", "uma sessão", "a sessão expira"], ["`V.geral`", "**todas** as sessões", "o processo termina"], ["`V.cache`", "todas, por argumento", "o TTL vence ou é invalidado"]]}},
  {"h2": "Estado da sessão"},
  { code: `V.estado.padrao("contador", 0)       // define só se ainda não existe

given V.botao("Incrementar"):
    V.estado.somar("contador")

V.texto($"Valor: {V.estado.obter("contador")}")`, lang: 'df' },
  {"p": "`V.estado.padrao` substitui as três linhas que todo app escreve no começo. `V.estado.somar` é **atômico**: duas abas clicando ao mesmo tempo não perdem uma das somas, o que o ler-somar-escrever à mão perderia."},
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`V.estado.obter(chave, padrão)`", "lê"], ["`V.estado.definir(chave, valor)`", "escreve"], ["`V.estado.padrao(chave, valor)`", "escreve só se não existe; devolve o que vale"], ["`V.estado.somar(chave, quanto)`", "incrementa, sem corrida"], ["`V.estado.existe(chave)`", "`yes`/`no`"], ["`V.estado.remover(chave)`", "apaga uma"], ["`V.estado.limpar()`", "apaga todas"], ["`V.estado.tudo()`", "o vault, sem as chaves internas"], ["`V.estado.id()`", "o identificador da sessão"]]}},
  {"h2": "Estado global"},
  {"p": "`V.geral` é compartilhado por **todas** as sessões — configuração, um contador de visitas, um modelo de ML carregado uma vez."},
  { code: `V.geral.definir("versao", "1.0.0")
V.geral.somar("visitas")`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Não guarde ali o que é de um usuário", "texto": "Dois visitantes veriam os dados um do outro, e nada daria erro. A trava protege o dicionário, não a lógica de quem lê-e-depois-escreve — para contar, `V.geral.somar`, que é atômico."}},
  {"h2": "Cache"},
  {"p": "`mark @V.cache` sobre uma ação, e ela para de recalcular. Vale **por argumento**: `vendas(\"2026-01\")` e `vendas(\"2026-02\")` ocupam entradas diferentes."},
  { code: `mark @V.cache
action vendas(mes):
    yield Banco.consultar("SELECT … WHERE mes = ?", [mes])`, lang: 'df' },
  {"p": "Com ajustes:"},
  { code: `mark @V.cache(validade := 300, teto := 32)
action cotacao(moeda):
    yield Http.get($"https://…/{moeda}").json()

mark @V.cache(pasta := ".cache/ibge")
action municipios():
    yield Http.get("https://…/municipios").json()`, lang: 'df' },
  {"table": {"head": ["Opção", "Faz"], "rows": [["`validade`", "segundos até o valor vencer (TTL)"], ["`teto`", "quantos valores guardar; ao encher, sai o menos usado (LRU)"], ["`pasta`", "também grava em disco, e sobrevive a reiniciar"]]}},
  {"p": "O teto existe porque um cache sem limite é um vazamento com outro nome: uma ação chamada com mil argumentos diferentes guardaria mil resultados e não soltaria nenhum."},
  {"h3": "Esvaziar"},
  { code: `V.cache.invalidar(vendas)     // só essa ação
V.cache.invalidar()           // tudo
V.cache.estatisticas()        // acertos, erros e taxa, por ação`, lang: 'df' },
  {"p": "E `vendas.sem_cache(mes)` chama a ação original — é o que permite testá-la sem o cache no caminho."},
  {"callout": {"tipo": "nota", "titulo": "O cache em disco só guarda o que vira JSON", "texto": "Guardar objeto arbitrário exigiria `pickle`, e ler `pickle` de um arquivo que outro processo escreveu é execução de código. Num framework web, isso é a porta aberta. Um valor que não vira JSON continua valendo em memória."}},
  {"h2": "Identidade do componente"},
  {"p": "O valor de um campo sobrevive a um clique em outro lugar da página porque cada componente tem uma **chave**. Sem `chave`, ela sai do tipo, do rótulo e da posição — estável enquanto o programa não muda."},
  { code: `// Dê uma chave quando a ordem dos componentes pode mudar:
cycle cliente in clientes:
    V.entrada("Observação", chave := $"obs-{cliente["id"]}")`, lang: 'df' },
  {"p": "Sem a chave explícita aqui, remover um cliente da lista faria as observações dos seguintes escorregarem uma posição."},
];

const headings = [{ id: 'estado-da-sessao', text: "Estado da sessão", level: 2 as const }, { id: 'estado-global', text: "Estado global", level: 2 as const }, { id: 'cache', text: "Cache", level: 2 as const }, { id: 'esvaziar', text: "Esvaziar", level: 3 as const }, { id: 'identidade-do-componente', text: "Identidade do componente", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Estado e cache"}
      description={"Os três lugares onde um valor pode morar numa aplicação Vitrine, e quem enxerga cada um."}
      href={"/docs/vitrine/estado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
