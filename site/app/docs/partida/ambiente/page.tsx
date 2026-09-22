// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ambiente e configuração",
  description: "Variáveis de ambiente com padrão, a configuração que falha na partida — e o segredo que nunca vai para o arquivo.",
};

const blocos: Bloco[] = [
  {"p": "A mesma imagem roda em desenvolvimento, homologação e produção; o que muda é o **ambiente**. Ler a configuração de variáveis — e não de um arquivo dentro da imagem — é o que deixa o mesmo artefato ir para os três lugares."},
  { code: `adopt Arcane.OS as OS

porta := int(OS.get_env("PORTA", "8080"))
modo := OS.get_env("MODO", "desenvolvimento")
assert porta bigger 0
assert OS.get_env("VARIAVEL_QUE_NAO_EXISTE_AQUI") is void
assert not OS.has_env("VARIAVEL_QUE_NAO_EXISTE_AQUI")`, lang: 'df' },
  {"h2": "Falhe na partida, não no primeiro pedido"},
  {"p": "Uma variável obrigatória que falta deveria impedir o programa de **subir** — com uma mensagem que diz qual —, e não estourar no primeiro pedido que precisa dela, às três da manhã:"},
  { code: `adopt Arcane.OS as OS

action exigir(nomes):
    faltam := [n cycle n in nomes given not OS.has_env(n)]
    given len(faltam) bigger 0:
        trigger $"faltam variáveis de ambiente: {faltam.join(", ")}"

OS.set_env("BANCO_URL", "sqlite:///tmp/app.db")
exigir(["BANCO_URL"])                       // passa

recusado := no
monitor:
    exigir(["BANCO_URL", "CHAVE_DA_API"])
handle Error as e:
    recusado := e.message.contains("CHAVE_DA_API")
assert recusado
OS.unset_env("BANCO_URL")`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "Segredo não é configuração", "texto": "Porta e modo podem estar num `.env` versionado de exemplo. Senha, token e chave **não**: eles vêm do ambiente de verdade, do gerenciador de segredos da plataforma, e nunca de um arquivo no repositório. `dataforge seguranca` procura segredo em arquivo de configuração — que é por onde eles mais vazam."}},
];

const headings = [{ id: 'falhe-na-partida-nao-no-primeiro-pedido', text: "Falhe na partida, não no primeiro pedido", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ambiente e configuração"}
      description={"Variáveis de ambiente com padrão, a configuração que falha na partida — e o segredo que nunca vai para o arquivo."}
      href={"/docs/partida/ambiente"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
