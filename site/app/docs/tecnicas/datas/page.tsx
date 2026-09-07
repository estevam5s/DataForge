import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Datas e horas",
  description: "Arcane.Time: construir, formatar, comparar e fazer aritmética com datas.",
};

const blocos: Bloco[] = [
  {"h2": "Construir"},
  { code: `adopt Arcane.Time as Time

Time.now()                        # agora, com hora
Time.today()                      # hoje à meia-noite
Time.date(2026, 12, 25)
Time.datetime(2026, 3, 15, 14, 30, 0)
Time.parse("2026-06-15")          # interpreta vários formatos` },
  {"p": "`parse` tenta ISO, brasileiro e as variantes com hora — sem você precisar dizer qual é."},
  {"h2": "Formatar"},
  {"table": {"head": ["Chamada", "Resultado"], "rows": [["`to_date_string(d)`", "`25/12/2026`"], ["`to_time_string(d)`", "`14:30:00`"], ["`to_br(d)`", "`25/12/2026 14:30:00`"], ["`to_iso(d)`", "`2026-12-25T00:00:00`"], ["`format(d, \"%d/%m\")`", "livre, com códigos strftime"]]}},
  {"h2": "Componentes"},
  { code: `Time.year(d)  Time.month(d)  Time.day(d)
Time.hour(d)  Time.minute(d)  Time.second(d)
Time.weekday(d)          # 0 = segunda
Time.weekday_name(d)     # "sexta-feira"
Time.month_name(d)       # "dezembro"
Time.quarter(d)          # 1..4
Time.day_of_year(d)      # 1..366` },
  {"p": "Os nomes vêm **em português** — é a língua do módulo, e evita traduzir `\"Friday\"` em cada relatório."},
  {"h2": "Aritmética"},
  { code: `Time.add_days(d, 10)      Time.add_weeks(d, 2)
Time.add_months(d, 1)     Time.add_years(d, 1)
Time.add_hours(d, 3)      Time.add_minutes(d, 45)` },
  {"p": "Todas devolvem uma **data nova** — a original não muda. Para subtrair, passe um número negativo."},
  {"h3": "O caso difícil: add_months"},
  {"p": "O que é \"31 de janeiro mais um mês\"? Não existe 31 de fevereiro."},
  { code: `Time.add_months(Time.date(2026, 1, 31), 1)     # 28/02/2026` },
  {"p": "A regra é **grampear no último dia válido** do mês de destino — o que Java, C# e a maioria das bibliotecas fazem."},
  {"callout": {"tipo": "atencao", "texto": "A operação **não é reversível**: somar um mês e subtrair um mês pode não voltar ao dia original (31/01 → 28/02 → 28/01). Se isso importa, trabalhe em dias."}},
  {"h2": "Diferenças"},
  { code: `d := Time.diff(inicio, fim)

d.days             # 364
d.total_hours      # 8736.0
d.total_seconds    # 31449600.0
d.human            # "364d 0h"` },
  {"p": "Ter todos os formatos calculados evita a conta de conversão espalhada pelo código."},
  {"h2": "Humanizar"},
  { code: `Time.humanize(45)       # "45s"
Time.humanize(90)       # "1min 30s"
Time.humanize(3725)     # "1h 2min"
Time.humanize(90000)    # "1d 1h"` },
  {"p": "A função escolhe a unidade sozinha — é o que você quer numa interface, onde \"31449600 segundos\" não diz nada."},
  {"h2": "Comparar"},
  { code: `Time.is_before(a, b)      Time.is_after(a, b)
Time.is_same_day(a, b)    Time.is_weekend(d)
Time.is_leap_year(2024)   Time.age(nascimento)` },
  {"p": "`is_same_day` existe porque comparar dois `DateTime` diretamente compararia também a hora — duas coisas no mesmo dia, às 9h e às 15h, não são iguais."},
  {"h2": "Limites de período"},
  { code: `Time.start_of_day(d)     Time.end_of_day(d)
Time.start_of_month(d)   Time.end_of_month(d)
Time.days_in_month(2024, 2)     # 29` },
  {"p": "`start_of_day` e `end_of_day` são o que você usa para filtrar \"tudo de hoje\" numa consulta — sem eles, comparar com `Time.today()` deixa de fora tudo depois da meia-noite."},
  {"h2": "Cronometrar"},
  { code: `medida := Time.measure(trabalho_pesado)
out medida.result, round(medida.ms, 2)

crono := Time.stopwatch()
crono.start()
# ... trabalho
out round(crono.stop() * 1000, 2)` },
  {"p": "`start` depois de `stop` **retoma** — o acumulado não se perde. Isso permite medir só as partes que interessam."},
  {"callout": {"tipo": "dica", "titulo": "Meça antes de otimizar", "texto": "A intuição sobre o que é lento erra com frequência. Uma medição isolada também é ruído: o **mínimo** de várias execuções costuma ser mais informativo que a média."}},
];

const headings = [{ id: 'construir', text: "Construir", level: 2 as const }, { id: 'formatar', text: "Formatar", level: 2 as const }, { id: 'componentes', text: "Componentes", level: 2 as const }, { id: 'aritmetica', text: "Aritmética", level: 2 as const }, { id: 'diferencas', text: "Diferenças", level: 2 as const }, { id: 'humanizar', text: "Humanizar", level: 2 as const }, { id: 'comparar', text: "Comparar", level: 2 as const }, { id: 'limites-de-periodo', text: "Limites de período", level: 2 as const }, { id: 'cronometrar', text: "Cronometrar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Datas e horas"}
      description={"Arcane.Time: construir, formatar, comparar e fazer aritmética com datas."}
      href={"/docs/tecnicas/datas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
