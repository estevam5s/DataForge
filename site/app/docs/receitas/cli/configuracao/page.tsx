// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/receitas_cli.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Configuração em camadas",
  description: "Padrão, arquivo, ambiente e flag — nessa ordem, e com quem venceu dito na tela.",
};

const blocos: Bloco[] = [
  {"p": "Toda ferramenta séria lê configuração de quatro lugares, e a **ordem** é o contrato: o padrão do programa, o arquivo do projeto, a variável de ambiente e a flag da linha de comando. A da direita vence."},
  {"table": {"head": ["Camada", "Para quê", "Exemplo"], "rows": [["padrão", "funcionar sem configurar nada", "`{\"formato\": \"tabela\"}`"], ["arquivo", "a decisão do projeto, versionada", "`forge.toml`, `.minharc`"], ["ambiente", "a decisão da máquina ou do CI", "`MINHA_FORMATO=json`"], ["flag", "a decisão desta execução", "`--formato=json`"]]}},
  { code: `adopt Arcane.OS as OS

PADRAO := {"formato": "tabela", "limite": 10, "cor": yes}

action em_camadas(arquivo, prefixo, flags):
    valor := {...PADRAO}
    cycle chave in keys(arquivo):
        valor[chave] := arquivo[chave]
    cycle chave in keys(valor):
        do_ambiente := OS.get_env($"{prefixo}_{upper(chave)}")
        given do_ambiente is not void:
            valor[chave] := do_ambiente
    cycle chave in keys(flags):
        given flags[chave] is not void:
            valor[chave] := flags[chave]
    yield valor

final := em_camadas({"limite": 50}, "MINHA", {"formato": "json"})
assert final["formato"] is "json"      // a flag venceu
assert final["limite"] is 50           // o arquivo venceu o padrão
assert final["cor"] is yes             // ninguém mexeu: o padrão`, lang: 'df' },
  {"h2": "Dizer de onde veio cada valor"},
  {"p": "A pergunta que aparece em todo suporte é \"por que ele está usando isso?\". Guardar a camada ao lado do valor transforma meia hora de investigação numa linha:"},
  { code: `PADRAO := {"formato": "tabela", "limite": 10}

action com_origem(arquivo, ambiente, flags):
    saida := {}
    cycle chave in keys(PADRAO):
        saida[chave] := {"valor": PADRAO[chave], "de": "padrão"}
    cycle chave in keys(arquivo):
        saida[chave] := {"valor": arquivo[chave], "de": "arquivo"}
    cycle chave in keys(ambiente):
        saida[chave] := {"valor": ambiente[chave], "de": "ambiente"}
    cycle chave in keys(flags):
        saida[chave] := {"valor": flags[chave], "de": "flag"}
    yield saida

visto := com_origem({"limite": 50}, {}, {"formato": "json"})
cycle chave in sorted(keys(visto)):
    out $"  {chave} = {visto[chave]['valor']}   ({visto[chave]['de']})"
assert visto["limite"]["de"] is "arquivo"`, lang: 'df' },
  {"h2": "O cofre, quando há muitas camadas"},
  {"p": "`packages/cofre` é um pacote deste repositório que faz exatamente isto, e serve de referência — ele está publicado no registro e tem testes."},
  { code: `$ dataforge add cofre
$ dataforge search config`, lang: 'bash' },
  {"callout": {"tipo": "atencao", "titulo": "Segredo não é configuração", "texto": "Senha, token e chave não entram no arquivo versionado — eles vêm do ambiente ou de um cofre. `Arcane.Seguranca.varrer_segredo` acha o que escapou, e `dataforge seguranca` roda isso sobre o projeto inteiro, não só sobre os `.df`: um segredo vaza do arquivo de configuração muito mais do que do código."}},
];

const headings = [{ id: 'dizer-de-onde-veio-cada-valor', text: "Dizer de onde veio cada valor", level: 2 as const }, { id: 'o-cofre-quando-ha-muitas-camadas', text: "O cofre, quando há muitas camadas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Configuração em camadas"}
      description={"Padrão, arquivo, ambiente e flag — nessa ordem, e com quem venceu dito na tela."}
      href={"/docs/receitas/cli/configuracao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
