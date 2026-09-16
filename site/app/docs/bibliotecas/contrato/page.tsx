// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O contrato de uma biblioteca",
  description: "O que o relay promete, o que a assinatura promete, e o que quebra quem depende de você.",
};

const blocos: Bloco[] = [
  {"p": "O contrato de uma biblioteca é tudo o que alguém pode escrever hoje e esperar que continue funcionando amanhã. Ele é maior do que parece — e a maior parte dele nunca foi escrita em lugar nenhum."},
  {"h2": "O que entra no contrato"},
  {"table": {"head": ["Faz parte", "Não faz"], "rows": [["os nomes no `relay`", "o que não está nele"], ["quantos parâmetros cada ação recebe", "o nome dos arquivos internos"], ["o que ela devolve, e de que tipo", "a ordem das ações no arquivo"], ["o **tipo** do erro que ela levanta", "o texto exato da mensagem de erro"], ["os campos de um `record` exportado", "um campo cujo nome começa com `_`"], ["os membros de um `enum` exportado", "a implementação de qualquer método"]]}},
  {"callout": {"tipo": "nota", "titulo": "O tipo do erro está no contrato", "texto": "Quem usa escreve `handle ValidationError`. Trocar o tipo levantado por outro quebra esse `handle` — e quebra em silêncio, porque o erro simplesmente deixa de ser capturado e sobe. Mudar o **texto** da mensagem é seguro; mudar o **tipo** não é."}},
  {"h2": "Escreva o `relay` cedo"},
  {"p": "Enquanto não há `relay`, **tudo** é público — e cada coisa que alguém descobre e passa a usar vira contrato sem você saber. O `relay` é o momento em que você decide, e quanto mais cedo, menor o estrago."},
  { code: `// no fim de src/main.df
relay cpf, cnpj, email, cep, Resultado
`, lang: 'df' },
  {"p": "A partir daí o analisador ajuda: `V.interna()` passa a ser acusado **antes de rodar**, na máquina de quem usa."},
  {"h2": "Assine o que você promete"},
  {"p": "Os tipos declarados atravessam o `adopt`. Uma ação sem anotação promete menos, e o `check` de quem usa fica cego:"},
  { code: `action formatar(valor, casas):          // promete pouco
    yield round(valor, casas)

action formatar(valor: Float, casas: Integer := 2) -> Float:
    yield round(valor, casas)
`, lang: 'df' },
  {"p": "Com a segunda forma, `V.formatar(\"12\", 2)` é acusado na máquina de quem chamou, com a linha certa — e a mensagem cita **o seu arquivo** como origem da declaração."},
  {"h2": "Erros: levante o seu, não o de dentro"},
  {"p": "Se a sua biblioteca deixa vazar o erro do `Arcane.Database` que ela usa por dentro, o banco virou parte do seu contrato — e trocá-lo numa versão de correção quebraria quem tratava aquele erro."},
  { code: `action buscar(id: Integer) -> Vault:
    monitor:
        yield consultar(id)
    handle Error as e:
        // o erro do domínio, com a causa preservada
        trigger $"nao foi possivel buscar o registro {id}"
`, lang: 'df' },
  {"p": "A causa do erro original continua acessível em `.causa`, e o relatório desenha as duas camadas: quem usa vê o que a sua biblioteca prometeu **e** o que de fato aconteceu."},
  {"h2": "O que um valor devolvido promete"},
  {"p": "Devolver um `record` promete os campos dele; devolver um `Vault` promete as chaves — e um vault é mais fácil de mudar por engano. Para um retorno estável, prefira `record`:"},
  { code: `record Resultado:
    valido: Boolean
    motivo: String := ""

action cpf(texto: String) -> Resultado:
    given len(texto) smaller 11:
        yield Resultado(no, "o CPF precisa de 11 dígitos")
    yield Resultado(yes)

relay cpf, Resultado
`, lang: 'df' },
  {"p": "Acrescentar um campo **com padrão** a um record é compatível; remover ou renomear um não é. E o `record` exportado precisa ir no `relay`: sem ele, quem usa recebe o valor e não consegue nomear o tipo."},
  {"h2": "A lista de conferência antes da 1.0.0"},
  {"list": ["Todo nome público está num `relay`?", "Toda ação pública tem tipos nos parâmetros e no retorno?", "Todo erro que sai da biblioteca é **seu**, e não de uma dependência?", "O topo dos arquivos não faz nada além de declarar?", "Os testes exercitam a biblioteca pelo nome público (`adopt minha-lib`)?", "O README tem um exemplo que roda?"]},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/bibliotecas/testes", "title": "Testes de biblioteca", "desc": "testar pelo nome público"}, {"href": "/docs/bibliotecas/versao", "title": "Versão", "desc": "o que cada número promete"}]},
];

const headings = [{ id: 'o-que-entra-no-contrato', text: "O que entra no contrato", level: 2 as const }, { id: 'escreva-o-relay-cedo', text: "Escreva o `relay` cedo", level: 2 as const }, { id: 'assine-o-que-voce-promete', text: "Assine o que você promete", level: 2 as const }, { id: 'erros-levante-o-seu-nao-o-de-dentro', text: "Erros: levante o seu, não o de dentro", level: 2 as const }, { id: 'o-que-um-valor-devolvido-promete', text: "O que um valor devolvido promete", level: 2 as const }, { id: 'a-lista-de-conferencia-antes-da-100', text: "A lista de conferência antes da 1.0.0", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O contrato de uma biblioteca"}
      description={"O que o relay promete, o que a assinatura promete, e o que quebra quem depende de você."}
      href={"/docs/bibliotecas/contrato"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
