import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Test",
  description: "Asserções e organização de suítes.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Test as Test

action fatorial(n):
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)

Test.assert_eq(fatorial(5), 120, "fatorial de 5")
Test.assert_true(fatorial(3) bigger fatorial(2), "cresce")
Test.assert_between(fatorial(4), 20, 30, "24 no intervalo")`, title: `exemplo` },
  {"p": "Guia com contexto e boas práticas: [Test](/docs/tecnicas/testes)."},
  {"h2": "Funções (34)"},
  {"table": {"head": ["Assinatura"], "rows": [["`add_test(suite, name, spec)`"], ["`assert_all(collection, predicate, msg=None)`"], ["`assert_any(collection, predicate, msg=None)`"], ["`assert_between(value, low, high, msg=None)`"], ["`assert_close(actual, expected, tolerance=0.001, msg=None)`"], ["`assert_contains(collection, item, msg=None)`"], ["`assert_deep_eq(a, b, msg=None)`"], ["`assert_empty(collection, msg=None)`"], ["`assert_eq(actual, expected, msg=None)`"], ["`assert_false(value, msg=None)`"], ["`assert_greater(a, b, msg=None)`"], ["`assert_instance(obj, blueprint_name, msg=None)`"], ["`assert_keys(d, *expected_keys, msg=None)`"], ["`assert_length(collection, expected, msg=None)`"], ["`assert_less(a, b, msg=None)`"], ["`assert_match(string, pattern, msg=None)`"], ["`assert_neq(actual, expected, msg=None)`"], ["`assert_not_contains(collection, item, msg=None)`"], ["`assert_not_empty(collection, msg=None)`"], ["`assert_not_void(value, msg=None)`"], ["`assert_sorted(collection, reverse=False, msg=None)`"], ["`assert_throws(func, msg=None)`"], ["`assert_true(value, msg=None)`"], ["`assert_type(value, expected_type, msg=None)`"], ["`assert_unique(collection, msg=None)`"], ["`assert_void(value, msg=None)`"], ["`benchmark(func, iterations=1000)`"], ["`describe(name, tests)`"], ["`it(description, test_func)`"], ["`mock(return_value=None)`"], ["`run(suite, tests)`"], ["`run_suite(suite)`"], ["`spy(func)`"], ["`suite(name='Test Suite')`"]]}},
];

const headings = [{ id: 'funcoes-34', text: "Funções (34)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Test"}
      description={"Asserções e organização de suítes."}
      href={"/docs/biblioteca/test"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
