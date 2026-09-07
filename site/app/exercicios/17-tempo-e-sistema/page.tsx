import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "17 · Tempo e sistema",
  description: "6 exercícios: datas, cronômetro, SO, processos e logging.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 17`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["157", "**Datas e horas**", "crie, formate e compare datas com Arcane.Time."], ["158", "**Aritmetica com datas**", "some e subtraia periodos, e calcule diferencas."], ["159", "**Cronometragem e desempenho**", "meca quanto tempo o codigo leva."], ["160", "**Sistema e ambiente**", "consulte o sistema operacional e as variaveis de ambiente."], ["161", "**Executando processos**", "rode comandos externos e trate a saida."], ["162", "**Registro de eventos**", "registre o que acontece com niveis, campos e destino em arquivo."]]}},
  {"h2": "157 · Datas e horas"},
  {"p": "Crie, formate e compare datas com Arcane.Time."},
  { code: `// Exercicio 157 — Datas e horas
// Enunciado: crie, formate e compare datas com Arcane.Time.

adopt Arcane.Time as Time

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
assert Time.quarter(natal) is 4, "dezembro e do quarto trimestre"
`, title: `157_datas_basico.df` },
  {"h2": "158 · Aritmetica com datas"},
  {"p": "Some e subtraia periodos, e calcule diferencas."},
  { code: `// Exercicio 158 — Aritmetica com datas
// Enunciado: some e subtraia periodos, e calcule diferencas.

adopt Arcane.Time as Time

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
assert Time.days_in_month(2024, 2) is 29, "fevereiro bissexto"
`, title: `158_datas_aritmetica.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 4 exercícios deste módulo estão em `exercicios/17-tempo-e-sistema/`. Cada um tem um `.md` ao lado com a explicação completa."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '157--datas-e-horas', text: "157 · Datas e horas", level: 2 as const }, { id: '158--aritmetica-com-datas', text: "158 · Aritmetica com datas", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"17 · Tempo e sistema"}
      description={"6 exercícios: datas, cronômetro, SO, processos e logging."}
      href={"/exercicios/17-tempo-e-sistema"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
