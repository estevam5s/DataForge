// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fundamentos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Texto a fundo",
  description: "Fatiar, procurar, trocar, dividir, juntar e formatar — e o texto de várias linhas.",
};

const blocos: Bloco[] = [
  {"p": "Texto é a coleção mais usada de todas: nomes, arquivos, mensagens, CSV. Ele é **imutável** — todo método devolve um texto novo, e o original não muda."},
  { code: `nome := "  Maria da Silva  "
limpo := nome.trim()
assert limpo is "Maria da Silva"
assert limpo.upper() is "MARIA DA SILVA"
assert limpo.startswith("Maria") and limpo.endswith("Silva")
assert limpo[0:5] is "Maria"                   // fatia: do 0 ate antes do 5
assert limpo[-5:] is "Silva"
assert "da" in limpo
assert limpo.replace("da ", "") is "Maria Silva"
assert limpo.split(" ") is ["Maria", "da", "Silva"]
assert ", ".join(["a", "b"]) is "a, b"
assert len("cafe") is 4`, lang: 'df' },
  {"h2": "Formatar"},
  { code: `preco := 1234.5
assert $"R$ {round(preco, 2)}" is "R$ 1234.5"
assert str(7).pad_start(3, "0") is "007"
assert "ab".pad_end(5, ".") is "ab..."
item := {"id": 7}
assert $"item {item["id"]}" is "item 7"        // aspas normais dentro de {}`, lang: 'df' },
  {"h2": "Várias linhas"},
  { code: `sql := """SELECT nome
FROM clientes
WHERE ativo = 1"""
assert len(sql.lines()) is 3`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Dentro de `$\"{…}\"`, aspas normais", "texto": "`$\"item {v[\"id\"]}\"` funciona; `$\"item {v[\\\"id\\\"]}\"` não — o escape quebra a leitura, e a mensagem (*“Unterminated interpolation”*) não aponta para a causa."}},
  {"p": "Continue em [Interpolação](/docs/fundamentos/interpolacao) e [Arcane.Regex](/docs/biblioteca/regex)."},
];

const headings = [{ id: 'formatar', text: "Formatar", level: 2 as const }, { id: 'varias-linhas', text: "Várias linhas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Texto a fundo"}
      description={"Fatiar, procurar, trocar, dividir, juntar e formatar — e o texto de várias linhas."}
      href={"/docs/fundamentos/textos-avancados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
