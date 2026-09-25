// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "17 · Tempo e sistema",
  description: "6 exercícios: datas, durações, ambiente e processos.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **A linguagem a fundo** · datas, durações, ambiente e processos · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 17`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[158](#158-datas-e-horas)", "**Datas e horas**", "crie, formate e compare datas com Arcane.Time."], ["[159](#159-aritmetica-com-datas)", "**Aritmetica com datas**", "some e subtraia periodos, e calcule diferencas."], ["[160](#160-cronometragem-e-desempenho)", "**Cronometragem e desempenho**", "meca quanto tempo o codigo leva."], ["[161](#161-sistema-e-ambiente)", "**Sistema e ambiente**", "consulte o sistema operacional e as variaveis de ambiente."], ["[162](#162-executando-processos)", "**Executando processos**", "rode comandos externos e trate a saida."], ["[163](#163-registro-de-eventos)", "**Registro de eventos**", "registre o que acontece com niveis, campos e destino em arquivo."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "158 · Datas e horas"},
  {"p": "**Enunciado.** crie, formate e compare datas com Arcane.Time."},
  { code: `adopt Arcane.Time as Time

// Construir datas
natal := Time.date(2026, 12, 25)
reuniao := Time.datetime(2026, 3, 15, 14, 30, 0)

out Time.to_date_string(natal)
out Time.to_br(reuniao)
out Time.to_iso(natal)

assert Time.to_date_string(natal) is "25/12/2026", "formato brasileiro"
assert Time.year(natal) is 2026, "ano"
assert Time.month(natal) is 12, "mes"
assert Time.day(natal) is 25, "dia"
assert Time.hour(reuniao) is 14, "hora"

// Componentes com nome
out $"{Time.to_date_string(natal)} cai numa {Time.weekday_name(natal)}"
out $"mes: {Time.month_name(natal)}"
assert Time.weekday_name(natal) is "sexta-feira", "25/12/2026 e sexta"
assert Time.month_name(natal) is "dezembro", "nome do mes"
assert Time.month_name(natal, yes) is "dez", "nome curto"

// Formato livre
out Time.format(reuniao, "%d/%m/%Y as %H:%M")
assert Time.format(natal, "%Y-%m-%d") is "2026-12-25", "formato personalizado"

// Interpretar texto
lida := Time.parse("2026-06-15")
out Time.to_date_string(lida)
assert Time.month(lida) is 6, "parse ISO"
assert Time.day(Time.parse("01/02/2026")) is 1, "parse brasileiro"

// Comparar
assert Time.is_before(reuniao, natal) is yes, "marco vem antes de dezembro"
assert Time.is_after(natal, reuniao) is yes, "dezembro vem depois"
assert Time.is_weekend(Time.date(2026, 12, 26)) is yes, "26/12/2026 e sabado"
assert Time.is_leap_year(2024) is yes, "2024 e bissexto"
assert Time.is_leap_year(2026) is no, "2026 nao e"

// Semana, trimestre e dia do ano
out $"trimestre: {Time.quarter(natal)}  dia do ano: {Time.day_of_year(natal)}"
assert Time.quarter(natal) is 4, "dezembro e do quarto trimestre"`, lang: 'df', title: `exercicios/17-tempo-e-sistema/158_datas_basico.df` },
  {"h3": "Conceitos"},
  {"p": "`Arcane.Time` trabalha com datas como vaults marcados com `__type__: \"DateTime\"`. Isso as faz circular pelo runtime como qualquer valor — dá para guardar numa lista, passar por pipeline, serializar."},
  {"p": "**Construir**"},
  { code: `Time.now()                        // agora, com hora
Time.today()                      // hoje à meia-noite
Time.date(2026, 12, 25)           // uma data
Time.datetime(2026, 3, 15, 14, 30, 0)
Time.from_timestamp(1767000000)
Time.parse("2026-06-15")          // interpreta vários formatos`, lang: 'df' },
  {"p": "`parse` tenta ISO, brasileiro e as variantes com hora — sem você precisar dizer qual é."},
  {"p": "**Formatar**"},
  {"table": {"head": ["Chamada", "Resultado"], "rows": [["`to_date_string(d)`", "`25/12/2026`"], ["`to_time_string(d)`", "`14:30:00`"], ["`to_br(d)`", "`25/12/2026 14:30:00`"], ["`to_iso(d)`", "`2026-12-25T00:00:00`"], ["`format(d, \"%d/%m\")`", "livre, com códigos strftime"]]}},
  {"p": "**Componentes**"},
  { code: `Time.year(d)  Time.month(d)  Time.day(d)
Time.hour(d)  Time.minute(d)  Time.second(d)
Time.weekday(d)          // 0 = segunda
Time.weekday_name(d)     // "sexta-feira"
Time.month_name(d)       // "dezembro"
Time.quarter(d)          // 1..4
Time.day_of_year(d)      // 1..366
Time.week_of_year(d)`, lang: 'df' },
  {"p": "Os nomes vêm **em português** — é a língua do módulo, e evita ter que traduzir `\"Friday\"` em cada relatório."},
  {"h3": "Comparação"},
  { code: `Time.is_before(a, b)
Time.is_after(a, b)
Time.is_same_day(a, b)
Time.is_weekend(d)
Time.is_leap_year(2024)`, lang: 'df' },
  {"p": "`is_same_day` existe porque comparar dois `DateTime` diretamente compararia também a hora — duas coisas no mesmo dia, mas às 9h e às 15h, não são iguais."},
  {"h3": "Saída esperada"},
  { code: `25/12/2026
15/03/2026 14:30:00
2026-12-25T00:00:00
25/12/2026 cai numa sexta-feira
mes: dezembro
15/03/2026 as 14:30
15/06/2026
trimestre: 4  dia do ano: 359`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Descubra em que dia da semana você nasceu.", "Liste todas as sextas-feiras 13 de um ano."]},
  {"h2": "159 · Aritmetica com datas"},
  {"p": "**Enunciado.** some e subtraia periodos, e calcule diferencas."},
  { code: `adopt Arcane.Time as Time

base := Time.date(2026, 1, 31)
out $"base: {Time.to_date_string(base)}"

// Somar periodos
out $"+10 dias:   {Time.to_date_string(Time.add_days(base, 10))}"
out $"+2 semanas: {Time.to_date_string(Time.add_weeks(base, 2))}"
out $"+1 mes:     {Time.to_date_string(Time.add_months(base, 1))}"
out $"+1 ano:     {Time.to_date_string(Time.add_years(base, 1))}"

assert Time.day(Time.add_days(base, 1)) is 1, "31/01 + 1 dia = 01/02"
assert Time.month(Time.add_days(base, 1)) is 2, "virou fevereiro"

// add_months ajusta o dia quando o mes e mais curto
fevereiro := Time.add_months(base, 1)
out $"31/01 + 1 mes = {Time.to_date_string(fevereiro)}"
assert Time.day(fevereiro) is 28, "fevereiro de 2026 tem 28 dias"

// Subtrair e somar negativo
assert Time.day(Time.add_days(base, -1)) is 30, "31/01 - 1 dia = 30/01"

// Diferenca entre datas
inicio := Time.date(2026, 1, 1)
fim := Time.date(2026, 12, 31)
d := Time.diff(inicio, fim)

out ""
out $"de 01/01 a 31/12: {d.days} dias"
out $"em horas: {d.total_hours}"
out $"legivel: {d.human}"
assert d.days is 364, "2026 nao e bissexto"
assert Time.days_between(inicio, fim) is 364, "days_between"

// Duracao construida a mao
duracao := Time.duration(1, 2, 30, 0)
out ""
out $"1 dia, 2h30: {duracao.human} = {duracao.total_seconds} segundos"
assert duracao.total_hours is 26.5, "1 dia + 2.5 horas"

// Humanizar segundos
cycle s in [45, 90, 3725, 90000]:
    out $"  {s}s -> {Time.humanize(s)}"
assert Time.humanize(3725) is "1h 2min", "uma hora e dois minutos"

// Idade
out ""
out $"quem nasceu em 20/05/1990 tem {Time.age(Time.date(1990, 5, 20))} anos"

// Limites do dia e do mes
out ""
out $"inicio do mes: {Time.to_date_string(Time.start_of_month(base))}"
out $"fim do mes:    {Time.to_date_string(Time.end_of_month(base))}"
assert Time.day(Time.start_of_month(base)) is 1, "primeiro dia"
assert Time.day(Time.end_of_month(base)) is 31, "janeiro tem 31"
assert Time.days_in_month(2024, 2) is 29, "fevereiro bissexto"`, lang: 'df', title: `exercicios/17-tempo-e-sistema/159_datas_aritmetica.df` },
  {"h3": "Somar períodos"},
  { code: `Time.add_days(d, 10)
Time.add_weeks(d, 2)
Time.add_months(d, 1)
Time.add_years(d, 1)
Time.add_hours(d, 3)
Time.add_minutes(d, 45)`, lang: 'df' },
  {"p": "Todas devolvem uma **data nova** — a original não muda. Para subtrair, passe um número negativo."},
  {"h3": "O caso difícil: `add_months`"},
  {"p": "O que é \"31 de janeiro mais um mês\"? Não existe 31 de fevereiro."},
  { code: `Time.add_months(Time.date(2026, 1, 31), 1)     // 28/02/2026`, lang: 'df' },
  {"p": "A regra adotada é **grampear no último dia válido** do mês de destino. É o que Java (`java.time`), C# e a maioria das bibliotecas fazem."},
  {"p": "Consequência a ter em mente: a operação **não é reversível**. Somar um mês e subtrair um mês pode não voltar ao dia original (31/01 → 28/02 → 28/01). Se a reversibilidade importa, trabalhe em dias."},
  {"h3": "Diferenças"},
  { code: `d := Time.diff(inicio, fim)`, lang: 'df' },
  {"p": "O resultado é uma **Duration** com vários formatos prontos:"},
  {"table": {"head": ["Campo", "Exemplo"], "rows": [["`d.days`", "`364`"], ["`d.total_hours`", "`8736.0`"], ["`d.total_seconds`", "`31449600.0`"], ["`d.human`", "`\"364d 0h\"`"]]}},
  {"p": "Ter todos calculados evita a conta de conversão espalhada pelo código."},
  {"h3": "Humanizar"},
  { code: `Time.humanize(45)       // "45s"
Time.humanize(90)       // "1min 30s"
Time.humanize(3725)     // "1h 2min"
Time.humanize(90000)    // "1d 1h"`, lang: 'df' },
  {"p": "A função escolhe a unidade sozinha — é o que você quer numa interface, onde \"31449600 segundos\" não diz nada a ninguém."},
  {"h3": "Limites de período"},
  { code: `Time.start_of_day(d)     Time.end_of_day(d)
Time.start_of_month(d)   Time.end_of_month(d)
Time.days_in_month(2024, 2)     // 29`, lang: 'df' },
  {"p": "`start_of_day` e `end_of_day` são o que você usa para filtrar \"tudo de hoje\" numa consulta — sem eles, comparar com `Time.today()` deixa de fora tudo que aconteceu depois da meia-noite."},
  {"h3": "Saída esperada"},
  { code: `base: 31/01/2026
+10 dias:   10/02/2026
+2 semanas: 14/02/2026
+1 mes:     28/02/2026
+1 ano:     31/01/2027
31/01 + 1 mes = 28/02/2026
de 01/01 a 31/12: 364 dias
...
1 dia, 2h30: 1d 2h = 95400.0 segundos`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Calcule quantos dias úteis há entre duas datas (pule `is_weekend`).", "Gere as datas de vencimento de 12 parcelas mensais."]},
  {"h2": "160 · Cronometragem e desempenho"},
  {"p": "**Enunciado.** meca quanto tempo o codigo leva."},
  { code: `adopt Arcane.Time as Time

// measure roda a acao e devolve resultado + tempo
action trabalho_pesado():
    total := 0
    cycle i from 1 to 200000:
        total += i
    yield total

medida := Time.measure(trabalho_pesado)
out $"resultado: {medida.result}"
out $"levou: {round(medida.ms, 2)} ms"
assert medida.result is 20000100000, "soma de 1 a 200000"
assert medida.ms bigger 0, "tempo positivo"

// Cronometro com controle manual
crono := Time.stopwatch()
crono.start()

soma := 0
cycle i from 1 to 50000:
    soma += i * 2

parcial := crono.elapsed_ms()
out ""
out $"parcial: {round(parcial, 2)} ms"

cycle i from 1 to 50000:
    soma += i

crono.stop()
out $"total:   {round(crono.elapsed_ms(), 2)} ms"
assert crono.elapsed_ms() bigger_eq parcial, "o total inclui a parcial"

// Comparar duas implementacoes
action com_laco(n):
    total := 0
    cycle i from 1 to n:
        total += i
    yield total

action com_formula(n):
    yield n * (n + 1) ~/ 2

a := Time.measure(lambda: com_laco(100000))
b := Time.measure(lambda: com_formula(100000))

out ""
out $"laco:    {round(a.ms, 3)} ms -> {a.result}"
out $"formula: {round(b.ms, 3)} ms -> {b.result}"
assert a.result is b.result, "os dois chegam ao mesmo numero"
assert b.ms smaller a.ms, "a formula e mais rapida"

// Medir varias vezes e tirar a media
tempos := []
cycle _ in [1, 2, 3, 4, 5]:
    tempos.append(Time.measure(lambda: com_laco(20000)).ms)

out ""
out $"5 execucoes: media {round(mean(tempos), 3)} ms, minimo {round(min(tempos), 3)} ms"
assert len(tempos) is 5, "cinco medicoes"

// reset zera o cronometro
crono.reset()
assert crono.elapsed() is 0.0, "zerado"
out ""
out "cronometro zerado"`, lang: 'df', title: `exercicios/17-tempo-e-sistema/160_cronometro.df` },
  {"h3": "`measure` — a forma direta"},
  { code: `medida := Time.measure(trabalho_pesado)
out medida.result      // o que a ação devolveu
out medida.ms          // quanto levou, em milissegundos`, lang: 'df' },
  {"p": "Recebe uma ação sem argumentos e devolve resultado **e** tempo. Para medir algo com argumentos, envolva numa lambda:"},
  { code: `Time.measure(lambda: com_laco(100000))`, lang: 'df' },
  {"h3": "`stopwatch` — controle manual"},
  {"p": "Quando você precisa de tempos parciais:"},
  { code: `crono := Time.stopwatch()
crono.start()
// ... primeira parte
parcial := crono.elapsed_ms()
// ... segunda parte
crono.stop()
total := crono.elapsed_ms()`, lang: 'df' },
  {"table": {"head": ["Método", "Faz"], "rows": [["`start()`", "começa ou retoma"], ["`stop()`", "pausa e devolve o acumulado"], ["`elapsed()`", "segundos até agora"], ["`elapsed_ms()`", "milissegundos"], ["`reset()`", "zera"]]}},
  {"p": "`start` depois de `stop` **retoma** — o acumulado não se perde. Isso permite medir só as partes que interessam, ignorando o meio."},
  {"h3": "Medir para decidir"},
  { code: `action com_laco(n):
    total := 0
    cycle i from 1 to n:
        total += i
    yield total

action com_formula(n):
    yield n * (n + 1) ~/ 2`, lang: 'df' },
  {"p": "As duas dão o mesmo resultado. A segunda é O(1) contra O(n) da primeira, e o cronômetro mostra isso em números."},
  {"p": "Essa é a disciplina que vale levar: **meça antes de otimizar**. A intuição sobre o que é lento erra com frequência, e otimizar o lugar errado gasta tempo sem efeito."},
  {"h3": "Medir várias vezes"},
  { code: `tempos := []
cycle _ in [1, 2, 3, 4, 5]:
    tempos.append(Time.measure(lambda: com_laco(20000)).ms)

out $"media {mean(tempos)}, minimo {min(tempos)}"`, lang: 'df' },
  {"p": "Uma medição isolada é ruído: o sistema operacional interrompe, o cache esquenta. O **mínimo** costuma ser mais informativo que a média — é a execução em que menos coisa atrapalhou."},
  {"p": "Repare no `cycle _ in ...`: o `_` diz que o valor da iteração não interessa."},
  {"h3": "Saída esperada"},
  { code: `resultado: 20000100000
levou: 42.31 ms

parcial: 11.2 ms
total:   19.8 ms

laco:    21.4 ms -> 5000050000
formula: 0.002 ms -> 5000050000

5 execucoes: media 4.3 ms, minimo 4.1 ms

cronometro zerado`, lang: 'text' },
  {"p": "(os tempos variam a cada máquina)"},
  {"h3": "Experimente"},
  {"list": ["Compare busca linear com `Arcane.Collections.binary_search` numa lista grande.", "Meça um pipeline contra o laço equivalente.", "Use `stopwatch` para medir só a parte de I/O de um programa."]},
  {"h2": "161 · Sistema e ambiente"},
  {"p": "**Enunciado.** consulte o sistema operacional e as variaveis de ambiente."},
  { code: `adopt Arcane.OS as OS
adopt Arcane.Text as Text

out Text.box("Sistema")
out $"sistema:    {OS.name()} {OS.release()}"
out $"arquitetura: {OS.arch()} ({OS.machine()})"
out $"maquina:    {OS.hostname()}"
out $"CPUs:       {OS.cpu_count()}"
out $"usuario:    {OS.user()}"

assert len(OS.name()) bigger 0, "o sistema tem nome"
assert OS.cpu_count() bigger_eq 1, "ao menos uma CPU"

// Detectar a plataforma
plataforma := "Windows" given OS.is_windows() otherwise "macOS" given OS.is_mac() otherwise "Linux" given OS.is_linux() otherwise "outro"
out $"plataforma: {plataforma}"

// info() traz tudo de uma vez
dados := OS.info()
assert "system" in dados, "info tem o sistema"
assert "cpus" in dados, "info tem as CPUs"

// Disco
uso := OS.disk_usage(".")
out ""
out Text.box("Disco")
out $"total: {uso.total_gb} GB"
out $"livre: {uso.free_gb} GB ({100 - uso.percent_used}% disponivel)"
assert uso.total_gb bigger 0, "o disco tem tamanho"

// Diretorios
out ""
out Text.box("Caminhos")
out $"atual: {OS.cwd()}"
out $"casa:  {OS.home()}"
out $"temp:  {OS.temp_dir()}"
out $"separador: '{OS.separator()}'"

// Variaveis de ambiente
out ""
out Text.box("Ambiente")
// Quantas HA nao se imprime: o numero depende da maquina, e mudaria
// entre duas execucoes se algo definisse uma variavel no meio. O que
// se pode afirmar e que ha alguma.
assert len(OS.env_names()) bigger 0
out $"PATH existe? {OS.has_env("PATH")}"
out $"inexistente com padrao: {OS.get_env("VARIAVEL_QUE_NAO_EXISTE", "(padrao)")}"

assert OS.get_env("SEM_ISSO_AQUI", "fallback") is "fallback", "padrao ao faltar"
assert OS.has_env("VARIAVEL_INEXISTENTE_XYZ") is no, "nao existe"

// Definir, ler de volta — e DESFAZER
//
// O ambiente e do PROCESSO, e um processo roda mais de um programa:
// 'dataforge test' cria um interpretador por arquivo. Deixar a
// variavel definida polui a execucao seguinte, e foi assim que este
// exercicio imprimia 77 variaveis na primeira vez e 78 na segunda —
// pego pelo teste que compara a saida com a compilacao ligada e
// desligada.
antes := len(OS.env_names())

OS.set_env("DATAFORGE_TESTE", "42")
assert OS.get_env("DATAFORGE_TESTE") is "42", "definida e lida"
assert len(OS.env_names()) is antes + 1, "uma a mais"
out $"definida: DATAFORGE_TESTE = {OS.get_env("DATAFORGE_TESTE")}"

assert OS.unset_env("DATAFORGE_TESTE"), "devolve yes: ela existia"
assert not OS.has_env("DATAFORGE_TESTE"), "e agora nao existe"
assert len(OS.env_names()) is antes, "o ambiente voltou ao que era"

// Remover o que nao existe devolve 'no', e nao levanta: remover e
// pedir um estado final, e nesse ponto ja nao importa se estava la.
assert OS.unset_env("NUNCA_EXISTIU_ISSO_AQUI") is no

// Encontrar um programa
out ""
python := OS.which("python3")
out $"python3 em: {python ?? "(nao encontrado)"}"

// Terminal
tam := OS.terminal_size()
out $"terminal: {tam.columns}x{tam.lines}"
assert tam.columns bigger 0, "largura do terminal"`, lang: 'df', title: `exercicios/17-tempo-e-sistema/161_sistema_e_ambiente.df` },
  {"h3": "Conceitos"},
  {"p": "`Arcane.OS` é **somente leitura por padrão**. As duas exceções — `set_env` e `chdir` — estão marcadas como tal na documentação do módulo. Nada aqui apaga arquivo ou mata processo."},
  {"h3": "Identificar o sistema"},
  { code: `OS.name()          // "Darwin", "Linux", "Windows"
OS.release()       OS.version()
OS.arch()          // "64bit"
OS.machine()       // "arm64", "x86_64"
OS.hostname()
OS.cpu_count()
OS.user()`, lang: 'df' },
  {"p": "Para ramificar por plataforma, prefira os predicados:"},
  { code: `OS.is_windows()
OS.is_mac()
OS.is_linux()
OS.is_posix()`, lang: 'df' },
  {"p": "Eles são mais legíveis e mais robustos que comparar `OS.name()` com texto — `\"Darwin\"` para macOS não é óbvio para quem lê."},
  {"h3": "Ternário encadeado"},
  { code: `plataforma := "Windows" given OS.is_windows()
    otherwise "macOS" given OS.is_mac()
    otherwise "Linux" given OS.is_linux()
    otherwise "outro"`, lang: 'df' },
  {"p": "Cada `otherwise` abre o próximo teste. Funciona, mas com quatro ramos um `given`/ `orif` em bloco já lê melhor — o ternário rende mais em dois ou três casos."},
  {"h3": "Variáveis de ambiente"},
  { code: `OS.get_env("PATH")                       // void se não existir
OS.get_env("PORTA", "8080")              // com padrão
OS.has_env("HOME")
OS.env()                                 // todas, como vault
OS.set_env("MINHA_VAR", "valor")`, lang: 'df' },
  {"p": "O segundo argumento de `get_env` é o que torna configuração por ambiente utilizável:"},
  { code: `porta := cast OS.get_env("PORTA", "8080") as Integer`, lang: 'df' },
  {"p": "Sem ele, cada leitura precisaria de um `given` para o caso ausente."},
  {"p": "**Cuidado com segredos:** variáveis de ambiente costumam guardar senhas e chaves. `OS.env()` traz tudo — nunca despeje isso em log."},
  {"h3": "Disco"},
  { code: `uso := OS.disk_usage(".")
out uso.total_gb, uso.free_gb, uso.percent_used`, lang: 'df' },
  {"p": "Os campos em GB vêm arredondados, prontos para exibir; os campos em bytes (`total`, `free`) servem para conta."},
  {"h3": "`which`"},
  { code: `OS.which("python3")     // caminho, ou void`, lang: 'df' },
  {"p": "Devolve `void` quando não encontra — combine com `??` para um padrão:"},
  { code: `editor := OS.which("nvim") ?? OS.which("vim") ?? "nano"`, lang: 'df' },
  {"h3": "Saída esperada"},
  { code: `┌─────────┐
│ Sistema │
└─────────┘
sistema:    Darwin 25.3.0
arquitetura: 64bit (arm64)
CPUs:       10
plataforma: macOS
...`, lang: 'text' },
  {"p": "(os valores dependem da sua máquina)"},
  {"h3": "Experimente"},
  {"list": ["Escreva um relatório que muda de formato conforme `OS.terminal_size()`.", "Leia a configuração de variáveis de ambiente com padrões sensatos."]},
  {"h2": "162 · Executando processos"},
  {"p": "**Enunciado.** rode comandos externos e trate a saida."},
  { code: `adopt Arcane.Process as Proc
adopt Arcane.OS as OS

// ── O comando externo e onde o programa deixa de ser portatil ──
//
// 'echo' existe no Linux e no macOS como programa; no Windows ele e
// embutido do interpretador de comandos, e nao ha arquivo para rodar.
// 'cat' se chama 'more', e 'sleep' se chama 'timeout'.
//
// Por isso o primeiro passo de um programa que chama o sistema e
// decidir COM QUEM esta falando. O resto do exercicio e igual nos dois.

steady WINDOWS := OS.is_windows()
steady NL := char(10)

steady ECO := "cmd /c echo" given WINDOWS otherwise "echo"

// Comando que demora, para a demonstracao de tempo limite. O 'timeout'
// do Windows recusa entrada redirecionada e sai na hora; o 'ping' para
// o proprio computador espera de verdade nos dois sistemas.
steady DEMORA := "ping -n 6 127.0.0.1" given WINDOWS otherwise "sleep 5"

// run devolve stdout, stderr e o codigo de saida
r := Proc.run($"{ECO} ola do processo")
out $"saida:  {r.stdout.trim()}"
out $"codigo: {r.exit_code}"
out $"ok:     {r.ok}"

assert r.ok is yes, "o eco funciona"
assert r.exit_code is 0, "codigo zero"
assert r.stdout.trim() is "ola do processo", "a saida"

// capture pega so o stdout, ja limpo
out ""
out $"capture: '{Proc.capture($"{ECO} direto")}'"
assert Proc.capture($"{ECO} direto") is "direto", "capture"

// Comando inexistente nao derruba o programa
falhou := Proc.run("comando_que_nao_existe_xyz")
out ""
out $"inexistente -> codigo {falhou.exit_code}, ok={falhou.ok}"
assert falhou.ok is no, "falhou"
// 127 nos DOIS: a linguagem normaliza. O Windows levanta um erro do
// sistema em vez de devolver codigo, e 'Arcane.Process' traduz — quem
// escreve nao precisa saber de qual lado esta.
assert falhou.exit_code is 127, "o codigo de comando nao encontrado"

// check devolve so yes/no
out ""
out $"xyz existe?  {Proc.exists("comando_inexistente_xyz")}"
assert Proc.exists("comando_inexistente_xyz") is no, "o que nao existe"

// Argumentos com espacos: passe como lista, sem shell
//
// Sem lista, o espaco separaria em dois argumentos — e com um nome de
// arquivo vindo de fora, um espaco a mais vira uma falha de seguranca.
r2 := Proc.run([...ECO.split(" "), "texto com espacos"])
out ""
out $"lista: {r2.stdout.trim()}"

// A comparacao e por CONTEM, e nao por igual, de proposito: o 'cmd' do
// Windows reprocessa a linha e devolve as aspas junto com o texto. Isso
// nao enfraquece o teste — enfraqueceria se o argumento tivesse sido
// PARTIDO, e e exatamente isso que se esta cobrando. E e a melhor
// ilustracao de por que se passa lista: mesmo com lista, o que ha do
// outro lado ainda pode reinterpretar.
assert "texto com espacos" in r2.stdout, "a lista preserva o argumento"

// Enviar entrada para o processo
//
// 'sort' e um dos poucos que existe com o mesmo nome nos dois sistemas,
// e le da entrada padrao quando nao recebe arquivo.
r3 := Proc.run("sort", input_text := $"c{NL}a{NL}b{NL}")
ordenado := r3.lines >> morph l: l.trim() >> sift l: l isnt ""
out $"stdin ordenado: {ordenado}"
assert ordenado is ["a", "b", "c"], "a entrada padrao chegou e voltou ordenada"

// Encadear comandos: a saida de um vira a entrada do proximo
resultado := Proc.pipeline([$"{ECO} zebra", "sort"])
out ""
out $"pipeline: {resultado.stdout.trim()}"
assert resultado.stdout.trim() is "zebra", "a saida de um virou a entrada do outro"

// Tempo limite
lento := Proc.run(DEMORA, timeout := 1)
out ""
out $"com timeout: ok={lento.ok}"
assert lento.ok is no, "o comando estourou o tempo"`, lang: 'df', title: `exercicios/17-tempo-e-sistema/162_processos.df` },
  {"h3": "Segurança primeiro"},
  {"p": "Por padrão, `Arcane.Process` **não passa pelo shell**:"},
  { code: `Proc.run("echo ola")                    // sem shell
Proc.run(["echo", "texto com espacos"]) // lista: mais seguro ainda
Proc.run("...", shell := yes)           // shell, conscientemente`, lang: 'df' },
  {"p": "Sem shell, não há injeção: `rm -rf /` dentro de uma variável vira um argumento literal, não um comando. Só ligue `shell := yes` quando precisar de pipes, redirecionamentos ou expansão de `*` — e nunca com texto vindo do usuário."},
  {"h3": "O resultado"},
  {"p": "`run` sempre devolve um `ProcessResult`, mesmo quando falha:"},
  {"table": {"head": ["Campo", "Contém"], "rows": [["`stdout`", "a saída padrão"], ["`stderr`", "a saída de erro"], ["`exit_code`", "0 = sucesso"], ["`ok`", "`yes` se o código foi 0"], ["`failed`", "o oposto de `ok`"], ["`lines`", "`stdout` já separado em linhas"]]}},
  {"p": "Um comando inexistente devolve `exit_code` **127** em vez de derrubar o programa. Isso é deliberado: falha de processo externo é um resultado esperado, não uma exceção."},
  {"p": "E é 127 nos três sistemas. O Windows não devolve código nenhum nesse caso — ele levanta um erro de sistema —, e `Arcane.Process` traduz. Quem escreve não precisa saber de qual lado está."},
  { code: `r := Proc.run("comando_inexistente")
given r.failed:
    out $"nao rolou: {r.stderr}"`, lang: 'df' },
  {"h3": "Atalhos"},
  { code: `Proc.capture("echo x")     // só o stdout, sem a quebra final
Proc.check("test -f x")    // só yes/no
Proc.exit_code("cmd")      // só o número
Proc.exists("git")         // o programa está instalado?`, lang: 'df' },
  {"h3": "Enviar entrada"},
  { code: `Proc.run("sort", input_text := "c\\na\\nb")`, lang: 'df' },
  {"p": "Útil para alimentar um filtro sem escrever arquivo temporário."},
  {"h3": "Encadear"},
  { code: `Proc.pipeline(["echo zebra", "sort"])`, lang: 'df' },
  {"p": "A saída de cada comando vira a entrada do próximo, e a cadeia **para no primeiro que falhar** — devolvendo o resultado daquele, não um sucesso enganoso."},
  {"h3": "Tempo limite"},
  { code: `Proc.run("sleep 5", timeout := 1)     // ok = no, timed_out = yes
// (no Windows: "timeout 5")`, lang: 'df' },
  {"p": "Sempre ponha timeout em comando que fala com a rede. Sem ele, um servidor que não responde trava seu programa indefinidamente."},
  {"h3": "Processos em segundo plano"},
  { code: `p := Proc.spawn("servidor --porta 8080")
// ... o programa continua
Proc.is_running(p)
Proc.terminate(p)      // pede para encerrar (SIGTERM)
Proc.kill(p)           // força (SIGKILL)
r := Proc.wait(p)      // espera e colhe o resultado`, lang: 'df' },
  {"h3": "O comando externo é onde o programa deixa de ser portátil"},
  {"p": "Tudo o mais em DataForge roda igual nos três sistemas. Chamar um programa de fora é a fronteira: `echo` existe no Linux e no macOS como arquivo executável e no Windows é embutido do interpretador de comandos, `cat` se chama `more`, e `sleep` se chama `timeout` — e o `timeout` do Windows recusa entrada redirecionada e sai na hora, então quem precisa de uma espera de verdade usa `ping` para o próprio computador."},
  {"p": "A resposta não é fingir que dá no mesmo. É decidir **uma vez**, no topo, e escrever o resto igual:"},
  { code: `adopt Arcane.OS as OS

steady WINDOWS := OS.is_windows()
steady ECO := "cmd /c echo" given WINDOWS otherwise "echo"
steady DEMORA := "ping -n 6 127.0.0.1" given WINDOWS otherwise "sleep 5"`, lang: 'df' },
  {"p": "`sort` é uma das poucas exceções: existe com o mesmo nome nos dois e lê da entrada padrão. Por isso o exercício o usa para mostrar `input_text` e `pipeline`."},
  {"p": "E há um detalhe que a lista **não** resolve: no Windows, `cmd` reprocessa a linha que recebe e devolve as aspas junto com o texto. Passar uma lista garante que o argumento chega **inteiro** ao programa — não garante o que o programa do outro lado faz com ele depois."},
  {"h3": "Saída esperada"},
  { code: `saida:  ola do processo
codigo: 0
ok:     yes

capture: 'direto'

inexistente -> codigo 127, ok=no

xyz existe?  no

lista: texto com espacos
stdin ordenado: [a, b, c]

pipeline: zebra

com timeout: ok=no`, lang: 'text' },
  {"p": "Idêntico nos três sistemas — e é por isso que o exercício decide os comandos **uma vez**, no topo."},
  {"h3": "Experimente"},
  {"list": ["Rode `git log --oneline -5` e mostre os commits formatados.", "Rode o exercício no outro sistema operacional e veja o que muda.", "Escreva `action tem_git()` usando `Proc.exists`.", "Compare `run` com `shell := yes` e sem, num comando com `*`."]},
  {"h2": "163 · Registro de eventos"},
  {"p": "**Enunciado.** registre o que acontece com niveis, campos e destino em arquivo."},
  { code: `adopt Arcane.Logging as Log
adopt Arcane.IO as IO

// Um logger nomeado, com nivel minimo
registro := Log.logger("pedidos", "DEBUG")
registro.colored(no)

registro.debug("iniciando o processamento")
registro.info("pedido recebido", {"id": 1042, "cliente": "Ana"})
registro.warn("estoque baixo", {"produto": "P02", "restam": 3})
registro.error("pagamento recusado", {"id": 1042, "codigo": 402})

out ""
out $"contagem: {registro.stats()}"
assert registro.stats().INFO is 1, "um INFO"
assert registro.stats().ERROR is 1, "um ERROR"

// O nivel filtra o que sai
out ""
out "── com nivel WARN, DEBUG e INFO somem ──"
silencioso := Log.logger("filtrado", "WARN")
silencioso.colored(no)
silencioso.debug("nao aparece")
silencioso.info("nao aparece")
silencioso.warn("essa aparece")
silencioso.error("essa tambem")

assert "DEBUG" not in silencioso.stats().keys(), "DEBUG filtrado"
assert silencioso.stats().WARN is 1, "WARN passou"

// Contexto fixo, repetido em toda linha
out ""
out "── com contexto ──"
servico := Log.logger("api", "INFO")
servico.colored(no)
servico.with_context({"servico": "checkout", "versao": "1.2"})
servico.info("requisicao recebida", {"rota": "/pagar"})
servico.info("requisicao concluida", {"ms": 42})

// Formato JSON, para maquina ler
out ""
out "── em JSON ──"
maquina := Log.logger("json", "INFO")
maquina.as_json(yes)
maquina.info("evento estruturado", {"usuario": 7, "acao": "login"})

// Guardar em memoria para inspecionar
out ""
auditoria := Log.logger("auditoria", "INFO")
auditoria.colored(no)
auditoria.keep(yes)
auditoria.info("acao A")
auditoria.error("acao B falhou")

erros := auditoria.records() >> sift r: r["level"] is "ERROR"
out $"registros guardados: {len(auditoria.records())}, erros: {len(erros)}"
assert len(auditoria.records()) is 2, "dois registros"
assert len(erros) is 1, "um erro"

// Gravar em arquivo
out ""
caminho := "_log_exercicio.txt"
arquivo := Log.logger("disco", "INFO")
arquivo.colored(no)
arquivo.to_file(caminho, no)
arquivo.info("linha gravada", {"n": 1})
arquivo.warn("segunda linha")
arquivo.close()

conteudo := IO.read(caminho)
out $"o arquivo tem {len(conteudo.lines())} linhas"
assert len(conteudo.lines()) is 2, "duas linhas no arquivo"
assert "linha gravada" in conteudo, "conteudo gravado"
IO.delete(caminho)
out "arquivo temporario removido"`, lang: 'df', title: `exercicios/17-tempo-e-sistema/163_logging_estruturado.df` },
  {"h3": "Por que não usar `out`"},
  {"p": "`out` serve para falar com quem está olhando o terminal agora. Log serve para responder perguntas depois: *o que aconteceu às 3h da manhã?*"},
  {"p": "A diferença prática está em três coisas que `out` não tem: **nível**, **campos estruturados** e **destino configurável**."},
  {"h3": "Os seis níveis"},
  {"table": {"head": ["Nível", "Quando"], "rows": [["`TRACE`", "detalhe fino, normalmente desligado"], ["`DEBUG`", "o que ajuda a investigar"], ["`INFO`", "eventos normais que valem registrar"], ["`WARN`", "algo estranho, mas o programa segue"], ["`ERROR`", "uma operação falhou"], ["`FATAL`", "o programa não continua"]]}},
  {"p": "O nível do logger é um **piso**: com `WARN`, tudo abaixo é descartado sem custo."},
  { code: `registro := Log.logger("pedidos", "DEBUG")     // durante o desenvolvimento
registro := Log.logger("pedidos", "WARN")      // em produção`, lang: 'df' },
  {"p": "Uma linha muda a verbosidade do sistema inteiro."},
  {"h3": "Campos estruturados"},
  { code: `registro.info("pedido recebido", {"id": 1042, "cliente": "Ana"})`, lang: 'df' },
  {"p": "Sai como `pedido recebido id=1042 cliente=Ana`."},
  {"p": "Compare com `out $\"pedido {id} do cliente {nome}\"`. A diferença aparece na hora de procurar: com campos, `grep 'id=1042'` acha tudo daquele pedido. Com texto interpolado, a estrutura se perdeu na formatação."},
  {"h3": "Contexto fixo"},
  { code: `servico.with_context({"servico": "checkout", "versao": "1.2"})`, lang: 'df' },
  {"p": "Esses campos passam a aparecer em **toda** linha daquele logger. Você escreve uma vez o que é constante e não repete em cada chamada."},
  {"h3": "JSON para máquina"},
  { code: `maquina.as_json(yes)`, lang: 'df' },
  {"p": "Cada linha vira um objeto JSON completo — o formato que ferramentas de agregação (Elasticsearch, Loki, CloudWatch) esperam. Uma linha de configuração troca o público-alvo do log de humano para máquina."},
  {"h3": "Guardar em memória"},
  { code: `auditoria.keep(yes)
...
erros := auditoria.records() >> sift r: r["level"] is "ERROR"`, lang: 'df' },
  {"p": "Útil em teste: você verifica **que o log certo foi emitido**, sem ler stdout."},
  {"h3": "Arquivo"},
  { code: `arquivo.to_file("app.log", yes)     // yes = anexar
...
arquivo.close()`, lang: 'df' },
  {"p": "O `close` garante que o buffer foi para o disco. Em programa que roda continuamente, combine com `defer`."},
  {"h3": "Saída esperada"},
  { code: `23:59:01 DEBUG [pedidos] iniciando o processamento
23:59:01 INFO  [pedidos] pedido recebido id=1042 cliente=Ana
23:59:01 WARN  [pedidos] estoque baixo produto=P02 restam=3
23:59:01 ERROR [pedidos] pagamento recusado id=1042 codigo=402

contagem: {DEBUG: 1, INFO: 1, WARN: 1, ERROR: 1}
...
{"time": "...", "level": "INFO", "logger": "json", "message": "evento estruturado", "usuario": 7, "acao": "login"}`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Ligue `as_json` e mande para arquivo; leia de volta com `Serde.from_json_lines`.", "Escreva um logger que também conta erros por código.", "Use `keep(yes)` num teste para verificar que um aviso foi emitido."]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/17-tempo-e-sistema/158_datas_basico.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '158-datas-e-horas', text: "158 · Datas e horas", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'comparacao', text: "Comparação", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '159-aritmetica-com-datas', text: "159 · Aritmetica com datas", level: 2 as const }, { id: 'somar-periodos', text: "Somar períodos", level: 3 as const }, { id: 'o-caso-dificil-addmonths', text: "O caso difícil: `add_months`", level: 3 as const }, { id: 'diferencas', text: "Diferenças", level: 3 as const }, { id: 'humanizar', text: "Humanizar", level: 3 as const }, { id: 'limites-de-periodo', text: "Limites de período", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '160-cronometragem-e-desempenho', text: "160 · Cronometragem e desempenho", level: 2 as const }, { id: 'measure-a-forma-direta', text: "`measure` — a forma direta", level: 3 as const }, { id: 'stopwatch-controle-manual', text: "`stopwatch` — controle manual", level: 3 as const }, { id: 'medir-para-decidir', text: "Medir para decidir", level: 3 as const }, { id: 'medir-varias-vezes', text: "Medir várias vezes", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '161-sistema-e-ambiente', text: "161 · Sistema e ambiente", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'identificar-o-sistema', text: "Identificar o sistema", level: 3 as const }, { id: 'ternario-encadeado', text: "Ternário encadeado", level: 3 as const }, { id: 'variaveis-de-ambiente', text: "Variáveis de ambiente", level: 3 as const }, { id: 'disco', text: "Disco", level: 3 as const }, { id: 'which', text: "`which`", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '162-executando-processos', text: "162 · Executando processos", level: 2 as const }, { id: 'seguranca-primeiro', text: "Segurança primeiro", level: 3 as const }, { id: 'o-resultado', text: "O resultado", level: 3 as const }, { id: 'atalhos', text: "Atalhos", level: 3 as const }, { id: 'enviar-entrada', text: "Enviar entrada", level: 3 as const }, { id: 'encadear', text: "Encadear", level: 3 as const }, { id: 'tempo-limite', text: "Tempo limite", level: 3 as const }, { id: 'processos-em-segundo-plano', text: "Processos em segundo plano", level: 3 as const }, { id: 'o-comando-externo-e-onde-o-programa-deixa-de-ser-portatil', text: "O comando externo é onde o programa deixa de ser portátil", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '163-registro-de-eventos', text: "163 · Registro de eventos", level: 2 as const }, { id: 'por-que-nao-usar-out', text: "Por que não usar `out`", level: 3 as const }, { id: 'os-seis-niveis', text: "Os seis níveis", level: 3 as const }, { id: 'campos-estruturados', text: "Campos estruturados", level: 3 as const }, { id: 'contexto-fixo', text: "Contexto fixo", level: 3 as const }, { id: 'json-para-maquina', text: "JSON para máquina", level: 3 as const }, { id: 'guardar-em-memoria', text: "Guardar em memória", level: 3 as const }, { id: 'arquivo', text: "Arquivo", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"17 · Tempo e sistema"}
      description={"6 exercícios: datas, durações, ambiente e processos."}
      href={"/docs/exercicios/17-tempo-e-sistema"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
