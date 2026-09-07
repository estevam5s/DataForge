import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Serialization",
  description: "JSON, JSONL, CSV, INI, TOML e XML.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Serialization as Serde

dados := {"app": "DataForge", "versao": 4, "web": {"porta": 8080}}

out Serde.to_json(dados)
out Serde.json_path(dados, "web.porta")
out Serde.flatten(dados)
out Serde.to_toml(dados)`, title: `exemplo` },
  {"p": "Guia com contexto e boas práticas: [Serialization](/tecnicas/serializacao)."},
  {"h2": "Funções (26)"},
  {"table": {"head": ["Assinatura"], "rows": [["`csv_to_records(texto, delimitador=',')`"], ["`deep_copy(d)`"], ["`flatten(dados, separador='.', prefixo='')`"], ["`formats()`"], ["`from_base64(t)`"], ["`from_bytes(b)`"], ["`from_csv(texto, delimitador=',', tem_cabecalho=False)`"], ["`from_ini(texto)`"], ["`from_json(texto)`"], ["`from_json_lines(texto)`"], ["`from_json_safe(texto, padrao=None)`"], ["`from_toml(texto)`"], ["`from_xml(texto)`"], ["`is_valid_json(texto)`"], ["`json_lines(registros)`"], ["`json_path(dados, caminho, padrao=None)`"], ["`json_pretty(d, indent=2)`"], ["`records_to_csv(registros, delimitador=',')`"], ["`to_base64(d)`"], ["`to_bytes(d)`"], ["`to_csv(linhas, delimitador=',', cabecalho=None)`"], ["`to_ini(dados)`"], ["`to_json(dados, indent=None, ordenar=False)`"], ["`to_toml(dados)`"], ["`to_xml(dados, raiz='root')`"], ["`unflatten(plano, separador='.')`"]]}},
];

const headings = [{ id: 'funcoes-26', text: "Funções (26)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Serialization"}
      description={"JSON, JSONL, CSV, INI, TOML e XML."}
      href={"/biblioteca/serialization"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
