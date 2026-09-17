"""Arcane.Quadro — a tabela de dados.

O teste de uma estrutura de dados é o que ela **devolve**, e não como
ela guarda. Por isso quase tudo aqui roda DataForge de verdade e compara
a saída: um quadro pode estar columnar e perfeito por dentro e responder
a coluna errada na fronteira.
"""

import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import DataForgeError            # noqa: E402
from dataforge.interpreter import Interpreter          # noqa: E402
from dataforge.lexer import tokenize                   # noqa: E402
from dataforge.parser import parse                     # noqa: E402
from dataforge.stdlib.arcane_quadro import Quadro      # noqa: E402

CABECA = 'adopt Arcane.Quadro as Q\n'

VENDAS = '''v := Q.de_vaults([
    {"produto": "cafe",   "regiao": "sul",   "valor": 120.0, "qtd": 4},
    {"produto": "cafe",   "regiao": "norte", "valor": 90.0,  "qtd": 3},
    {"produto": "cha",    "regiao": "sul",   "valor": 60.0,  "qtd": 2},
    {"produto": "cha",    "regiao": "norte", "valor": void,  "qtd": 1},
    {"produto": "acucar", "regiao": "sul",   "valor": 30.0,  "qtd": 5}
])
'''


def rodar(corpo, com_vendas=True):
    """Executa DataForge e devolve o que foi impresso."""
    fonte = CABECA + (VENDAS if com_vendas else "") + corpo
    arvore = parse(tokenize(fonte, "<q>"), "<q>")
    guardado, sys.stdout = sys.stdout, io.StringIO()
    try:
        Interpreter().run(arvore, "<q>")
        return sys.stdout.getvalue().strip()
    finally:
        sys.stdout = guardado


# ═══ Nascer ════════════════════════════════════════════════

def test_de_vaults_descobre_as_colunas_na_ordem_em_que_aparecem():
    """A ORDEM importa: um CSV gravado com as colunas embaralhadas não é
    o mesmo arquivo."""
    assert rodar('out v.colunas()') == "[produto, regiao, valor, qtd]"


def test_uma_linha_com_coluna_a_mais_nao_perde_a_coluna():
    assert rodar('q := Q.de_vaults([{"a": 1}, {"a": 2, "b": 3}])\n'
                 'out q.colunas(), q.coluna("b")', False) == "[a, b] [void, 3]"


def test_de_colunas_recusa_tamanhos_diferentes():
    """Um quadro é retangular. Aceitar e completar calado esconderia o
    engano de quem montou as colunas."""
    with pytest.raises(DataForgeError) as e:
        rodar('out Q.de_colunas({"a": [1, 2], "b": [3]})', False)
    assert "tamanhos diferentes" in e.value.message


def test_de_vaults_recusa_o_que_nao_e_vault():
    with pytest.raises(DataForgeError) as e:
        rodar('out Q.de_vaults([1, 2, 3])', False)
    assert "vault" in e.value.message


# ═══ O protocolo: por que cycle e >> funcionam de graça ════

def test_o_pipeline_da_linguagem_atravessa_um_quadro():
    """Nada no `>>` sabe o que é um quadro. Ele funciona porque iterar um
    quadro dá LINHAS como vault — o mesmo protocolo que faz a ponte para
    o Python funcionar."""
    assert rodar('out v >> sift l: l["qtd"] bigger 3 >> morph l: l["produto"]') \
        == "[cafe, acucar]"


def test_cycle_percorre_linhas_e_len_conta_linhas():
    assert rodar('total := 0\ncycle l in v:\n    total += l["qtd"]\n'
                 'out total, len(v)') == "15 5"


def test_indexar_por_texto_da_coluna_e_por_numero_da_linha():
    assert rodar('out v["qtd"]') == "[4, 3, 2, 1, 5]"
    assert rodar('out v[0]["produto"], v[0:2].altura()') == "cafe 2"


def test_typeof_responde_Quadro():
    """O nome do tipo é o da linguagem, e não o da classe do Python."""
    assert rodar('out typeof(v)') == "Quadro"


# ═══ Escolher ══════════════════════════════════════════════

def test_pegar_devolve_as_colunas_na_ordem_pedida():
    assert rodar('out v.pegar("qtd", "produto").colunas()') == "[qtd, produto]"


def test_sem_remove_e_mantem_o_resto_na_ordem():
    assert rodar('out v.sem("valor", "qtd").colunas()') == "[produto, regiao]"


def test_onde_filtra_pela_linha_inteira():
    assert rodar('out v.onde(lambda l: l["regiao"] is "sul").altura()') == "3"


def test_ordenar_poe_a_ausencia_no_fim():
    """Ordenar com `void` no meio é o caso que mais quebra ordenação
    ingênua — tipos diferentes não se comparam."""
    assert rodar('out v.ordenar("valor").coluna("valor")') \
        == "[30.0, 60.0, 90.0, 120.0, void]"
    assert rodar('out v.ordenar("valor", yes).coluna("valor")') \
        == "[void, 120.0, 90.0, 60.0, 30.0]"


def test_ordenar_por_duas_colunas():
    assert rodar('out v.ordenar(["regiao", "qtd"]).coluna("qtd")') \
        == "[1, 3, 2, 4, 5]"


def test_distintas_e_duplicadas_sao_complementares():
    fonte = ('q := Q.de_vaults([{"a": 1}, {"a": 1}, {"a": 2}])\n'
             'out q.distintas().altura(), q.duplicadas().altura()')
    assert rodar(fonte, False) == "2 2"


# ═══ Mudar ═════════════════════════════════════════════════

def test_com_aceita_valor_cluster_e_acao():
    assert rodar('out v.com("fixo", 1).coluna("fixo")') == "[1, 1, 1, 1, 1]"
    assert rodar('out v.com("dobro", lambda l: l["qtd"] * 2).coluna("dobro")') \
        == "[8, 6, 4, 2, 10]"


def test_com_recusa_um_cluster_de_tamanho_errado():
    with pytest.raises(DataForgeError) as e:
        rodar('out v.com("x", [1, 2])')
    assert "retangular" in e.value.dica


def test_todo_verbo_devolve_um_quadro_NOVO():
    """Como record e `with`: o original nunca muda. É o que permite
    comparar o antes e o depois, e o que torna um pipeline reexecutável."""
    assert rodar('antes := v.altura()\n'
                 'depois := v.onde(lambda l: no).altura()\n'
                 'out antes, depois, v.altura()') == "5 0 5"


def test_converter_devolve_void_no_que_nao_converte():
    """Levantar na primeira célula ruim de um CSV de um milhão de linhas
    não ajuda ninguém: o perfil conta quantas não converteram."""
    fonte = ('q := Q.de_vaults([{"n": "1"}, {"n": "x"}, {"n": "3"}])\n'
             'out q.converter({"n": "Integer"}).coluna("n")')
    assert rodar(fonte, False) == "[1, void, 3]"


def test_converter_recusa_um_tipo_que_nao_existe():
    with pytest.raises(DataForgeError) as e:
        rodar('out v.converter({"qtd": "Numero"})')
    assert "os tipos são" in e.value.nota


def test_inferir_tipos_nao_converte_a_coluna_pela_metade():
    """Converter o que dá e deixar o resto como texto produziria uma
    coluna de DOIS tipos — pior que uma de um tipo errado."""
    fonte = ('q := Q.de_vaults([{"a": "1", "b": "1"}, {"a": "2", "b": "n/a"}])\n'
             'r := q.inferir_tipos()\n'
             'out typeof(r.coluna("a")[0]), typeof(r.coluna("b")[0])')
    assert rodar(fonte, False) == "Integer String"


# ═══ Ausência ══════════════════════════════════════════════

def test_os_tres_vazios_sao_a_mesma_ausencia():
    """`void`, texto vazio e NaN dizem a mesma coisa. Tratá-los como
    coisas diferentes é de onde vem metade do bug de limpeza."""
    fonte = ('q := Q.de_vaults([{"a": void}, {"a": ""}, {"a": "  "}, {"a": 1}])\n'
             'out q.nulos()["a"], q.sem_nulos().altura()')
    assert rodar(fonte, False) == "3 1"


def test_preencher_com_valor_com_media_e_com_o_vizinho():
    assert rodar('out v.preencher({"valor": 0.0}).coluna("valor")') \
        == "[120.0, 90.0, 60.0, 0.0, 30.0]"
    assert rodar('out v.preencher({"valor": "media"}).coluna("valor")') \
        == "[120.0, 90.0, 60.0, 75.0, 30.0]"
    assert rodar('out v.preencher({"valor": "anterior"}).coluna("valor")') \
        == "[120.0, 90.0, 60.0, 60.0, 30.0]"


def test_sem_nulos_pode_olhar_so_algumas_colunas():
    assert rodar('out v.sem_nulos("qtd").altura(), v.sem_nulos().altura()') \
        == "5 4"


# ═══ Agrupar ═══════════════════════════════════════════════

def test_agrupar_e_resumir():
    saida = rodar('r := v.agrupar("produto").resumir({"valor": "soma"})\n'
                  'out r.colunas(), r.coluna("valor")')
    assert saida == "[produto, valor] [210.0, 60.0, 30.0]"


def test_duas_agregacoes_ganham_o_nome_da_coluna_e_da_agregacao():
    saida = rodar('r := v.agrupar("produto")'
                  '.resumir({"valor": "soma", "qtd": "media"})\n'
                  'out r.colunas()')
    assert saida == "[produto, valor_soma, qtd_media]"


def test_agrupar_por_duas_colunas():
    assert rodar('out v.agrupar(["regiao", "produto"]).contar().altura()') == "5"


def test_a_agregacao_desconhecida_e_recusada_com_a_lista():
    """A tabela é fechada de propósito: o nome vem como TEXTO, e aceitar
    qualquer ação abriria a porta para um nome vindo de fora."""
    with pytest.raises(DataForgeError) as e:
        rodar('out v.agrupar("produto").resumir({"valor": "medía"})')
    assert "as agregações são" in e.value.nota


def test_a_soma_ignora_a_ausencia_e_a_contagem_a_inclui():
    """São perguntas diferentes: 'quanto vendeu' e 'quantas linhas há'."""
    saida = rodar('r := v.agrupar("produto")'
                  '.resumir({"valor": ["soma", "contagem", "contagem_valida"]})\n'
                  'out r.onde(lambda l: l["produto"] is "cha").para_vaults()')
    assert "valor_soma: 60" in saida
    assert "valor_contagem: 2" in saida
    assert "valor_contagem_valida: 1" in saida


def test_resumir_sem_agrupar_resume_o_quadro_inteiro():
    assert rodar('out v.resumir({"qtd": "soma"}).coluna("qtd")') == "[15]"


def test_contar_valores_vem_do_mais_comum_ao_menos():
    assert rodar('out v.contar_valores("produto").coluna("produto")') \
        == "[cafe, cha, acucar]"


# ═══ Pivô e cruzamento ═════════════════════════════════════

def test_pivotar_vira_colunas():
    saida = rodar('p := v.preencher({"valor": 0.0})'
                  '.pivotar("produto", "regiao", "valor")\n'
                  'out p.colunas()')
    assert saida == "[produto, norte, sul]"


def test_despivotar_e_o_caminho_de_volta():
    fonte = ('q := Q.de_vaults([{"id": 1, "a": 10, "b": 20}])\n'
             'l := q.despivotar("id")\n'
             'out l.altura(), l.colunas()')
    assert rodar(fonte, False) == "2 [id, variavel, valor]"


def test_tabela_cruzada_conta_os_pares():
    assert rodar('out v.tabela_cruzada("produto", "regiao").colunas()') \
        == "[produto, norte, sul]"


# ═══ Juntar ════════════════════════════════════════════════

REGIOES = ('r := Q.de_vaults([{"regiao": "sul", "gerente": "Ana"},\n'
           '                  {"regiao": "leste", "gerente": "Caio"}])\n')


def test_juntar_dentro_so_traz_o_que_casa():
    assert rodar(REGIOES + 'out v.juntar(r, "regiao").altura()') == "3"


def test_juntar_pela_esquerda_mantem_quem_nao_casou():
    saida = rodar(REGIOES + 'j := v.juntar(r, "regiao", "esquerda")\n'
                            'out j.altura(), j.nulos()["gerente"]')
    assert saida == "5 2"


def test_juntar_por_fora_traz_os_dois_lados():
    assert rodar(REGIOES + 'out v.juntar(r, "regiao", "fora").altura()') == "6"


def test_o_tipo_de_juncao_desconhecido_e_recusado():
    with pytest.raises(DataForgeError) as e:
        rodar(REGIOES + 'out v.juntar(r, "regiao", "interno")')
    assert "dentro, esquerda, direita, fora" in e.value.nota


def test_empilhar_completa_a_coluna_que_falta_de_um_lado():
    fonte = ('a := Q.de_vaults([{"x": 1}])\n'
             'b := Q.de_vaults([{"y": 2}])\n'
             'out a.empilhar(b).colunas(), a.empilhar(b).altura()')
    assert rodar(fonte, False) == "[x, y] 2"


# ═══ Escala e feições ══════════════════════════════════════

def test_normalizar_leva_para_zero_um():
    assert rodar('out v.normalizar("qtd").coluna("qtd")') \
        == "[0.75, 0.5, 0.25, 0.0, 1.0]"


def test_normalizar_uma_coluna_constante_da_zero_e_nao_erro():
    fonte = ('q := Q.de_vaults([{"a": 5}, {"a": 5}])\n'
             'out q.normalizar("a").coluna("a")')
    assert rodar(fonte, False) == "[0.0, 0.0]"


def test_padronizar_deixa_media_zero():
    saida = rodar('p := v.padronizar("qtd")\n'
                  'out round(sum(p.coluna("qtd")), 6)')
    assert saida == "0.0"


def test_codificar_cria_uma_coluna_por_valor():
    saida = rodar('c := v.codificar("regiao")\n'
                  'out c.colunas()')
    assert "regiao_norte" in saida and "regiao_sul" in saida
    assert "regiao," not in saida        # a original sai


def test_discretizar_transforma_numero_em_faixa():
    saida = rodar('d := v.discretizar("qtd", 2, ["baixo", "alto"])\n'
                  'out d.coluna("qtd")')
    assert saida == "[alto, alto, baixo, baixo, alto]"


# ═══ Estatística ═══════════════════════════════════════════

def test_descrever_tem_UM_contrato():
    """`Analytics.describe` e `Data.describe` devolviam chaves diferentes
    para a mesma pergunta. Este é o formato único."""
    saida = rodar('out v.descrever().colunas()')
    assert saida == ("[coluna, contagem, ausentes, media, desvio, "
                     "minimo, q1, mediana, q3, maximo]")


def test_descrever_conta_a_ausencia_separado_da_media():
    """Uma média sobre dados com buraco não avisa que tinha buraco."""
    saida = rodar('d := v.descrever().onde(lambda l: l["coluna"] is "valor")\n'
                  'out d.coluna("contagem"), d.coluna("ausentes"), '
                  'd.coluna("media")')
    assert saida == "[4] [1] [75.0]"


def test_descrever_ignora_coluna_de_texto():
    assert rodar('out v.descrever().coluna("coluna")') == "[valor, qtd]"


def test_correlacao_de_uma_coluna_consigo_e_um():
    assert rodar('c := v.correlacao(["qtd"])\nout c.coluna("qtd")') == "[1.0]"


def test_perfil_responde_o_que_se_pergunta_num_conjunto_novo():
    saida = rodar('p := v.perfil().onde(lambda l: l["coluna"] is "valor")\n'
                  'out p.coluna("tipo"), p.coluna("ausentes_pct"), '
                  'p.coluna("distintos")')
    assert saida == "[Float] [20.0] [4]"


def test_fora_da_curva_acha_o_ponto_distante():
    fonte = ('q := Q.de_vaults([{"n": 1}, {"n": 2}, {"n": 2}, {"n": 3},\n'
             '                  {"n": 2}, {"n": 900}])\n'
             'out q.fora_da_curva("n").coluna("n")')
    assert rodar(fonte, False) == "[900]"


# ═══ A coluna que não existe ═══════════════════════════════

def test_coluna_ausente_e_erro_com_sugestao():
    """Devolver uma coluna vazia calada é o jeito mais rápido de um
    relatório sair errado sem ninguém notar."""
    with pytest.raises(DataForgeError) as e:
        rodar('q := Q.de_vaults([{"nome": "a"}])\nout q.pegar("nomes")', False)
    assert "não existe" in e.value.message
    assert "você quis dizer 'nome'" in e.value.dica


def test_a_lista_de_colunas_vem_na_nota():
    with pytest.raises(DataForgeError) as e:
        rodar('out v.coluna("zzz")')
    assert "produto, regiao, valor, qtd" in e.value.nota


# ═══ Entrada e saída ═══════════════════════════════════════

def test_ida_e_volta_por_csv_preserva_os_valores(tmp_path):
    alvo = str(tmp_path / "v.csv")
    saida = rodar(f'v.para_csv("{alvo}")\n'
                  f'lido := Q.de_csv("{alvo}")\n'
                  'out lido.altura(), lido.colunas(), lido.coluna("qtd")')
    assert saida == "5 [produto, regiao, valor, qtd] [4, 3, 2, 1, 5]"


def test_o_csv_traz_tudo_como_texto_e_a_inferencia_conserta(tmp_path):
    """Somar coluna de texto é o primeiro engano de quem chega."""
    alvo = str(tmp_path / "n.csv")
    fonte = (f'q := Q.de_vaults([{{"n": 1}}, {{"n": 2}}])\n'
             f'q.para_csv("{alvo}")\n'
             f'sem := Q.de_csv("{alvo}", ",", no)\n'
             f'com := Q.de_csv("{alvo}")\n'
             'out typeof(sem.coluna("n")[0]), typeof(com.coluna("n")[0])')
    assert rodar(fonte, False) == "String Integer"


def test_a_ausencia_vira_celula_vazia_no_csv(tmp_path):
    alvo = str(tmp_path / "a.csv")
    rodar(f'v.para_csv("{alvo}")')
    texto = io.open(alvo, encoding="utf-8").read()
    assert "norte,," in texto


def test_para_json_sem_caminho_devolve_o_texto():
    assert rodar('out v.para_json().starts_with("[")') == "yes"


def test_texto_desenha_o_quadro_e_diz_o_tamanho():
    saida = rodar('out v.texto()')
    assert "produto" in saida and "[5 linha(s) × 4 coluna(s)]" in saida


def test_texto_corta_e_diz_quantas_ficaram_de_fora():
    assert "3 linha(s) a mais" in rodar('out v.texto(2)')


# ═══ O que o Python vê ═════════════════════════════════════

def test_o_quadro_e_imutavel_tambem_do_lado_do_python():
    q = Quadro.de_vaults([{"a": 1}, {"a": 2}])
    filtrado = q.onde(lambda l: l["a"] > 1)
    assert len(q) == 2 and len(filtrado) == 1
    assert q.coluna("a") == [1, 2]


def test_colunar_por_dentro_e_vault_por_fora():
    """A decisão que faz `descrever` ser uma passada por coluna, e a
    linha continuar sendo a forma que o resto da linguagem usa."""
    q = Quadro.de_vaults([{"a": 1, "b": "x"}, {"a": 2, "b": "y"}])
    assert q.para_colunas() == {"a": [1, 2], "b": ["x", "y"]}
    assert q.para_vaults() == [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]


# ═══ A sintaxe da linguagem ════════════════════════════════
#
# Os seis verbos são CONTEXTUAIS, como as onze palavras do Kiln: valem
# só logo depois de um '>>', e continuam livres como nome em todo o
# resto. 'agrupar', 'ordenar' e 'pegar' são nomes bons demais para tirar
# de quem escreve.

def test_o_pipeline_do_documento_roda():
    """A forma que o documento de origem esboçou, na gramática daqui."""
    saida = rodar('''r := v
    >> onde valor bigger 50
    >> agrupar produto
    >> resumir {"valor": "soma"}
    >> ordenar valor desc
out r.para_vaults()''')
    assert saida == "[{produto: cafe, valor: 210.0}, {produto: cha, valor: 60.0}]"


def test_a_coluna_se_escreve_nua_dentro_de_onde():
    """É o que faz o verbo valer a pena: `onde valor bigger 50` lê como
    se lê, sem `lambda l: l["valor"]`."""
    assert rodar('out (v >> onde qtd bigger 3).altura()') == "2"


def test_a_coluna_tambem_se_escreve_entre_aspas():
    """Nem todo cabeçalho de CSV é um identificador válido: 'Valor Total'
    e 'preco/kg' só se alcançam com aspas."""
    fonte = ('q := Q.de_vaults([{"Valor Total": 10}, {"Valor Total": 30}])\n'
             'out (q >> onde q bigger 0 >> pegar "Valor Total").colunas()')
    assert rodar(fonte.replace('onde q bigger 0 >> ', ''), False) \
        == "[Valor Total]"


def test_um_nome_de_fora_continua_alcancavel_dentro_do_onde():
    """A coluna vence, mas o escopo de fora não some: um limite guardado
    numa variável é o caso mais comum que existe."""
    assert rodar('limite := 100.0\nout (v >> onde valor bigger limite).altura()') \
        == "1"


def test_a_coluna_vence_um_nome_de_fora_com_o_mesmo_nome():
    """Dentro de um `onde`, um nome nu é uma COLUNA. É a regra do verbo,
    e ela precisa ser previsível."""
    assert rodar('qtd := 999\nout (v >> onde qtd bigger 3).altura()') == "2"


def test_os_verbos_convivem_com_sift_e_morph_no_mesmo_pipeline():
    """A conversão virou preguiçosa: cada estágio pede a forma de que
    precisa, na hora em que precisa."""
    assert rodar('out v >> onde regiao is "sul" >> morph l: l["produto"]') \
        == "[cafe, cha, acucar]"


def test_um_cluster_de_vaults_tambem_serve_de_fonte():
    """É o que sai de `IO.read_csv(c, yes)` e de `Database.query` —
    obrigar a converter na mão faria o verbo valer menos onde o dado
    entra."""
    fonte = ('linhas := [{"a": 1}, {"a": 5}]\n'
             'out (linhas >> onde a bigger 2).altura()')
    assert rodar(fonte, False) == "1"


def test_agrupar_sem_resumir_diz_o_que_falta():
    """Um agrupamento não tem forma retangular até agregar."""
    with pytest.raises(DataForgeError) as e:
        rodar('out v >> agrupar produto >> ordenar valor')
    assert "depois de 'agrupar' vem 'resumir'" in e.value.nota


def test_pipelinar_de_um_numero_continua_sendo_recusado():
    with pytest.raises(DataForgeError) as e:
        rodar('out 42 >> onde a bigger 1', False)
    assert "quadro" in e.value.message


def test_os_verbos_continuam_livres_como_nome_de_variavel():
    """O preço de uma palavra reservada é ela sair do vocabulário de quem
    escreve. Estas seis não saíram."""
    fonte = ('onde := 1\npegar := 2\nsem := 3\n'
             'agrupar := 4\nresumir := 5\nordenar := 6\n'
             'out onde + pegar + sem + agrupar + resumir + ordenar')
    assert rodar(fonte, False) == "21"


def test_o_analisador_nao_acusa_a_coluna_nua():
    """Inferir a expressão de um `onde` no escopo de fora acusaria
    `onde valor bigger 50` com "'valor' is not defined" — um falso alarme
    no caminho mais comum do verbo."""
    from dataforge.typechecker import check_program

    fonte = CABECA + VENDAS + 'out (v >> onde valor bigger 50).altura()'
    erros = [d for d in check_program(parse(tokenize(fonte, "t.df"), "t.df"),
                                      "t.df") if d.severity == "error"]
    assert not erros, [d.message for d in erros]


def test_ordenar_aceita_desc_e_decrescente():
    assert rodar('out (v >> ordenar qtd desc).coluna("qtd")') \
        == "[5, 4, 3, 2, 1]"
    assert rodar('out (v >> ordenar qtd decrescente).coluna("qtd")') \
        == "[5, 4, 3, 2, 1]"


def test_a_falta_do_nome_da_coluna_diz_as_duas_formas():
    from dataforge.errors import ParseError

    with pytest.raises(ParseError) as e:
        rodar('out v >> agrupar 3.5')
    assert "nome de uma coluna" in e.value.message


def test_onde_usa_a_logica_de_tres_valores_do_sql():
    """Comparar com o DESCONHECIDO não dá nem sim nem não, e a linha não
    passa. É o que SQL faz, e o que toda ferramenta de dados faz.

    A alternativa — levantar — é defensável e torna o verbo inútil: todo
    conjunto real tem ausência, e o primeiro `onde` morreria na primeira
    linha vazia.
    """
    # A linha com 'valor' void não passa, e não derruba o programa.
    assert rodar('out (v >> onde valor bigger 0).altura()') == "4"
    # E quem QUER a ausência pergunta por ela.
    assert rodar('out (v >> onde valor is void).altura()') == "1"


def test_onde_so_engole_a_comparacao_com_o_desconhecido():
    """Uma coluna que não existe, uma ação que quebra, uma divisão por
    zero — tudo o mais sobe. Engolir todo erro do teste esconderia um
    nome de coluna digitado errado."""
    with pytest.raises(DataForgeError) as e:
        rodar('out (v >> onde qtd / 0 bigger 1).altura()')
    assert "zero" in e.value.message.lower()
