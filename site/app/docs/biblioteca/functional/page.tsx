import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Functional",
  description: "Composição, lentes, Maybe/Either e transdutores.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Functional as F

nums := [5, 1, 4, 2, 8, 3]

out F.sort_by(lambda n: n, nums)
out F.chunk(2, nums)
out F.take_while(lambda n: n bigger 0, nums)
out F.unique_by(lambda n: n % 3, nums)
out F.group_by(lambda n: n % 2 is 0 and "par" or "impar", nums)`, title: `exemplo` },
  {"h2": "Funções (56)"},
  {"table": {"head": ["Assinatura"], "rows": [["`all_pass(*preds)`"], ["`any_pass(*preds)`"], ["`both(f, g)`"], ["`chunk(n, collection)`"], ["`complement(fn)`"], ["`compose(*fns)`"], ["`constantly(x)`"], ["`curry(fn, arity=None)`"], ["`drop_while(fn, collection)`"], ["`either(f, g)`"], ["`filter(fn, collection)`"], ["`flat_map(fn, collection)`"], ["`flip(fn)`"], ["`frequencies(collection)`"], ["`from_either(left_fn, right_fn, e)`"], ["`from_maybe(default, m)`"], ["`group_by(fn, collection)`"], ["`identity(x)`"], ["`index_by(fn, collection)`"], ["`interleave(*collections)`"], ["`into(target_type, xform, collection)`"], ["`is_just(m)`"], ["`is_left(e)`"], ["`is_nothing(m)`"], ["`is_right(e)`"], ["`just(value)`"], ["`juxt(*fns)`"], ["`left(value)`"], ["`lens(*keys)`"], ["`map(fn, collection)`"], ["`match(value, *cases)`"], ["`maybe(value)`"], ["`memoize(fn)`"], ["`nothing()`"], ["`once(fn)`"], ["`over(lens, fn, obj)`"], ["`partial(fn, *args)`"], ["`partition_by(fn, collection)`"], ["`pipe(*fns)`"], ["`reduce(fn, collection, initial=None)`"], ["`right(value)`"], ["`scan(fn, collection, initial)`"], ["`set_lens(lens, value, obj)`"], ["`sort_by(fn, collection)`"], ["`spread(fn)`"], ["`take_while(fn, collection)`"], ["`tap(fn, value)`"], ["`thread_first(value, *fns)`"], ["`thread_last(value, *fns)`"], ["`trampoline(fn, *args)`"], ["`transduce(xform, reducer, initial, collection)`"], ["`try_catch(fn)`"], ["`unique_by(fn, collection)`"], ["`view(lens, obj)`"], ["`when(*conditions)`"], ["`zip_with(fn, *collections)`"]]}},
];

const headings = [{ id: 'funcoes-56', text: "Funções (56)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Functional"}
      description={"Composição, lentes, Maybe/Either e transdutores."}
      href={"/docs/biblioteca/functional"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
