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

    # O indice sai da MESMA funcao que o 'gerar_indices.py' usa, e com
    # 'h3' junto. Antes eram duas implementacoes: esta pegava so 'h2' e
    # minusculava DEPOIS de remover o que nao e [a-z0-9], o que apagava
    # cada letra maiuscula — 'HMAC' virava ancora vazia. As duas se
    # sobrescreviam a cada geracao, e o estado final dependia da ORDEM
    # em que os dois geradores rodassem.
    from gerar_indices import slugify

    headings = ", ".join(
        "{ id: '%s', text: %s, level: %s as const }"
        % (slugify(b[nivel]), json.dumps(b[nivel], ensure_ascii=False),
           nivel[1])
        for b in pagina['blocos']
        for nivel in ("h2", "h3") if nivel in b)

    # Atributos JSX recebem a string via expressão {"..."}: o literal com
    # aspas escapadas (\") é válido em JS mas NÃO em atributo JSX.
    # O aviso e a primeira linha do arquivo, e nao um comentario no
    # gerador: quem abre a pagina para editar precisa ver ANTES de
    # comecar. Sem ele, uma correcao a mao some no proximo
    # 'gerar_conteudo.py' sem nada explicando — foi o que aconteceu com
    # a contagem de simbolos desta pagina.
    # A previa PROPRIA, quando a pagina merece uma.
    #
    # Sem 'openGraph' aqui, o Next herda o do layout — que e o card do
    # site inteiro, e e o certo para a maioria das paginas. Declarar um
    # vazio seria pior: no Next, o 'openGraph' do filho SUBSTITUI o do
    # pai, entao uma pagina com openGraph sem imagem ficaria sem imagem
    # nenhuma.
    # A forma vazia precisa do tipo — é a que 'gerar_indices.py' escreve, e
    # os dois geradores tem de concordar byte a byte.
    linha_de_headings = (f"const headings = [{headings}];" if headings
                         else "const headings: never[] = [];")
    og = ""
    if pagina.get('og'):
        titulo = json.dumps(pagina['title'], ensure_ascii=False)
        descricao = json.dumps(pagina.get('description', ''),
                               ensure_ascii=False)
        url = json.dumps("https://dataforge-lang.vercel.app" + href,
                         ensure_ascii=False)
        imagem = json.dumps("/" + pagina['og'], ensure_ascii=False)
        og = f"""
  openGraph: {{
    type: 'article',
    locale: 'pt_BR',
    url: {url},
    siteName: 'DataForge',
    title: {titulo},
    description: {descricao},
    images: [{{ url: {imagem}, width: 1200, height: 630,
               type: 'image/png', alt: {titulo} }}],
  }},
  twitter: {{
    card: 'summary_large_image',
    title: {titulo},
    description: {descricao},
    images: [{imagem}],
  }},
  alternates: {{ canonical: {url} }},"""

    fonte_py = pagina.get('fonte', 'site/scripts/conteudo/')
    tsx = f'''// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e '{fonte_py}' — mude la e rode o gerador.

import type {{ Metadata }} from 'next';
import type {{ Bloco }} from '@/lib/content';
import {{ DocPage }} from '@/components/Doc';
import {{ Renderer }} from '@/components/Renderer';

export const metadata: Metadata = {{
  title: {json.dumps(pagina['title'], ensure_ascii=False)},
  description: {json.dumps(pagina.get('description', ''), ensure_ascii=False)},{og}
}};

const blocos: Bloco[] = [
  {blocos},
];

{linha_de_headings}

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
