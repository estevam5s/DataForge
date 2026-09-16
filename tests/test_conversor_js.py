"""JavaScript e TypeScript → DataForge.

O teste forte de um conversor não é comparar texto com texto: é
**rodar** o que saiu e conferir o resultado. Um conversor pode produzir
uma tradução bonita e errada, e só a execução denuncia.

Por isso quase todo teste aqui converte, executa e compara a saída com o
que o JavaScript original produziria.
"""

import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.interpreter import Interpreter          # noqa: E402
from dataforge.lexer import tokenize                   # noqa: E402
from dataforge.migrar_js import (ErroDeLeitura,        # noqa: E402
                                 analisar, converter_fonte, tokenizar)
from dataforge.parser import parse                     # noqa: E402
from dataforge.typechecker import check_program        # noqa: E402


def converter(fonte, arquivo="t.js"):
    texto, pendencias = converter_fonte(fonte, arquivo)
    return texto, pendencias


def rodar(fonte_js, arquivo="t.js"):
    """Converte, executa e devolve a saída — o teste que importa."""
    texto, _ = converter_fonte(fonte_js, arquivo)
    arvore = parse(tokenize(texto, "convertido.df"), "convertido.df")
    interpretador = Interpreter()
    guardado = sys.stdout
    sys.stdout = capturado = io.StringIO()
    try:
        interpretador.run(arvore)
    finally:
        sys.stdout = guardado
    return capturado.getvalue().strip()


def limpo(fonte_js, arquivo="t.js"):
    """O `check` não acusa erro no que saiu."""
    texto, _ = converter_fonte(fonte_js, arquivo)
    arvore = parse(tokenize(texto, "convertido.df"), "convertido.df")
    return [d for d in check_program(arvore, "convertido.df")
            if d.severity == "error"]


# ═══ O tokenizador ═════════════════════════════════════════

def test_a_barra_de_regex_nao_e_divisao():
    """`/\\d+/.test(s)` lido como divisão faz o resto da linha virar lixo."""
    tokens = tokenizar("const r = /\\d+/g;")
    assert [t.tipo for t in tokens if t.tipo == "REGEX"] == ["REGEX"]
    # E uma divisão de verdade continua divisão.
    tokens = tokenizar("const x = a / b / c;")
    assert not [t for t in tokens if t.tipo == "REGEX"]


def test_o_template_guarda_texto_e_expressao_separados():
    tokens = tokenizar("`oi ${nome}!`")
    partes = tokens[0].valor
    assert partes[0] == ("texto", "oi ")
    assert partes[1] == ("expr", "nome")
    assert partes[2] == ("texto", "!")


def test_chave_dentro_de_template_nao_fecha_cedo():
    """`${ {a: 1} }` tem chaves dentro, e contar é o que segura."""
    tokens = tokenizar("`v: ${ {a: 1}['a'] }`")
    assert tokens[0].valor[-1] == ("expr", " {a: 1}['a'] ")


def test_o_comentario_some_e_a_linha_continua_certa():
    tokens = tokenizar("// nota\nconst x = 1; /* outra\nnota */ const y = 2;")
    nomes = [t.valor for t in tokens if t.tipo == "NOME"]
    assert nomes == ["x", "y"]
    assert tokens[-2].linha == 3


# ═══ O que roda igual ══════════════════════════════════════

def test_variaveis_e_saida():
    assert rodar("const a = 1;\nlet b = 2;\nconsole.log(a + b);") == "3"


def test_const_vira_steady():
    texto, _ = converter("const a = 1;")
    assert "steady a := 1" in texto


def test_template_literal_vira_interpolacao():
    assert rodar("const n = 'Ana';\nconsole.log(`oi, ${n}!`);") == "oi, Ana!"


def test_funcao_e_retorno():
    assert rodar("function dobro(x) { return x * 2; }\n"
                 "console.log(dobro(21));") == "42"


def test_condicional_com_os_tres_ramos():
    fonte = """
    function nivel(n) {
      if (n > 10) { return 'alto'; }
      else if (n === 10) { return 'dez'; }
      else { return 'baixo'; }
    }
    console.log(nivel(11), nivel(10), nivel(1));
    """
    assert rodar(fonte) == "alto dez baixo"


def test_for_contado_vira_cycle():
    texto, _ = converter("for (let i = 0; i < 3; i++) { console.log(i); }")
    assert "cycle i from 0 to 2:" in texto
    assert rodar("for (let i = 0; i < 3; i++) { console.log(i); }") == "0\n1\n2"


def test_for_que_nao_casa_vira_persist():
    """Inventar um `cycle` a partir de um cabeçalho parecido trocaria o
    número de voltas em silêncio. O `persist` é sempre correto."""
    fonte = "let i = 10;\nfor (; i > 7; i -= 1) { console.log(i); }"
    texto, _ = converter(fonte)
    assert "persist" in texto and "cycle" not in texto
    assert rodar(fonte) == "10\n9\n8"


def test_for_of_e_for_in():
    assert rodar("for (const x of [1, 2]) { console.log(x); }") == "1\n2"
    assert rodar("const v = {a: 1};\n"
                 "for (const k in v) { console.log(k); }") == "a"


def test_while_e_do_while():
    assert rodar("let i = 0;\nwhile (i < 2) { console.log(i); i++; }") == "0\n1"
    assert rodar("let i = 5;\ndo { console.log(i); i++; } while (i < 3);") == "5"


def test_seta_com_expressao_vira_lambda():
    texto, _ = converter("const d = (x) => x * 2;")
    assert "lambda x: x * 2" in texto
    assert rodar("const d = (x) => x * 2;\nconsole.log(d(4));") == "8"


def test_seta_com_bloco_vira_acao_nomeada():
    """O `lambda` da DataForge é uma expressão só; traduzir um bloco para
    lambda produziria algo que não compila."""
    fonte = ("const nums = [1, 2, 3].map(x => { const y = x + 1; return y * 2; });"
             "\nconsole.log(nums);")
    texto, _ = converter(fonte)
    assert "lambda" not in texto.split("map(")[1].split(")")[0]
    assert rodar(fonte) == "[4, 6, 8]"


def test_map_e_filter_encadeados():
    assert rodar("console.log([1,2,3,4].map(n => n * 2).filter(n => n > 4));") \
        == "[6, 8]"


def test_try_catch_finally():
    fonte = """
    try {
      throw new Error('quebrou');
    } catch (e) {
      console.log('peguei:', e.message);
    } finally {
      console.log('fim');
    }
    """
    assert rodar(fonte) == "peguei: quebrou\nfim"


def test_switch_vira_match_sem_os_break():
    """O `break` de um `case` existe para não cair no seguinte, e o
    `match` não cai — mantê-lo viraria um `halt` fora de laço."""
    fonte = """
    function cor(n) {
      switch (n) {
        case 1: return 'um';
        case 2: return 'dois';
        default: return 'outro';
      }
    }
    console.log(cor(1), cor(2), cor(9));
    """
    texto, _ = converter(fonte)
    assert "halt" not in texto
    assert rodar(fonte) == "um dois outro"


def test_classe_com_construtor_e_metodo():
    fonte = """
    class Contador {
      constructor(inicio) { this.valor = inicio; }
      somar(n) { this.valor = this.valor + n; return this.valor; }
    }
    const c = new Contador(10);
    console.log(c.somar(5));
    """
    texto, _ = converter(fonte)
    assert "blueprint Contador:" in texto
    assert "action setup(inicio):" in texto
    assert "self.valor" in texto
    assert rodar(fonte) == "15"


def test_heranca_e_super():
    fonte = """
    class Animal {
      constructor(nome) { this.nome = nome; }
      falar() { return this.nome + ' faz algo'; }
    }
    class Cao extends Animal {
      falar() { return super.falar() + ': au'; }
    }
    console.log(new Cao('Rex').falar());
    """
    assert "extends Animal" in converter(fonte)[0]
    assert rodar(fonte) == "Rex faz algo: au"


def test_estatico_e_prefixo_e_nao_linha_propria():
    fonte = ("class M { static dobro(n) { return n * 2; } }\n"
             "console.log(M.dobro(4));")
    texto, _ = converter(fonte)
    assert "static action dobro(n):" in texto
    assert rodar(fonte) == "8"


def test_desestruturacao_de_lista_e_de_vault():
    assert rodar("const [a, ...resto] = [1, 2, 3];\n"
                 "console.log(a, resto);") == "1 [2, 3]"
    assert rodar("const {x, y} = {x: 1, y: 2};\nconsole.log(x, y);") == "1 2"


def test_ternario_e_encadeamento_opcional():
    assert rodar("const n = 5;\nconsole.log(n > 3 ? 'sim' : 'nao');") == "sim"
    assert rodar("const v = {a: 1};\nconsole.log(v?.a ?? 9);") == "1"


def test_ler_um_campo_ausente_falha_aqui_e_isso_e_de_proposito():
    """A divergência que o conversor **não** mascara.

    Em JavaScript, `v.naoExiste` devolve `undefined` — inclusive com
    `?.`, cuja função é só proteger contra `null` do lado esquerdo. Na
    DataForge, ler uma chave que não está no vault é **erro**.

    Traduzir isso para algo que devolve `void` calado transformaria um
    erro de digitação num valor vazio que atravessa o programa inteiro,
    que é exatamente o bug que a DataForge recusa a ter. A tradução
    mantém o acesso, e o programa falha na linha certa.
    """
    from dataforge.errors import DataForgeError

    with pytest.raises(DataForgeError):
        rodar("const v = {a: 1};\nconsole.log(v?.b ?? 9);")

    # A forma que funciona nas duas: indexar com '??'.
    assert rodar("const v = {a: 1};\nconsole.log(v['b'] ?? 9);") == "9"


def test_os_dois_vazios_do_js_viram_void():
    """A DataForge tem um vazio só; fingir dois seria inventar semântica."""
    texto, _ = converter("const a = null;\nconst b = undefined;")
    assert texto.count(":= void") == 2


def test_operadores_de_igualdade_mudam_de_nome():
    texto, _ = converter("const a = x === y;\nconst b = x !== y;")
    assert " is " in texto and " isnt " in texto


def test_length_vira_len():
    assert rodar("console.log([1,2,3].length);") == "3"


def test_push_vira_append():
    assert rodar("const xs = [];\nxs.push(7);\nconsole.log(xs);") == "[7]"


def test_math_e_json_viram_embutidas():
    assert rodar("console.log(Math.max(1, 9), Math.floor(2.7));") == "9 2"


def test_espalhamento_na_lista_e_na_chamada():
    assert rodar("const a = [1, 2];\nconsole.log([...a, 3]);") == "[1, 2, 3]"


# ═══ TypeScript ════════════════════════════════════════════

def test_anotacoes_de_tipo_sao_aproveitadas():
    texto, _ = converter("function f(n: number, s: string): boolean "
                         "{ return true; }", "t.ts")
    assert "action f(n: Float, s: String) -> Boolean:" in texto


def test_interface_vira_trait():
    texto, _ = converter("interface Forma { area(): number; }", "t.ts")
    assert "trait Forma:" in texto
    assert "action area()" in texto


def test_enum_do_ts_vira_enum():
    texto, _ = converter('enum E { A = "a", B = "b" }', "t.ts")
    assert "enum E:" in texto
    assert 'A := "a"' in texto


def test_apelido_de_tipo_vira_comentario_e_nao_palpite():
    """A DataForge não tem apelido de tipo. Inventar um record com esse
    nome mudaria o que o programa faz."""
    texto, pendencias = converter("type Id = string | number;", "t.ts")
    assert "// type Id = string | number" in texto


def test_o_que_e_so_do_sistema_de_tipos_some():
    fonte = "const x = foo as string;\nconst y = bar!.baz;"
    texto, _ = converter(fonte, "t.ts")
    assert "as string" not in texto
    assert "!" not in texto.split("y :=")[1]


def test_modificadores_de_parametro_do_construtor():
    fonte = ("class P { constructor(private nome: string) {} "
             "ler() { return this.nome; } }\n"
             "console.log(new P('Ana').ler());")
    assert rodar(fonte, "t.ts") == "Ana"


def test_generico_do_ts_nao_quebra_a_leitura():
    fonte = "function primeiro<T>(xs: T[]): T { return xs[0]; }\n" \
            "console.log(primeiro([7, 8]));"
    assert rodar(fonte, "t.ts") == "7"


# ═══ Módulos ═══════════════════════════════════════════════

def test_import_e_export_viram_adopt_e_relay():
    texto, _ = converter("import { a, b as c } from './lib';\n"
                         "export { a };")
    assert "adopt {a, b as c} from ./lib" in texto
    assert "relay a" in texto


def test_export_de_uma_declaracao_declara_e_exporta():
    texto, _ = converter("export function f() { return 1; }")
    assert "action f():" in texto
    assert "relay f" in texto


# ═══ A honestidade ═════════════════════════════════════════

def test_o_que_nao_se_le_recusa_em_vez_de_chutar():
    """Traduzir o que não se leu produz lixo com cara de tradução."""
    with pytest.raises(ErroDeLeitura):
        converter("function ( { ] }")


def test_a_saida_sempre_compila():
    """Uma pendência é um comentário, e comentário sempre compila. É por
    isso que o modo de falhar daqui é 'faltou traduzir', nunca 'gerou
    algo quebrado'."""
    fonte = """
    const a = 1;
    delete a.b;
    label: for (const x of [1]) { console.log(x); }
    """
    try:
        texto, pendencias = converter(fonte)
    except ErroDeLeitura:
        return                       # recusar também é honesto
    parse(tokenize(texto, "t.df"), "t.df")


def test_um_nome_reservado_da_dataforge_ganha_sufixo():
    """`no` é `false` na DataForge: um `const no = 1` vindo do JS não
    pode virar `no := 1`, que é erro de sintaxe."""
    texto, _ = converter("const no = 1;\nconsole.log(no);")
    assert "no_ := 1" in texto
    assert rodar("const no = 1;\nconsole.log(no);") == "1"


def test_o_arquivo_convertido_passa_no_check():
    fonte = """
    class Pilha {
      constructor() { this.itens = []; }
      por(x) { this.itens.push(x); return this; }
      tirar() { return this.itens.pop(); }
    }
    const p = new Pilha();
    p.por(1).por(2);
    console.log(p.tirar());
    """
    assert limpo(fonte) == []
    assert rodar(fonte) == "2"


def test_o_cabecalho_diz_de_onde_veio_e_quantas_pendencias():
    texto, _ = converter("const a = 1;", "app.ts")
    assert "Convertido de app.ts (TypeScript)" in texto
    assert "Nada ficou pendente" in texto
