import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Serialização",
  description: "JSON, CSV, TOML, XML e a fronteira entre o programa e o mundo.",
};

const blocos: Bloco[] = [
  {"h2": "Por que importa"},
  {"p": "Todo programa que não é um exercício conversa com o mundo: lê um arquivo, chama uma API, grava um relatório. Serialização é essa fronteira."},
  { code: `adopt Arcane.Serialization as Serde` },
  {"h2": "JSON"},
  { code: `Serde.to_json(dados)                  # compacto
Serde.json_pretty(dados, 2)           # indentado
Serde.from_json(texto)                # pode disparar
Serde.from_json_safe(texto, padrao)   # nunca dispara` },
  {"h3": "A variante _safe"},
  { code: `r := Serde.from_json_safe("{isso nao e json")
# {ok: no, value: void, error: "Expecting property name..."}

r := Serde.from_json_safe(corpo)
given r.ok:
    processar(r.value)
otherwise:
    responder_erro(r.error)` },
  {"p": "Dado que veio de fora **vai** estar malformado alguma hora. A variante `_safe` transforma isso num valor que você examina, em vez de uma exceção que precisa envolver em `monitor`."},
  {"h3": "json_path — navegar sem quebrar"},
  { code: `Serde.json_path(dados, "autor.nome")
Serde.json_path(dados, "tags.0")                       # índice de lista
Serde.json_path(dados, "autor.telefone", "ausente")    # com padrão` },
  {"p": "Sem isso, chegar num campo aninhado exige verificar cada nível. `json_path` faz o mesmo em uma expressão."},
  {"h2": "CSV"},
  { code: `Serde.records_to_csv(registros)     # lista de vaults → CSV com cabeçalho
Serde.csv_to_records(csv)           # CSV → lista de vaults
Serde.to_csv(linhas, ",", cabecalho)
Serde.from_csv(texto, ",", yes)` },
  {"p": "As duas primeiras assumem que a primeira linha é cabeçalho e que cada linha vira um vault — o formato natural para dados tabulares."},
  {"h2": "TOML"},
  {"p": "Legível para humanos, ideal para configuração:"},
  { code: `config := {"servidor": {"host": "localhost", "porta": 8080}}
out Serde.to_toml(config)` },
  { code: `[servidor]
host = "localhost"
porta = 8080`, lang: 'toml', title: `saída` },
  {"h2": "Achatar e desachatar"},
  { code: `Serde.flatten({"a": {"b": 1}})      # {"a.b": 1}
Serde.unflatten({"a.b": 1})         # {"a": {"b": 1}}` },
  {"p": "`flatten` é o que transforma um JSON aninhado em colunas de CSV. `unflatten` reconstrói."},
  {"h2": "JSON Lines"},
  { code: `Serde.json_lines(registros)         # um objeto JSON por linha
Serde.from_json_lines(texto)` },
  {"p": "O formato de log e de exportação em lote: cada linha é independente, então dá para processar em [stream](/docs/tecnicas/streams) sem carregar o arquivo inteiro."},
  {"h2": "Outros formatos"},
  {"table": {"head": ["Formato", "Funções"], "rows": [["INI", "`to_ini` `from_ini`"], ["XML", "`to_xml` `from_xml`"], ["Binário", "`to_bytes` `from_bytes`"], ["Base64", "`to_base64` `from_base64`"]]}},
  {"p": "A lista completa está em [Arcane.Serialization](/docs/biblioteca/serialization)."},
];

const headings = [{ id: 'por-que-importa', text: "Por que importa", level: 2 as const }, { id: 'json', text: "JSON", level: 2 as const }, { id: 'a-variante-safe', text: "A variante _safe", level: 3 as const }, { id: 'jsonpath-navegar-sem-quebrar', text: "json_path — navegar sem quebrar", level: 3 as const }, { id: 'csv', text: "CSV", level: 2 as const }, { id: 'toml', text: "TOML", level: 2 as const }, { id: 'achatar-e-desachatar', text: "Achatar e desachatar", level: 2 as const }, { id: 'json-lines', text: "JSON Lines", level: 2 as const }, { id: 'outros-formatos', text: "Outros formatos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Serialização"}
      description={"JSON, CSV, TOML, XML e a fronteira entre o programa e o mundo."}
      href={"/docs/tecnicas/serializacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
