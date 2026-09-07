"""Gera as páginas .tsx do site a partir de definições de conteúdo em Python."""
import json, os, re, textwrap

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = json.load(open(f"{RAIZ}/lib/dados-gerados.json", encoding="utf-8"))

def esc(s):
    """Escapa uma string Python para literal de template JS."""
    return s.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

def bloco_para_ts(b):
    k = list(b)[0]
    if k == 'code':
        partes = [f"code: `{esc(b['code'])}`"]
        if b.get('lang'): partes.append(f"lang: '{b['lang']}'")
        if b.get('title'): partes.append(f"title: `{esc(b['title'])}`")
        return "{ " + ", ".join(partes) + " }"
    return json.dumps(b, ensure_ascii=False)

def escrever(pagina):
    href = pagina['href']
    dir_ = f"{RAIZ}/app" + ("" if href == "/" else href)
    os.makedirs(dir_, exist_ok=True)
    blocos = ",\n  ".join(bloco_para_ts(b) for b in pagina['blocos'])
    heads = [b['h2'] for b in pagina['blocos'] if 'h2' in b]

    def slug(t):
        import unicodedata
        t = unicodedata.normalize('NFD', t)
        t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
        return re.sub(r'[^a-z0-9\s-]', '', t.lower()).strip().replace(' ', '-')

    headings = ", ".join(
        "{ id: '%s', text: %s, level: 2 as const }" % (slug(h), json.dumps(h, ensure_ascii=False))
        for h in heads)

    # Atributos JSX recebem a string via expressão {"..."}: o literal com
    # aspas escapadas (\") é válido em JS mas NÃO em atributo JSX.
    tsx = f'''import type {{ Metadata }} from 'next';
import type {{ Bloco }} from '@/lib/content';
import {{ DocPage }} from '@/components/Doc';
import {{ Renderer }} from '@/components/Renderer';

export const metadata: Metadata = {{
  title: {json.dumps(pagina['title'], ensure_ascii=False)},
  description: {json.dumps(pagina.get('description', ''), ensure_ascii=False)},
}};

const blocos: Bloco[] = [
  {blocos},
];

const headings = [{headings}];

export default function Pagina() {{
  return (
    <DocPage
      title={{{json.dumps(pagina['title'], ensure_ascii=False)}}}
      description={{{json.dumps(pagina.get('description', ''), ensure_ascii=False)}}}
      href={{{json.dumps(href)}}}
      headings={{headings}}
    >
      <Renderer blocos={{blocos}} />
    </DocPage>
  );
}}
'''
    open(f"{dir_}/page.tsx", "w", encoding="utf-8").write(tsx)
    return href
