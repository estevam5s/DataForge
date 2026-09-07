import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Math",
  description: "Matemática, álgebra linear e estatística.",
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
  {"table": {"head": ["Nome", "Valor"], "rows": [["`E`", "`2.718281828459045`"], ["`INF`", "`inf`"], ["`NAN`", "`nan`"], ["`PI`", "`3.141592653589793`"], ["`TAU`", "`6.283185307179586`"], ["`random`", "`{'random': <built-in method random of Random o…`"]]}},
  {"h2": "Funções (45)"},
  {"table": {"head": ["Assinatura"], "rows": [["`abs(x)`"], ["`acos(x)`"], ["`asin(x)`"], ["`atan(x)`"], ["`atan2(y, x)`"], ["`cbrt(x)`"], ["`ceil(x)`"], ["`clamp(value, min_val, max_val)`"], ["`comb(n, k)`"], ["`cos(x)`"], ["`degrees(x)`"], ["`determinant(matrix)`"], ["`dot(a, b)`"], ["`exp(x)`"], ["`factorial(n)`"], ["`fibonacci(n)`"], ["`floor(x)`"], ["`gcd(*integers)`"], ["`hypot(…)`"], ["`identity(n)`"], ["`is_prime(n)`"], ["`lcm(a, b)`"], ["`lerp(a, b, t)`"], ["`log(…)`"], ["`log10(x)`"], ["`log2(x)`"], ["`map_range(value, in_min, in_max, out_min, out_max)`"], ["`matrix(data)`"], ["`max(…)`"], ["`mean(data)`"], ["`median(data)`"], ["`min(…)`"], ["`ones(rows, cols=None)`"], ["`perm(n, k=None)`"], ["`pow(x, y)`"], ["`radians(x)`"], ["`round(number, ndigits=None)`"], ["`sin(x)`"], ["`sqrt(x)`"], ["`stdev(data)`"], ["`sum(data)`"], ["`tan(x)`"], ["`transpose(matrix)`"], ["`variance(data)`"], ["`zeros(rows, cols=None)`"]]}},
];

const headings = [{ id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-45', text: "Funções (45)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Math"}
      description={"Matemática, álgebra linear e estatística."}
      href={"/docs/biblioteca/math"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
