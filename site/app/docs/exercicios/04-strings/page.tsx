// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "04 · Textos",
  description: "10 exercícios: interpolação, métodos de texto, formatação e regex.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 04`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[039](#039-strings-basicas)", "**Strings basicas**", "monte, meca e indexe textos."], ["[040](#040-caixa-e-limpeza)", "**Caixa e limpeza**", "normalize um texto sujo vindo de um formulario."], ["[041](#041-busca-dentro-de-texto)", "**Busca dentro de texto**", "descubra se e onde um trecho aparece."], ["[042](#042-split-e-join)", "**split e join**", "converta um CSV de uma linha em cluster e volte para texto."], ["[043](#043-substituicao-e-preenchimento)", "**Substituicao e preenchimento**", "mascare um documento e alinhe uma coluna."], ["[044](#044-palindromo)", "**Palindromo**", "verifique se uma frase e palindromo ignorando espacos e caixa."], ["[045](#045-contagem-de-palavras)", "**Contagem de palavras**", "conte palavras e ache a mais frequente."], ["[046](#046-templates-de-texto)", "**Templates de texto**", "preencha um modelo com dados de um vault."], ["[047](#047-expressoes-regulares)", "**Expressoes regulares**", "valide e extraia dados com Arcane.Regex."], ["[048](#048-cifra-de-cesar)", "**Cifra de Cesar**", "cifre e decifre um texto deslocando as letras."]]}},
  {"h2": "039 · Strings basicas"},
  {"p": "**Enunciado.** monte, meca e indexe textos."},
  { code: `nome := "DataForge"
out nome.length(), nome[0], nome[-1], nome[0:4]

assert nome.length() is 9, "tamanho"
assert nome[0] is "D", "primeiro caractere"
assert nome[-1] is "e", "ultimo caractere"
assert nome[0:4] is "Data", "fatia"
assert nome + " v3" is "DataForge v3", "concatenacao"
assert "ab".repeat(3) is "ababab", "repeticao"`, lang: 'df', title: `exercicios/04-strings/039_basico_strings.df` },
  {"h2": "040 · Caixa e limpeza"},
  {"p": "**Enunciado.** normalize um texto sujo vindo de um formulario."},
  { code: `bruto := "   joao DA silva   "
limpo := bruto.trim()

out "'" + bruto + "'"
out "'" + limpo + "'"
out limpo.upper(), limpo.lower(), limpo.title()

assert limpo is "joao DA silva", "trim"
assert limpo.upper() is "JOAO DA SILVA", "upper"
assert limpo.lower() is "joao da silva", "lower"
assert limpo.title() is "Joao Da Silva", "title"
assert limpo.capitalize() is "Joao da silva", "capitalize"`, lang: 'df', title: `exercicios/04-strings/040_caixa_e_limpeza.df` },
  {"h2": "041 · Busca dentro de texto"},
  {"p": "**Enunciado.** descubra se e onde um trecho aparece."},
  { code: `frase := "DataForge e uma linguagem de programacao"

out frase.contains("linguagem"), frase.find("linguagem"), frase.startswith("Data"), frase.endswith("cao")

assert frase.contains("linguagem") is yes, "contains"
assert frase.find("linguagem") is 16, "posicao"
assert frase.find("python") is -1, "ausente devolve -1"
assert frase.startswith("Data") is yes, "startswith"
assert frase.endswith("cao") is yes, "endswith"
assert frase.count("a") is 7, "contagem de a"`, lang: 'df', title: `exercicios/04-strings/041_busca_em_texto.df` },
  {"h2": "042 · split e join"},
  {"p": "**Enunciado.** converta um CSV de uma linha em cluster e volte para texto."},
  { code: `linha := "nome,idade,cidade"
campos := linha.split(",")
out campos

remontado := ";".join(campos)
out remontado

assert campos is ["nome", "idade", "cidade"], "split"
assert remontado is "nome;idade;cidade", "join"
assert "a b c".words() is ["a", "b", "c"], "words"
assert "l1\\nl2".lines() is ["l1", "l2"], "lines"`, lang: 'df', title: `exercicios/04-strings/042_split_join.df` },
  {"h2": "043 · Substituicao e preenchimento"},
  {"p": "**Enunciado.** mascare um documento e alinhe uma coluna."},
  { code: `cpf := "123.456.789-00"
mascarado := cpf.replace("123", "***")
out mascarado

assert mascarado is "***.456.789-00", "replace"
assert "abc".pad_start(6, ".") is "...abc", "pad_start"
assert "abc".pad_end(6, ".") is "abc...", "pad_end"
assert "7".zfill(3) is "007", "zfill"
assert "  meio  ".strip() is "meio", "strip"

cabecalho := "item".pad_end(10) + "qtd".pad_start(5)
out cabecalho
assert cabecalho.length() is 15, "largura da coluna"`, lang: 'df', title: `exercicios/04-strings/043_substituicao.df` },
  {"h2": "044 · Palindromo"},
  {"p": "**Enunciado.** verifique se uma frase e palindromo ignorando espacos e caixa."},
  { code: `action eh_palindromo(texto):
    limpo := texto.lower().replace(" ", "")
    yield limpo is limpo.reverse()

cycle t in ["Ana", "socorram me subi no onibus em marrocos", "DataForge"]:
    out t, "->", eh_palindromo(t)

assert eh_palindromo("Ana") is yes, "Ana"
assert eh_palindromo("socorram me subi no onibus em marrocos") is yes, "frase"
assert eh_palindromo("DataForge") is no, "nao e palindromo"`, lang: 'df', title: `exercicios/04-strings/044_inversao_palindromo.df` },
  {"h2": "045 · Contagem de palavras"},
  {"p": "**Enunciado.** conte palavras e ache a mais frequente."},
  { code: `texto := "o rato roeu a roupa do rei de roma o rato fugiu"
palavras := texto.words()
freq := palavras.frequencies()

out "palavras:", len(palavras)
out "distintas:", len(freq.keys())

top := ""
maximo := 0
cycle par in freq.items():
    given par[1] bigger maximo:
        maximo := par[1]
        top := par[0]

out "mais frequente:", top, "(" + str(maximo) + "x)"
assert len(palavras) is 12, "12 palavras"
assert freq["rato"] is 2, "rato aparece 2x"
assert maximo is 2, "frequencia maxima"`, lang: 'df', title: `exercicios/04-strings/045_contagem_palavras.df` },
  {"h2": "046 · Templates de texto"},
  {"p": "**Enunciado.** preencha um modelo com dados de um vault."},
  { code: `adopt Arcane.Text as Text

modelo := "Ola {nome}, voce tem {pontos} pontos."
dados := {"nome": "Ana", "pontos": 120}
mensagem := Text.render(modelo, dados)

out mensagem
assert mensagem is "Ola Ana, voce tem 120 pontos.", "render"

assert Text.slug("Ola Mundo DataForge!") is "ola-mundo-dataforge", "slug"
assert Text.snake_case("MinhaVariavelLegal") is "minha_variavel_legal", "snake_case"
assert Text.truncate("frase bem longa demais", 10) is "frase b...", "truncate"
out Text.slug("Ola Mundo DataForge!")`, lang: 'df', title: `exercicios/04-strings/046_template.df` },
  {"h2": "047 · Expressoes regulares"},
  {"p": "**Enunciado.** valide e extraia dados com Arcane.Regex."},
  { code: `adopt Arcane.Regex as Regex

texto := "contato: ana@exemplo.com e bruno@teste.org, tel (48) 99999-1234"

emails := Regex.extract_emails(texto)
numeros := Regex.extract_numbers(texto)

out "emails: ", emails
out "numeros:", numeros

assert len(emails) is 2, "dois emails"
assert emails[0] is "ana@exemplo.com", "primeiro email"
assert Regex.is_email("ana@exemplo.com") is yes, "email valido"
assert Regex.is_email("ana@") is no, "email invalido"
assert Regex.test("\\\\d+", "abc123") is yes, "test encontra digitos"
assert Regex.replace_all("\\\\d", "#", "texto1 texto2") is "texto# texto#", "replace_all"`, lang: 'df', title: `exercicios/04-strings/047_regex.df` },
  {"h2": "048 · Cifra de Cesar"},
  {"p": "**Enunciado.** cifre e decifre um texto deslocando as letras."},
  { code: `action cifrar(texto, desloc):
    saida := ""
    cycle c in texto:
        given c.isalpha():
            base := 97
            given c.isupper():
                base := 65
            pos := (ord(c) - base + desloc) % 26
            saida += char(base + pos)
        otherwise:
            saida += c
    yield saida

original := "DataForge Rocks"
cifrado := cifrar(original, 3)
decifrado := cifrar(cifrado, -3)

out "original: ", original
out "cifrado:  ", cifrado
out "decifrado:", decifrado

assert cifrado is "GdwdIrujh Urfnv", "cifra +3"
assert decifrado is original, "ida e volta"`, lang: 'df', title: `exercicios/04-strings/048_cifra_cesar.df` },
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/04-strings/039_basico_strings.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '039-strings-basicas', text: "039 · Strings basicas", level: 2 as const }, { id: '040-caixa-e-limpeza', text: "040 · Caixa e limpeza", level: 2 as const }, { id: '041-busca-dentro-de-texto', text: "041 · Busca dentro de texto", level: 2 as const }, { id: '042-split-e-join', text: "042 · split e join", level: 2 as const }, { id: '043-substituicao-e-preenchimento', text: "043 · Substituicao e preenchimento", level: 2 as const }, { id: '044-palindromo', text: "044 · Palindromo", level: 2 as const }, { id: '045-contagem-de-palavras', text: "045 · Contagem de palavras", level: 2 as const }, { id: '046-templates-de-texto', text: "046 · Templates de texto", level: 2 as const }, { id: '047-expressoes-regulares', text: "047 · Expressoes regulares", level: 2 as const }, { id: '048-cifra-de-cesar', text: "048 · Cifra de Cesar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"04 · Textos"}
      description={"10 exercícios: interpolação, métodos de texto, formatação e regex."}
      href={"/docs/exercicios/04-strings"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
