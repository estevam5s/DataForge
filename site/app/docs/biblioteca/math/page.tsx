// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/math.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Math",
  description: "Matemática, álgebra linear e estatística básica.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Math as Math

out Math.sqrt(16), Math.factorial(5)
out Math.is_prime(97), Math.fibonacci(12)
out Math.gcd(48, 18), Math.lcm(4, 6)
out Math.clamp(15, 0, 10)

amostra := [12, 15, 11, 18, 20, 15]
out Math.mean(amostra), Math.median(amostra)
out round(Math.stdev(amostra), 4)`, title: `exemplo` },
  {"h2": "Constantes"},
  {"table": {"head": ["Nome", "Valor"], "rows": [["`E`", "`2.718281828459045`"], ["`INF`", "`Infinity`"], ["`NAN`", "`NaN`"], ["`PI`", "`3.141592653589793`"], ["`TAU`", "`6.283185307179586`"], ["`random`", "`{'random': <built-in method random of Random object at 0x…`"]]}},
  {"h2": "Funções (66)"},
  {"table": {"head": ["Assinatura"], "rows": [["`abs(x, /)`"], ["`acos(x, /)`"], ["`asin(x, /)`"], ["`atan(x, /)`"], ["`atan2(y, x, /)`"], ["`cbrt(x)`"], ["`ceil(x, /)`"], ["`clamp(value, min_val, max_val)`"], ["`comb(n, k, /)`"], ["`complexo(real, imaginario=0.0)`"], ["`complexo_conjugado(z)`"], ["`complexo_de_polar(r, a)`"], ["`complexo_exp(z)`"], ["`complexo_fase(z)`"], ["`complexo_log(z, base=None)`"], ["`complexo_modulo(z)`"], ["`complexo_partes(z)`"], ["`complexo_polar(z)`"], ["`complexo_raiz(z)`"], ["`complexo_texto(z)`"], ["`cos(x, /)`"], ["`degrees(x, /)`"], ["`determinant(matrix)`"], ["`dot(a, b)`"], ["`exp(x, /)`"], ["`factorial(n, /)`"], ["`fibonacci(n)`"], ["`floor(x, /)`"], ["`fracao(a, b=None)`"], ["`fracao_de_texto(t)`"], ["`fracao_dividido(a, b)`"], ["`fracao_float(f)`"], ["`fracao_limitar(f, teto)`"], ["`fracao_menos(a, b)`"], ["`fracao_partes(f)`"], ["`fracao_soma(*p)`"], ["`fracao_texto(f)`"], ["`fracao_vezes(*p)`"], ["`gcd(*integers)`"], ["`hypot`"], ["`identity(n)`"], ["`is_prime(n)`"], ["`lcm(a, b)`"], ["`lerp(a, b, t)`"], ["`log`"], ["`log10(x, /)`"], ["`log2(x, /)`"], ["`map_range(value, in_min, in_max, out_min, out_max)`"], ["`matrix(data)`"], ["`max`"], ["`mean(data)`"], ["`median(data)`"], ["`min`"], ["`ones(rows, cols=None)`"], ["`perm(n, k=None, /)`"], ["`pow(x, y, /)`"], ["`radians(x, /)`"], ["`round(number, ndigits=None)`"], ["`sin(x, /)`"], ["`sqrt(x, /)`"], ["`stdev(data)`"], ["`sum(data)`"], ["`tan(x, /)`"], ["`transpose(matrix)`"], ["`variance(data)`"], ["`zeros(rows, cols=None)`"]]}},
];

const headings = [{ id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-66', text: "Funções (66)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Math"}
      description={"Matemática, álgebra linear e estatística básica."}
      href={"/docs/biblioteca/math"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
