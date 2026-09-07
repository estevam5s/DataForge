import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Time",
  description: "Datas, horas, durações e cronometragem.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Time as Time

hoje := Time.today()
out Time.to_date_string(hoje)
out Time.weekday_name(hoje)
out Time.to_date_string(Time.add_days(hoje, 45))
out Time.age(Time.date(1995, 3, 10))
out Time.humanize(3725)`, title: `exemplo` },
  {"callout": {"tipo": "nota", "texto": "`add_months` grampeia no último dia válido: 31/01 + 1 mês = 28/02. A operação não é reversível — veja [Datas e horas](/docs/tecnicas/datas)."}},
  {"p": "Guia com contexto e boas práticas: [Time](/docs/tecnicas/datas)."},
  {"h2": "Funções (54)"},
  {"table": {"head": ["Assinatura"], "rows": [["`add_days(d, n)`"], ["`add_hours(d, n)`"], ["`add_minutes(d, n)`"], ["`add_months(d, n)`"], ["`add_seconds(d, n)`"], ["`add_weeks(d, n)`"], ["`add_years(d, n)`"], ["`age(nascimento, referencia=None)`"], ["`date(ano, mes, dia)`"], ["`datetime(ano, mes, dia, hora=0, minuto=0, segundo=0)`"], ["`day(d)`"], ["`day_of_year(d)`"], ["`days_between(a, b)`"], ["`days_in_month(a, m)`"], ["`diff(a, b)`"], ["`duration(dias=0, horas=0, minutos=0, segundos=0)`"], ["`end_of_day(d)`"], ["`end_of_month(d)`"], ["`format(d, formato='%Y-%m-%d %H:%M:%S')`"], ["`from_iso(t)`"], ["`from_timestamp(ts)`"], ["`hour(d)`"], ["`humanize(s)`"], ["`is_after(a, b)`"], ["`is_before(a, b)`"], ["`is_leap_year(a)`"], ["`is_same_day(a, b)`"], ["`is_weekend(d)`"], ["`measure(acao)`"], ["`minute(d)`"], ["`monotonic()`"], ["`month(d)`"], ["`month_name(d, curto=False)`"], ["`now()`"], ["`parse(texto, formato=None)`"], ["`quarter(d)`"], ["`second(d)`"], ["`sleep(s)`"], ["`start_of_day(d)`"], ["`start_of_month(d)`"], ["`stopwatch()`"], ["`timestamp()`"], ["`timezone_offset()`"], ["`to_br(d)`"], ["`to_date_string(d)`"], ["`to_iso(d)`"], ["`to_time_string(d)`"], ["`to_utc(d)`"], ["`today()`"], ["`utcnow()`"], ["`week_of_year(d)`"], ["`weekday(d)`"], ["`weekday_name(d, curto=False)`"], ["`year(d)`"]]}},
];

const headings = [{ id: 'funcoes-54', text: "Funções (54)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Time"}
      description={"Datas, horas, durações e cronometragem."}
      href={"/docs/biblioteca/time"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
