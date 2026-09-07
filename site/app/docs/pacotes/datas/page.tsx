import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "datas",
  description: "Datas em português, com feriados brasileiros e dias úteis.",
};

const blocos: Bloco[] = [
  { code: `dataforge add datas`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"]]}},
  {"h2": "Por que existe"},
  {"p": "Somar um mês a 31 de janeiro tem que dar 28 (ou 29) de fevereiro. As contas aqui passam pelo dia juliano, não por manipulação de texto — é o que faz esse caso sair certo."},
  {"h2": "Exemplo"},
  { code: `adopt datas as D

hoje := D.hoje()
out D.formatar(hoje, "dd/MM/yyyy")        // 07/09/2026
out D.formatar(hoje, "EEEE")              // segunda-feira
out D.por_extenso(hoje)                   // 7 de setembro de 2026

out D.relativo(D.dias_atras(3))           // há 3 dias
out D.idade(D.criar(1990, 5, 10))         // 36

out D.e_feriado(D.criar(2026, 12, 25))    // yes
out D.nome_do_feriado(D.criar(2026, 9, 7))// Independência
out D.iso(D.pascoa(2026))                 // 2026-04-05

// 31 de janeiro + 1 mês
out D.iso(D.somar_meses(D.criar(2026, 1, 31), 1))   // 2026-02-28`, lang: 'df' },
  {"h2": "API"},
  {"table": {"head": ["Função", "O que faz"], "rows": [["`hoje()` / `criar(a, m, d)`", "a data"], ["`formatar(d, padrao)`", "dd MM yyyy MMMM EEEE"], ["`por_extenso(d)`", "7 de setembro de 2026"], ["`relativo(d)`", "há 3 dias, em 2 meses"], ["`idade(nascimento)`", "anos completos"], ["`somar_dias/meses/anos`", "aritmética de calendário"], ["`dias_entre(a, b)`", "diferença em dias"], ["`dia_da_semana(d)`", "0 = segunda … 6 = domingo"], ["`e_feriado(d)` / `feriados(ano)`", "feriados nacionais"], ["`pascoa(ano)`", "base dos feriados móveis"], ["`e_dia_util(d)` / `dias_uteis_entre`", "desconta fim de semana e feriado"], ["`de_iso(t)` / `de_br(t)`", "leitura de texto"], ["`faixa(inicio, fim)`", "todas as datas do intervalo"]]}},
  {"h2": "Instalar"},
  { code: `dataforge add datas
dataforge add datas@1.0.0
dataforge add datas@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'exemplo', text: "Exemplo", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"datas"}
      description={"Datas em português, com feriados brasileiros e dias úteis."}
      href={"/docs/pacotes/datas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
