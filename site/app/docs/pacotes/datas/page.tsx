import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "datas",
  description: "Datas em português: formatação, tempo relativo, dias úteis, feriados brasileiros e faixas.",
};

const blocos: Bloco[] = [
  { code: `dataforge add datas`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "35 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Somar um mês a 31 de janeiro tem que dar 28 (ou 29) de fevereiro. As contas passam pelo dia juliano, não por manipulação de texto — é o que faz esse caso sair certo."},
  {"h2": "Uso"},
  { code: `adopt datas as D
out D.formatar(D.hoje(), "dd/MM/yyyy")     // 07/09/2026
out D.relativo(D.dias_atras(3))            // "há 3 dias"
out D.e_feriado(D.criar(2026, 12, 25))     // yes`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 35 símbolos:"},
  { code: `record Data
criar(ano, mes, dia)
hoje()
bissexto(ano)
dias_no_mes(ano, mes)
valida(d)
somar_dias(d, n)
somar_meses(d, n)
somar_anos(d, n)
dias_entre(a, b)
dias_atras(n)
dias_a_frente(n)
dia_da_semana(d)
e_fim_de_semana(d)
e_dia_util(d)
para_juliano(d)
de_juliano(jd)
pascoa(ano)
feriados(ano)
e_feriado(d)
nome_do_feriado(d)
dias_uteis_entre(a, b)
proximo_dia_util(d)
formatar(d, padrao := "dd/MM/yyyy")
por_extenso(d)
iso(d)
de_iso(texto)
de_br(texto)
relativo(d, referencia := void)
idade(nascimento, referencia := void)
faixa(inicio, fim)
MESES
MESES_CURTOS
DIAS
DIAS_CURTOS`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add datas
dataforge add datas@1.0.0
dataforge add datas@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"datas"}
      description={"Datas em português: formatação, tempo relativo, dias úteis, feriados brasileiros e faixas."}
      href={"/docs/pacotes/datas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
