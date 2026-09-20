#!/usr/bin/env python3
"""
Gera a pagina de referencia da Vitrine a partir do proprio modulo.

    python3 tools/gerar_ref_vitrine.py

A lista de simbolos e as assinaturas saem de dataforge/stdlib/vitrine/.
Escrever isso a mao garantiria que, um dia, a doc listaria uma funcao
que nao existe mais — ou esconderia uma que existe. O script RECUSA
rodar se um simbolo do modulo nao estiver num grupo com resumo: e a
mesma trava do gerador da gramatica do editor.
"""

import inspect
import json
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import marca  # noqa: E402

marca.preparar_saida()

from dataforge.stdlib import get_module   # noqa: E402

DESTINO = os.path.join(RAIZ, "site", "app", "docs", "vitrine",
                       "referencia", "page.tsx")

#: Como agrupar. A ordem aqui e a ordem da pagina.
GRUPOS = [
    ("Aplicação e servidor", [
        "app", "configurar", "configurar_pagina", "pagina", "paginas",
        "rodar", "subir", "servir", "parar_servidor", "montar",
        "modo_servidor"]),
    ("Texto", [
        "titulo", "subtitulo", "cabecalho", "texto", "markdown", "codigo",
        "html", "divisor", "espaco", "escrever", "legenda", "citacao",
        "selo", "selos", "formula", "ajuda", "fluxo", "icone", "icones"]),
    ("Entrada", [
        "botao", "entrada", "area_de_texto", "numero", "deslizante",
        "caixa", "interruptor", "opcao", "escolha", "escolhas", "data",
        "cor", "arquivo", "hora", "periodo", "faixa", "deslizante_opcoes",
        "pilulas", "segmentado", "avaliacao", "tags", "autocompletar",
        "senha", "busca", "email", "camera", "mudou", "mudancas"]),
    ("Dados", [
        "tabela", "frame", "metrica", "json", "vault", "grade", "editor",
        "coluna", "regra", "indicador", "indicadores", "estatisticas",
        "formatar", "moeda", "numero_br", "percentual", "compacto",
        "data_br"]),
    ("Retorno ao usuário", [
        "sucesso", "erro", "aviso", "informacao", "progresso",
        "carregando", "imagem", "audio", "video", "link", "baixar",
        "pdf", "iframe", "logo", "galeria", "toast", "esqueleto",
        "comemorar", "excecao", "status", "chat", "chat_mensagem",
        "chat_entrada", "historico_de_chat", "guardar_no_chat"]),
    ("Layout", [
        "colunas", "linha", "container", "cartao", "expandir", "abas",
        "formulario", "vazio", "lateral", "espacador", "malha", "painel",
        "barra_superior", "dialogo", "popover", "passos", "separador",
        "rolagem", "fragmento", "fragmentos"]),
    ("Gráficos", [
        "grafico", "desenhar", "grafico_linha", "grafico_barras",
        "grafico_barras_h", "grafico_area", "grafico_dispersao",
        "grafico_pizza", "grafico_rosca", "histograma", "paleta",
        "tipos_de_grafico", "grafico_combo", "grafico_barras_100",
        "grafico_area_empilhada", "grafico_funil", "grafico_treemap",
        "grafico_cascata", "grafico_pareto", "grafico_radar",
        "grafico_caixa", "grafico_bolhas", "grafico_dispersao_xy",
        "grafico_velas", "grafico_sankey", "grafico_gantt", "grafico_mapa",
        "grafico_rede", "grafico_calendario", "mapa_de_calor", "medidor",
        "grafico_bala", "mini_grafico"]),
    ("Estado, cache e conexões", [
        "estado", "geral", "cache", "recurso", "conexao", "conexao_de",
        "conexoes", "fechar_conexoes", "segredos", "segredo",
        "segredos_mascarados"]),
    ("Navegação", [
        "navegar", "parar", "recarregar", "caminho", "parametros",
        "parametro", "menu"]),
    ("Segurança", [
        "autenticacao", "entrar", "sair", "usuario", "autenticado",
        "pode", "exigir_login", "exigir_permissao"]),
    ("Operação", [
        "registrar", "logs", "metricas", "saude", "plugin", "antes",
        "depois", "sessoes", "encerrar_sessao", "sessoes_em_banco",
        "sessoes_em_arquivos", "tarefa", "agendar",
        "atualizar_a_cada"]),
    ("Exportar e aparência", [
        "exportar_csv", "exportar_json", "exportar_svg", "exportar_excel",
        "html_da_pagina", "markdown_para_html", "tema", "temas",
        "seletor_de_tema"]),
    ("Validação e idioma", [
        "validar", "campo_validado", "i18n", "t", "traduzir"]),
    ("Componentes próprios", ["componente", "usar", "componentes"]),
    ("Testes", ["testar", "pedir"]),
]

#: O que cada simbolo faz, em uma linha. A docstring do Python e escrita
#: para quem le o runtime; isto e para quem escreve DataForge.
RESUMOS = {
    "app": "Cria a aplicação e passa a ser a atual.",
    "configurar": "Ajusta uma opção, ou várias por vault.",
    "configurar_pagina": "Título e ícone **só desta** página.",
    "pagina": "Registra uma página. Também serve de decorador.",
    "paginas": "As páginas registradas, para montar um menu.",
    "rodar": "Sobe a aplicação. Com uma ação, ela vira a página de `/`.",
    "subir": "Sobe e bloqueia. `recarregar := yes` reinicia ao salvar.",
    "servir": "Sobe em segundo plano e devolve a porta. Para testes.",
    "parar_servidor": "Desliga o servidor.",
    "montar": "O app Kiln por baixo — para acrescentar rota ou middleware.",
    "modo_servidor": "`yes` quando quem chamou quer o servidor **no ar** — "
                     "é o que faz o mesmo arquivo servir com `dataforge "
                     "vitrine dev` e ser testável com `dataforge run`.",

    "titulo": "O título da página, com ícone opcional.",
    "subtitulo": "Um subtítulo.",
    "cabecalho": "Um cabeçalho de seção, do nível 1 ao 6.",
    "texto": "Um parágrafo. Vários argumentos viram uma linha, como o `out`.",
    "markdown": "Títulos, listas, tabela, ênfase, código e link.",
    "codigo": "Um bloco de código, com a linguagem.",
    "html": "HTML **cru, sem escapar**. Nunca com o que veio do usuário.",
    "divisor": "Uma linha horizontal.",
    "espaco": "Espaço vertical em pixels.",

    "botao": "Devolve `yes` no ciclo em que foi clicado, `no` nos outros.",
    "entrada": "Campo de texto. Devolve o que está digitado.",
    "area_de_texto": "Campo de várias linhas.",
    "numero": "Campo numérico, com mínimo, máximo e passo.",
    "deslizante": "Escolher um número numa faixa.",
    "caixa": "Uma caixa de marcar. Devolve `yes`/`no`.",
    "interruptor": "O mesmo, com cara de chave.",
    "opcao": "Uma de poucas, em botões de rádio.",
    "escolha": "Uma de muitas, em lista suspensa.",
    "escolhas": "Várias de muitas. Devolve um cluster.",
    "data": "Um seletor de data. Devolve `\"2026-03-14\"`.",
    "cor": "Um seletor de cor. Devolve `\"#FED403\"`.",
    "arquivo": "Envio de arquivo. Devolve `void` até alguém mandar um.",

    "tabela": "Uma tabela estática. Aceita cluster de vaults, Frame ou matriz.",
    "frame": "Uma tabela com busca e ordenação, para explorar dado.",
    "metrica": "Um número grande, com a variação ao lado.",
    "json": "Um vault ou cluster, formatado e recolhível.",
    "vault": "Um vault como lista de chave e valor.",

    "sucesso": "Uma mensagem verde.",
    "erro": "Uma mensagem vermelha.",
    "aviso": "Uma mensagem amarela.",
    "informacao": "Uma mensagem azul.",
    "progresso": "Barra de 0 a 1.",
    "carregando": "Um giro com uma mensagem.",
    "imagem": "Uma imagem, com legenda.",
    "audio": "Um tocador de áudio.",
    "video": "Um tocador de vídeo.",
    "link": "Um link, opcionalmente em nova aba.",
    "baixar": "Um botão que entrega um arquivo ao visitante.",

    "colunas": "Divide em colunas. Devolve um cluster de áreas.",
    "linha": "Container horizontal — os filhos ficam lado a lado.",
    "container": "Um agrupamento, com borda e altura opcionais.",
    "cartao": "Uma caixa com título e subtítulo.",
    "expandir": "Uma seção que abre e fecha; o estado sobrevive.",
    "abas": "Abas. **Todas** são montadas; só a escolhida aparece.",
    "formulario": "Agrupa campos que só valem no envio.",
    "vazio": "Um espaço reservado para ser preenchido depois.",
    "lateral": "A barra lateral. Sempre a mesma, chamada de onde for.",
    "espacador": "Empurra o que vem depois para a outra ponta de uma `linha`.",

    "grafico": "Começa a montar um gráfico. Nada aparece até `desenhar`.",
    "desenhar": "Põe o gráfico montado na página.",
    "grafico_linha": "Linha, a forma curta.",
    "grafico_barras": "Barras verticais.",
    "grafico_barras_h": "Barras horizontais, para categorias de nome longo.",
    "grafico_area": "Linha com a área preenchida.",
    "grafico_dispersao": "Pontos.",
    "grafico_pizza": "Fatias, com o percentual escrito.",
    "grafico_rosca": "O mesmo, com o miolo vazado.",
    "histograma": "Distribuição: conta quantos valores caem em cada faixa.",
    "paleta": "As dez cores padrão, como cluster.",

    "estado": "O estado da sessão: `obter`, `definir`, `padrao`, `somar`…",
    "geral": "O estado do processo — **todas** as sessões veem o mesmo.",
    "cache": "`mark @V.cache` sobre uma ação, e ela para de recalcular.",

    "navegar": "Vai para outra página. Interrompe o programa aqui.",
    "parar": "Acaba a página neste ponto, sem erro.",
    "recarregar": "Roda de novo, do começo, jogando fora o que foi montado.",
    "caminho": "Onde a página está.",
    "parametros": "Os da rota e os da query, juntos.",
    "parametro": "Um deles, com padrão.",
    "menu": "Desenha o menu das páginas registradas na barra lateral.",

    "autenticacao": "Registra a ação que confere usuário e senha.",
    "entrar": "Tenta entrar. Devolve o vault do usuário, ou `void`.",
    "sair": "Derruba a sessão de quem está logado.",
    "usuario": "Quem está logado, ou `void`.",
    "autenticado": "`yes`/`no`.",
    "pode": "Se o papel de quem está logado tem a permissão.",
    "exigir_login": "A barreira: desenha a entrada e para a página.",
    "exigir_permissao": "O mesmo, e ainda cobra a permissão.",

    "registrar": "Escreve no log da aplicação.",
    "logs": "As últimas linhas, filtráveis por nível.",
    "metricas": "Execuções, erros, média em ms, sessões e cache.",
    "saude": "O que um balanceador pergunta antes de mandar tráfego.",
    "plugin": "Instala um plugin. O mesmo nome duas vezes é erro.",
    "antes": "Middleware que roda antes de toda página; `no` interrompe.",
    "depois": "Middleware de saída, com o contexto já montado.",
    "sessoes": "Quantas sessões estão vivas.",
    "encerrar_sessao": "Descarta a sessão de agora.",
    "sessoes_em_banco": "As sessões num SQLite que vários processos abrem (`sessoes_em := …`).",
    "sessoes_em_arquivos": "As sessões num JSON por sessão, numa pasta que os processos dividem.",
    "tarefa": "Roda numa thread e devolve na hora. A página não espera.",
    "agendar": "Roda de tempos em tempos, enquanto o processo viver.",
    "atualizar_a_cada": "A página se recarrega sozinha nesse intervalo.",

    "exportar_csv": "Um botão que entrega os dados como CSV.",
    "exportar_json": "O mesmo, em JSON.",
    "html_da_pagina": "A página atual como HTML.",
    "markdown_para_html": "Converte Markdown sem pôr nada na página.",

    "validar": "Confere um valor e desenha o erro **sob o campo**.",
    "campo_validado": "Um campo com a regra junto. Devolve `(valor, bom)`.",
    "i18n": "Tradução: `carregar`, `idioma`, `traduzir`, `seletor`.",
    "t": "O texto de uma chave, no idioma da sessão. Atalho de `traduzir`.",
    "traduzir": "O mesmo que `t`, pelo nome inteiro.",
    "componente": "Registra um componente reaproveitável, pelo nome.",
    "usar": "Chama um componente registrado.",
    "componentes": "Os nomes registrados.",

    "testar": "Uma sonda: clica, digita e pergunta, sem navegador.",
    "pedir": "Um pedido HTTP de verdade contra a aplicação, sem socket.",

    # ── o que veio com o painel profissional ──
    "escrever": "Mostra o que vier, escolhendo o componente **pelo valor**.",
    "legenda": "Texto pequeno e discreto — a nota sob um gráfico.",
    "citacao": "Um bloco citado, com autor opcional.",
    "selo": "Uma etiqueta curta, na cor do tema.",
    "selos": "Vários selos numa linha só.",
    "formula": "Fração, potência, índice e as letras gregas.",
    "ajuda": "A assinatura e a documentação de uma ação, na página.",
    "fluxo": "Consome um gerador de texto e mostra o resultado.",
    "icone": "Um dos 48 ícones desenhados no módulo.",
    "icones": "Os nomes de todos os ícones.",

    "hora": "Um horário. Devolve `\"14:30\"`.",
    "periodo": "Duas datas. Devolve `[inicio, fim]`, já em ordem.",
    "faixa": "Dois cursores na mesma trilha. Devolve `[menor, maior]`.",
    "deslizante_opcoes": "Um cursor sobre rótulos. Devolve o rótulo.",
    "pilulas": "Botões arredondados, um ou vários. O filtro que fica visível.",
    "segmentado": "Um grupo colado, com um segmento aceso.",
    "avaliacao": "Estrelas, corações ou polegares. Devolve `0` sem nota.",
    "tags": "Etiquetas que se acrescenta digitando. Devolve um cluster.",
    "autocompletar": "Campo de texto com sugestões — que **não** restringem.",
    "senha": "`V.entrada` com o tipo senha.",
    "busca": "`V.entrada` com o tipo busca.",
    "email": "`V.entrada` com o tipo e-mail.",
    "camera": "Tira uma foto pela câmera. Exige HTTPS e permissão.",
    "mudou": "`yes` quando o campo dessa chave chegou diferente agora.",
    "mudancas": "As chaves que mudaram nesta execução.",

    "grade": "A tabela de trabalho: pagina, ordena e filtra **no servidor**.",
    "editor": "Uma tabela que se edita na tela. Devolve as linhas novas.",
    "coluna": "A configuração de uma coluna da grade, como vault.",
    "regra": "Uma regra de formatação condicional para a grade.",
    "indicador": "O cartão de um número: faixa de cor, nota, meta e série.",
    "indicadores": "Vários indicadores numa faixa que se ajusta à largura.",
    "estatisticas": "Contagem, ausências, média, desvio, quartis.",
    "formatar": "Aplica um formato conhecido pelo nome.",
    "moeda": "`1091947.91` vira `R$ 1.091.947,91`.",
    "numero_br": "Separador de milhar e vírgula decimal.",
    "percentual": "`12.5` vira `12,5%`.",
    "compacto": "`1234567` vira `1,2 mi`.",
    "data_br": "`2026-09-20` vira `20/09/2026`.",

    "pdf": "Mostra um PDF na própria página.",
    "iframe": "Incorpora outra página, em `sandbox`.",
    "logo": "A marca, no alto da barra lateral.",
    "galeria": "Várias imagens numa grade.",
    "toast": "Um aviso flutuante, que aparece e some sozinho.",
    "esqueleto": "O contorno cinza do que ainda não chegou.",
    "comemorar": "Balões, neve ou confete, por alguns segundos.",
    "excecao": "Um erro desenhado como erro: tipo, mensagem e rastro.",
    "status": "Uma caixa com estado, que se escreve por dentro.",
    "chat": "A área de uma conversa.",
    "chat_mensagem": "Uma bolha. Devolve a área, para escrever dentro.",
    "chat_entrada": "A caixa de escrever. Devolve o texto enviado, ou `void`.",
    "historico_de_chat": "A lista de mensagens guardada na sessão.",
    "guardar_no_chat": "Acrescenta ao histórico e devolve a lista inteira.",

    "malha": "Uma grade que se reorganiza pela **largura**, não pelo número.",
    "painel": "O bloco de painel: faixa de cor, título discreto, conteúdo.",
    "barra_superior": "Marca, navegação e o canto dos filtros.",
    "dialogo": "Uma janela por cima da página. O estado é de quem escreve.",
    "popover": "Um botão que abre um cartãozinho.",
    "passos": "A trilha de um processo, com o passo aceso.",
    "separador": "Uma linha com um rótulo no meio.",
    "rolagem": "Uma caixa com rolagem própria, de altura fixa.",
    "fragmento": "Um pedaço que se redesenha **sozinho**, sem a página junto.",
    "fragmentos": "As chaves dos fragmentos montados nesta execução.",

    "tipos_de_grafico": "Os nomes de todos os tipos, como cluster.",
    "grafico_combo": "Barras e linhas juntas, com **duas** escalas.",
    "grafico_barras_100": "Barras em que cada categoria soma 100%.",
    "grafico_area_empilhada": "Áreas somadas: o todo e as partes.",
    "grafico_funil": "Quanto sobra em cada etapa, com as duas conversões.",
    "grafico_treemap": "Retângulos proporcionais, para itens demais.",
    "grafico_cascata": "De onde veio a diferença entre o começo e o fim.",
    "grafico_pareto": "Barras em ordem, com a curva do acumulado.",
    "grafico_radar": "Eixos saindo do centro — vale até umas oito pontas.",
    "grafico_caixa": "Mediana, quartis e os pontos fora da curva.",
    "grafico_bolhas": "Três grandezas: posição, posição e **área**.",
    "grafico_dispersao_xy": "Dispersão com o eixo x numérico, e a tendência.",
    "grafico_velas": "Abertura, máxima, mínima e fechamento.",
    "grafico_sankey": "Para onde o dinheiro (ou o usuário) foi.",
    "grafico_gantt": "Barras no tempo — o cronograma.",
    "grafico_mapa": "Pontos por latitude e longitude. **Sem** mapa por baixo.",
    "grafico_rede": "Nós e arestas, dispostos em círculo.",
    "grafico_calendario": "Um ano em quadradinhos, uma semana por coluna.",
    "mapa_de_calor": "Uma matriz colorida: hora × dia, produto × região.",
    "medidor": "Um ponteiro numa escala, com faixas coloridas.",
    "grafico_bala": "O valor, a meta e as faixas numa linha só.",
    "mini_grafico": "Uma série miúda, do tamanho de uma linha de texto.",

    "recurso": "`mark @V.recurso` guarda o **objeto** — conexão, modelo.",
    "conexao": "Abre (ou devolve) uma conexão do processo, com cache.",
    "conexao_de": "Registra uma conexão que **você** abriu.",
    "conexoes": "Os nomes das conexões vivas.",
    "fechar_conexoes": "Fecha todas. Devolve quantas eram.",
    "segredos": "Todos os segredos, como vault.",
    "segredo": "Um segredo. O **ambiente vence o arquivo**.",
    "segredos_mascarados": "As chaves, com o valor escondido.",

    "exportar_svg": "O gráfico como arquivo SVG — o mesmo que a página desenha.",
    "exportar_excel": "Uma planilha `.xlsx` de verdade, sem dependência.",
    "tema": "Lê ou troca o tema e a densidade da aplicação.",
    "temas": "Os seis temas prontos.",
    "seletor_de_tema": "Desenha a troca de tema e devolve o escolhido.",
}


def assinatura(valor):
    """A assinatura como quem escreve DataForge a chama."""
    if not callable(valor):
        return ""
    try:
        texto = str(inspect.signature(valor))
    except (TypeError, ValueError):
        return "(…)"
    return texto.replace("**kw", "…").replace("**pares", "…")


def conferir_cobertura(modulo):
    """Recusa gerar uma referencia que mente.

    Um simbolo fora da pagina e trabalho que ninguem encontra; um
    listado que nao existe e uma promessa quebrada na primeira tentativa
    de quem le.
    """
    listados = {n for _, nomes in GRUPOS for n in nomes}
    reais = {n for n in modulo if n != "__name__"}
    faltando = reais - listados
    if faltando:
        raise SystemExit(
            f"simbolos da Vitrine fora da referencia: {sorted(faltando)}\n"
            f"acrescente cada um a GRUPOS e a RESUMOS em "
            f"tools/gerar_ref_vitrine.py")
    inventados = listados - reais
    if inventados:
        raise SystemExit(f"a referencia lista o que nao existe: "
                         f"{sorted(inventados)}")
    sem_resumo = reais - set(RESUMOS)
    if sem_resumo:
        raise SystemExit(f"sem resumo em RESUMOS: {sorted(sem_resumo)}")


def construir():
    modulo = get_module("Arcane.Vitrine")
    conferir_cobertura(modulo)
    total = len(modulo) - 1

    blocos = [
        {"p": "Esta página é gerada a partir de "
              "`dataforge/stdlib/vitrine/`. São **"
              f"{total} símbolos**, e o gerador recusa rodar se algum "
              "deles ficar de fora."},
        {"p": "Em todos os exemplos, `V` é o apelido de "
              "`adopt Arcane.Vitrine as V`."},
        {"callout": {"tipo": "dica", "titulo": "Toda área tem os mesmos componentes",
                     "texto": "Os grupos **Texto**, **Entrada**, **Dados**, "
                              "**Retorno** e **Gráficos** também são métodos de "
                              "qualquer área de layout — `coluna.metrica(…)`, "
                              "`aba.frame(…)`, `lateral.escolha(…)`. Aprender "
                              "um lugar ensina todos."}},
    ]

    for titulo, nomes in GRUPOS:
        blocos.append({"h2": titulo})
        linhas = []
        for nome in nomes:
            chamada = f"`V.{nome}{assinatura(modulo[nome])}`"
            linhas.append([chamada, RESUMOS[nome]])
        blocos.append({"table": {"head": ["Símbolo", "Faz"], "rows": linhas}})

    blocos.append({"h2": "Os métodos da sonda"})
    blocos.append({"p": "O que `V.testar(pagina)` devolve — ver "
                        "[Testar sem navegador](/docs/vitrine/testes)."})
    blocos.append({"table": {"head": ["Método", "Faz"], "rows": [
        ["`t.clicar(rótulo)`", "clica num botão e roda a página de novo"],
        ["`t.digitar(rótulo, valor)`", "preenche um campo"],
        ["`t.marcar(rótulo, ligado)`", "liga uma caixa ou interruptor"],
        ["`t.selecionar(rótulo, valor)`", "escolhe numa lista"],
        ["`t.abrir_aba(rótulo)`", "troca de aba"],
        ["`t.enviar(formulário)`", "aperta o botão de envio"],
        ["`t.enviar_arquivo(rótulo, nome, conteúdo)`", "simula um upload"],
        ["`t.ir_para(caminho)`", "vai para outra página"],
        ["`t.rodar()`", "roda de novo, sem interação"],
        ["`t.texto()`", "a página como texto corrido"],
        ["`t.achar(tipo)` · `t.primeiro(tipo)`", "os nós de um tipo"],
        ["`t.quantos(tipo)` · `t.existe(tipo, rótulo)`", "contar e conferir"],
        ["`t.metrica(rótulo)` · `t.valor(rótulo)`", "o que a tela mostra"],
        ["`t.alertas(nível)`", "as mensagens de sucesso, erro, aviso"],
        ["`t.estado(chave)`", "o estado da sessão"],
        ["`t.falhou()` · `t.falhas()`", "se algo disparou, e o quê"],
        ["`t.html()` · `t.arvore()`", "a página como HTML, ou como vault"],
    ]}})

    blocos.append({"h2": "As rotas que vêm prontas"})
    blocos.append({"table": {"head": ["Rota", "Devolve"], "rows": [
        ["`GET /__vitrine__/saude`", "estado, tempo no ar, sessões"],
        ["`GET /__vitrine__/metricas`", "execuções, erros, média em ms, cache"],
        ["`POST /__vitrine__/acao`", "o miolo da página, após uma interação"],
        ["`GET /__vitrine__/baixar/:chave`", "o arquivo de um `V.baixar`"],
        ["`GET /__vitrine__/manifesto.json`", "o manifesto PWA, se ligado"],
    ]}})

    corpo = json.dumps(blocos, ensure_ascii=False, indent=2)

    def slug(texto):
        texto = unicodedata.normalize("NFD", texto)
        texto = "".join(c for c in texto
                        if unicodedata.category(c) != "Mn")
        return re.sub(r"[^a-z0-9\s-]", "",
                      texto.lower()).strip().replace(" ", "-")

    titulos = [b["h2"] for b in blocos if "h2" in b]
    cabecalhos = ", ".join(
        "{ id: '%s', text: %s, level: 2 as const }"
        % (slug(t), json.dumps(t, ensure_ascii=False)) for t in titulos)

    descricao = (f"Os {total} símbolos do módulo, agrupados por assunto, "
                 f"com a assinatura extraída do código-fonte.")

    return f'''import type {{ Metadata }} from 'next';
import type {{ Bloco }} from '@/lib/content';
import {{ DocPage }} from '@/components/Doc';
import {{ Renderer }} from '@/components/Renderer';

// Gerado por tools/gerar_ref_vitrine.py — não edite à mão.

export const metadata: Metadata = {{
  title: "Referência da Vitrine",
  description: {json.dumps(descricao, ensure_ascii=False)},
}};

const blocos: Bloco[] = {corpo};

const headings = [{cabecalhos}];

export default function Page() {{
  return (
    <DocPage
      title="Referência da Vitrine"
      description={json.dumps(descricao, ensure_ascii=False)}
      href="/docs/vitrine/referencia"
      headings={{headings}}
    >
      <Renderer blocos={{blocos}} />
    </DocPage>
  );
}}
'''


def main():
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write(construir())
    modulo = get_module("Arcane.Vitrine")
    print(f"referencia gerada: {os.path.relpath(DESTINO, RAIZ)}")
    print(f"  {len(modulo) - 1} simbolos em {len(GRUPOS)} grupos")


if __name__ == "__main__":
    main()
