import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Funções embutidas",
  description: "As 225 funções e constantes globais, disponíveis sem import.",
};

const blocos: Bloco[] = [
  {"p": "São **225 funções e constantes** disponíveis sem nenhum `adopt`. Para o que está além disso, veja a [Biblioteca Arcane](/biblioteca)."},
  {"h2": "Tipos e conversão (10)"},
  {"p": "`bool` `cast` `cluster` `float` `int` `len` `range` `str` `type` `vault`"},
  {"h2": "Texto (54)"},
  {"p": "`capitalize` `center` `char` `char_at` `concat` `count_str` `decode` `encode` `endswith` `expandtabs` `find` `format` `includes` `index_of` `isalnum` `isalpha` `isascii` `isdigit` `islower` `isnumeric` `isspace` `istitle` `isupper` `join` `last_index_of` `lines` `ljust` `lower` `lstrip` `ord` `pad_end` `pad_start` `partition` `removeprefix` `removesuffix` `repeat` `replace` `reverse_str` `rfind` `rjust` `rpartition` `rstrip` `split` `splitlines` `startswith` `strip` `substring` `swapcase` `template` `title` `trim` `upper` `words` `zfill`"},
  {"h2": "Expressões regulares (8)"},
  {"p": "`regex_count` `regex_extract` `regex_findall` `regex_match` `regex_search` `regex_split` `regex_sub` `regex_test`"},
  {"h2": "Matemática (43)"},
  {"p": "`abs` `acos` `asin` `atan` `atan2` `cbrt` `ceil` `clamp` `comb` `cos` `degrees` `exp` `factorial` `floor` `gcd` `hypot` `is_finite` `is_inf` `is_nan` `lcm` `lerp` `log` `log10` `log2` `max` `mean` `median` `min` `mode` `percentile` `perm` `pow` `radians` `reversed` `round` `sign` `sin` `sorted` `sqrt` `stdev` `sum` `tan` `variance`"},
  {"h2": "Coleções (29)"},
  {"p": "`append` `chunk` `contains` `count` `deep_copy` `drop` `enumerate` `first` `flatten` `frequencies` `index` `insert` `interleave` `invert_dict` `items` `keys` `last` `merge_dicts` `omit` `pick` `pop` `remove` `rotate` `slice` `take` `unique` `unzip` `values` `zip`"},
  {"h2": "Funcional (21)"},
  {"p": "`complement` `compose` `constantly` `curry` `every` `filter` `find_first` `find_last` `flat_map` `identity` `map` `memoize` `none_of` `once` `partial` `pipe_fn` `reduce` `scan` `some` `tap` `zip_with`"},
  {"h2": "Sistema e utilidades (27)"},
  {"p": "`accumulate` `base64_decode` `base64_encode` `chain` `choice` `combinations` `env_var` `exists` `freeze` `from_json` `hash` `hash_md5` `hash_sha256` `id` `permutations` `product` `randint` `random` `repeat_val` `sample` `shuffle` `sleep` `thaw` `time` `timestamp` `to_json` `uuid`"},
  {"h2": "Predicados e validação (15)"},
  {"p": "`assert_type` `coalesce` `default` `default_val` `is_boolean` `is_callable` `is_dict` `is_empty` `is_float` `is_integer` `is_list` `is_number` `is_string` `is_void` `validate`"},
  {"h2": "Introspecção (8)"},
  {"p": "`class_name` `get_fields` `get_methods` `get_mro` `get_parent` `has_field` `has_method` `instanceof`"},
  {"h2": "Constantes e outros (10)"},
  {"p": "`E` `EMPTY` `INF` `MAX_INT` `MIN_INT` `NAN` `NEWLINE` `PI` `TAB` `TAU`"},
];

const headings = [{ id: 'tipos-e-conversao-10', text: "Tipos e conversão (10)", level: 2 as const }, { id: 'texto-54', text: "Texto (54)", level: 2 as const }, { id: 'expressoes-regulares-8', text: "Expressões regulares (8)", level: 2 as const }, { id: 'matematica-43', text: "Matemática (43)", level: 2 as const }, { id: 'colecoes-29', text: "Coleções (29)", level: 2 as const }, { id: 'funcional-21', text: "Funcional (21)", level: 2 as const }, { id: 'sistema-e-utilidades-27', text: "Sistema e utilidades (27)", level: 2 as const }, { id: 'predicados-e-validacao-15', text: "Predicados e validação (15)", level: 2 as const }, { id: 'introspeccao-8', text: "Introspecção (8)", level: 2 as const }, { id: 'constantes-e-outros-10', text: "Constantes e outros (10)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Funções embutidas"}
      description={"As 225 funções e constantes globais, disponíveis sem import."}
      href={"/referencia/embutidas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
