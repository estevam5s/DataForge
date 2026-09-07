import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Web",
  description: "Cliente HTTP, URL encoding e JSON.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Web as Web

out Web.encode_url("busca com espacos")
out Web.json_stringify({"acao": "criar"})
out Web.json_parse('{"a": 1}')`, title: `exemplo` },
  {"h2": "Funções (11)"},
  {"table": {"head": ["Assinatura"], "rows": [["`check(user_id=None)`"], ["`close()`"], ["`decode_url(text)`"], ["`encode_url(text)`"], ["`get(url, headers=None)`"], ["`json_parse(text)`"], ["`json_stringify(obj, indent=None)`"], ["`post(url, data=None, headers=None)`"], ["`request(url, method='GET', data=None, headers=None)`"], ["`serve(port=8080, host='0.0.0.0')`"], ["`socket(host, port)`"]]}},
];

const headings = [{ id: 'funcoes-11', text: "Funções (11)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Web"}
      description={"Cliente HTTP, URL encoding e JSON."}
      href={"/docs/biblioteca/web"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
