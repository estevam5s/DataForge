# Biblioteca padrão DataForge — módulos `Arcane.*`

Referência gerada a partir das assinaturas reais do código
(`python3 tools/gerar_doc_stdlib.py`). Todo módulo é carregado com `adopt`:

```dataforge
adopt Arcane.Math as Math
out Math.sqrt(16)
```

Cada módulo tem um **nome curto** equivalente (`adopt Math as M` funciona igual).

## Índice

| Módulo | Nome curto | Símbolos | Para quê |
|--------|-----------|----------|----------|
| [`Arcane.Math`](#arcanemath) | `Math` | 51 | Matemática, álgebra linear e estatística básica. |
| [`Arcane.Text`](#arcanetext) | `Text` | 58 | Manipulação de texto, formatação, tabelas e conversão de caixa. |
| [`Arcane.Analytics`](#arcaneanalytics) | `Analytics` | 65 | Análise de dados: estatística, regressão, clustering e gráficos ASCII. |
| [`Arcane.Functional`](#arcanefunctional) | `Functional` | 56 | Utilitários funcionais: composição, lentes, Maybe/Either, transdutores. |
| [`Arcane.Database`](#arcanedatabase) | `Database / DB` | 39 | Banco de dados SQLite: tabelas, consultas, migrações e importação. |
| [`Arcane.Test`](#arcanetest) | `Test` | 34 | Asserções e organização de suítes de teste. |
| [`Arcane.Regex`](#arcaneregex) | `Regex` | 32 | Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone). |
| [`Arcane.IO`](#arcaneio) | `IO` | 27 | Arquivos, diretórios, JSON, CSV e shell. |
| [`Arcane.Http`](#arcanehttp) | `Http / Server` | 17 | Servidor HTTP: rotas, middleware, JSON, arquivos estáticos. |
| [`Arcane.Async`](#arcaneasync) | `Async` | 46 | Promessas, filas, agendamento e execução concorrente. |
| [`Arcane.Data`](#arcanedata) | `Data` | 13 | DataFrames, séries e transformações tabulares. |
| [`Arcane.Web`](#arcaneweb) | `Web / Network` | 11 | Cliente HTTP, URL encoding e JSON. |
| [`Arcane.Cortex`](#arcanecortex) | `Cortex` | 5 | Blocos de rede neural, visão e NLP (implementações simplificadas). |

> Os nomes curtos e os aliases (`DB`, `Server`, `Network`) apontam para o mesmo
> módulo — use o que ficar mais legível.

## Exemplos rápidos

```dataforge
adopt Arcane.Math as Math
adopt Arcane.Text as Text
adopt Arcane.Analytics as An

out Math.sqrt(16)                       // 4.0
out Math.is_prime(97)                   // yes
out Text.slug("Ola Mundo")              // ola-mundo
out Text.box("Relatorio")               // caixa desenhada
out An.correlation([1,2,3], [2,4,6])    // 1.0
```


---

## Arcane.Math

Matemática, álgebra linear e estatística básica.

```dataforge
adopt Arcane.Math as Math
```

**Constantes**

| Nome | Valor |
|------|-------|
| `E` | `2.718281828459045` |
| `INF` | `inf` |
| `NAN` | `nan` |
| `PI` | `3.141592653589793` |
| `TAU` | `6.283185307179586` |
| `random` | `{'random': <built-in method random of Random objec…` |

**Funções (45)**

| Assinatura |
|------------|
| `abs(x)` |
| `acos(x)` |
| `asin(x)` |
| `atan(x)` |
| `atan2(y, x)` |
| `cbrt(x)` |
| `ceil(x)` |
| `clamp(value, min_val, max_val)` |
| `comb(n, k)` |
| `cos(x)` |
| `degrees(x)` |
| `determinant(matrix)` |
| `dot(a, b)` |
| `exp(x)` |
| `factorial(n)` |
| `fibonacci(n)` |
| `floor(x)` |
| `gcd(*integers)` |
| `hypot(…)` |
| `identity(n)` |
| `is_prime(n)` |
| `lcm(a, b)` |
| `lerp(a, b, t)` |
| `log(…)` |
| `log10(x)` |
| `log2(x)` |
| `map_range(value, in_min, in_max, out_min, out_max)` |
| `matrix(data)` |
| `max(…)` |
| `mean(data)` |
| `median(data)` |
| `min(…)` |
| `ones(rows, cols=None)` |
| `perm(n, k=None)` |
| `pow(x, y)` |
| `radians(x)` |
| `round(number, ndigits=None)` |
| `sin(x)` |
| `sqrt(x)` |
| `stdev(data)` |
| `sum(data)` |
| `tan(x)` |
| `transpose(matrix)` |
| `variance(data)` |
| `zeros(rows, cols=None)` |


---

## Arcane.Text

Manipulação de texto, formatação, tabelas e conversão de caixa.

```dataforge
adopt Arcane.Text as Text
```

**Funções (58)**

| Assinatura |
|------------|
| `align(lines, alignment='left', width=None)` |
| `box(text, style='single')` |
| `camel_case(text)` |
| `char_count(text, include_spaces=True)` |
| `closest(query, candidates, n=3)` |
| `constant_case(text)` |
| `currency(amount, symbol='$', decimals=2)` |
| `dedent(text)` |
| `diff(a, b)` |
| `distance(a, b)` |
| `dot_case(text)` |
| `escape_html(text)` |
| `escape_regex(text)` |
| `extract_emails(text)` |
| `extract_hashtags(text)` |
| `extract_links(text)` |
| `extract_mentions(text)` |
| `extract_numbers(text)` |
| `frequency(text)` |
| `fuzzy_match(query, text, threshold=0.6)` |
| `highlight(text, word, start='\x1b[1;33m', end='\x1b[0m')` |
| `indent(text, prefix='    ')` |
| `kebab_case(text)` |
| `line_count(text)` |
| `lorem(sentences=3)` |
| `ngrams(text, n=2)` |
| `normalize_whitespace(text)` |
| `number_format(n, decimals=2, thousands_sep=',', decimal_sep='.')` |
| `pad(text, width, fill=' ', align='left')` |
| `paragraph_count(text)` |
| `parse_csv(text, delimiter=',')` |
| `parse_ini(text)` |
| `parse_query(query_string)` |
| `pascal_case(text)` |
| `path_case(text)` |
| `random_string(length=16, charset='alphanumeric')` |
| `reading_time(text, wpm=200)` |
| `remove_accents(text)` |
| `render(template, context)` |
| `repeat_str(text, n, separator='')` |
| `sentence_case(text)` |
| `sentence_count(text)` |
| `similarity(a, b)` |
| `slug(text)` |
| `snake_case(text)` |
| `strip_ansi(text)` |
| `strip_html(text)` |
| `table(headers, rows, style='simple')` |
| `template(text)` |
| `title_case(text)` |
| `to_csv(data, delimiter=',')` |
| `to_query(params)` |
| `transliterate(text)` |
| `truncate(text, length=50, suffix='...')` |
| `unescape_html(text)` |
| `unified_diff(a, b, a_name='original', b_name='modified')` |
| `word_count(text)` |
| `wrap(text, width=80)` |


---

## Arcane.Analytics

Análise de dados: estatística, regressão, clustering e gráficos ASCII.

```dataforge
adopt Arcane.Analytics as Analytics
```

**Funções (65)**

| Assinatura |
|------------|
| `DataFrame(data=None, columns=None)` |
| `autocorrelation(data, lag=1)` |
| `bar_chart(data, labels=None, width=40, char='█')` |
| `bin_data(data, bins=5)` |
| `bootstrap(data, n_samples=1000, stat_fn=None)` |
| `box_plot(data, width=40)` |
| `correlation(x, y)` |
| `correlation_matrix(data_dict)` |
| `cosine_similarity(a, b)` |
| `covariance(x, y)` |
| `create_frame(data, columns=None)` |
| `cross_tab(data, row_fn, col_fn)` |
| `cumulative_sum(data)` |
| `data_types(data)` |
| `describe(data)` |
| `diff(data, periods=1)` |
| `euclidean_distance(a, b)` |
| `exponential_smoothing(data, alpha=0.3)` |
| `frequency_table(data)` |
| `from_csv(path, delimiter=',', has_header=True)` |
| `from_dict(d)` |
| `from_json(path)` |
| `from_records(records)` |
| `group_by(data, key_fn)` |
| `heatmap(matrix, row_labels=None, col_labels=None)` |
| `histogram(data, bins=10, width=40, char='█')` |
| `iqr(data)` |
| `kmeans(data, k=3, max_iter=100)` |
| `kurtosis(data)` |
| `lag(data, k=1)` |
| `line_chart(data, width=60, height=15)` |
| `linear_regression(x, y)` |
| `log_transform(data, base=None)` |
| `manhattan_distance(a, b)` |
| `mean(data)` |
| `median(data)` |
| `min_max_scale(data, feature_range=(0, 1))` |
| `missing_values(data)` |
| `mode(data)` |
| `moving_average(data, window=3)` |
| `normalize(data, low=0, high=1)` |
| `outliers(data, threshold=1.5)` |
| `percentile(data, p)` |
| `pivot_table(data, index_fn, value_fn, agg='sum')` |
| `predict_linear(model, x_val)` |
| `profile(data)` |
| `quartiles(data)` |
| `r_squared(x, y)` |
| `rank(data, method='average')` |
| `running_average(data)` |
| `sample(data, n=5, replace=False)` |
| `scatter_plot(x, y, width=40, height=20)` |
| `seasonality(data, period=7)` |
| `silhouette_score(data, labels)` |
| `skewness(data)` |
| `sparkline(data)` |
| `standardize(data)` |
| `stdev(data)` |
| `stratified_sample(data, labels, n_per_group=2)` |
| `summary(data)` |
| `trend(data)` |
| `unique_counts(data)` |
| `value_counts(data)` |
| `variance(data)` |
| `zscore(data)` |


---

## Arcane.Functional

Utilitários funcionais: composição, lentes, Maybe/Either, transdutores.

```dataforge
adopt Arcane.Functional as Functional
```

**Funções (56)**

| Assinatura |
|------------|
| `all_pass(*preds)` |
| `any_pass(*preds)` |
| `both(f, g)` |
| `chunk(n, collection)` |
| `complement(fn)` |
| `compose(*fns)` |
| `constantly(x)` |
| `curry(fn, arity=None)` |
| `drop_while(fn, collection)` |
| `either(f, g)` |
| `filter(fn, collection)` |
| `flat_map(fn, collection)` |
| `flip(fn)` |
| `frequencies(collection)` |
| `from_either(left_fn, right_fn, e)` |
| `from_maybe(default, m)` |
| `group_by(fn, collection)` |
| `identity(x)` |
| `index_by(fn, collection)` |
| `interleave(*collections)` |
| `into(target_type, xform, collection)` |
| `is_just(m)` |
| `is_left(e)` |
| `is_nothing(m)` |
| `is_right(e)` |
| `just(value)` |
| `juxt(*fns)` |
| `left(value)` |
| `lens(*keys)` |
| `map(fn, collection)` |
| `match(value, *cases)` |
| `maybe(value)` |
| `memoize(fn)` |
| `nothing()` |
| `once(fn)` |
| `over(lens, fn, obj)` |
| `partial(fn, *args)` |
| `partition_by(fn, collection)` |
| `pipe(*fns)` |
| `reduce(fn, collection, initial=None)` |
| `right(value)` |
| `scan(fn, collection, initial)` |
| `set_lens(lens, value, obj)` |
| `sort_by(fn, collection)` |
| `spread(fn)` |
| `take_while(fn, collection)` |
| `tap(fn, value)` |
| `thread_first(value, *fns)` |
| `thread_last(value, *fns)` |
| `trampoline(fn, *args)` |
| `transduce(xform, reducer, initial, collection)` |
| `try_catch(fn)` |
| `unique_by(fn, collection)` |
| `view(lens, obj)` |
| `when(*conditions)` |
| `zip_with(fn, *collections)` |


---

## Arcane.Database

Banco de dados SQLite: tabelas, consultas, migrações e importação.

```dataforge
adopt Arcane.Database as Database
```

**Funções (39)**

| Assinatura |
|------------|
| `Model(db, table, schema=None)` |
| `QueryBuilder(db, table)` |
| `add_column(db, table, name, col_type='TEXT')` |
| `backup(db, dest_path)` |
| `begin(db)` |
| `builder(db, table)` |
| `close(db)` |
| `columns(db, table)` |
| `commit(db)` |
| `connect(path)` |
| `count(db, table, where=None)` |
| `create_index(db, table, columns, unique=False, name=None)` |
| `create_model(db, table, schema)` |
| `create_table(db, name, schema)` |
| `database_size(db)` |
| `delete(db, table, where=None)` |
| `drop_table(db, name)` |
| `execute(db, sql, params=None)` |
| `execute_many(db, sql, params_list)` |
| `execute_script(db, script)` |
| `exists(db, table, where)` |
| `export_csv(db, table, path)` |
| `export_json(db, table, path)` |
| `import_csv(db, table, path, has_header=True)` |
| `import_json(db, table, path)` |
| `insert(db, table, data)` |
| `insert_many(db, table, records)` |
| `memory()` |
| `migrate(db, migrations)` |
| `query(db, sql, params=None)` |
| `query_one(db, sql, params=None)` |
| `rollback(db)` |
| `seed(db, table, records)` |
| `select(db, table, where=None, order_by=None, limit=None, columns=None)` |
| `table_exists(db, name)` |
| `table_info(db, table)` |
| `tables(db)` |
| `update(db, table, data, where)` |
| `vacuum(db)` |


---

## Arcane.Test

Asserções e organização de suítes de teste.

```dataforge
adopt Arcane.Test as Test
```

**Funções (34)**

| Assinatura |
|------------|
| `add_test(suite, name, spec)` |
| `assert_all(collection, predicate, msg=None)` |
| `assert_any(collection, predicate, msg=None)` |
| `assert_between(value, low, high, msg=None)` |
| `assert_close(actual, expected, tolerance=0.001, msg=None)` |
| `assert_contains(collection, item, msg=None)` |
| `assert_deep_eq(a, b, msg=None)` |
| `assert_empty(collection, msg=None)` |
| `assert_eq(actual, expected, msg=None)` |
| `assert_false(value, msg=None)` |
| `assert_greater(a, b, msg=None)` |
| `assert_instance(obj, blueprint_name, msg=None)` |
| `assert_keys(d, *expected_keys, msg=None)` |
| `assert_length(collection, expected, msg=None)` |
| `assert_less(a, b, msg=None)` |
| `assert_match(string, pattern, msg=None)` |
| `assert_neq(actual, expected, msg=None)` |
| `assert_not_contains(collection, item, msg=None)` |
| `assert_not_empty(collection, msg=None)` |
| `assert_not_void(value, msg=None)` |
| `assert_sorted(collection, reverse=False, msg=None)` |
| `assert_throws(func, msg=None)` |
| `assert_true(value, msg=None)` |
| `assert_type(value, expected_type, msg=None)` |
| `assert_unique(collection, msg=None)` |
| `assert_void(value, msg=None)` |
| `benchmark(func, iterations=1000)` |
| `describe(name, tests)` |
| `it(description, test_func)` |
| `mock(return_value=None)` |
| `run(suite, tests)` |
| `run_suite(suite)` |
| `spy(func)` |
| `suite(name='Test Suite')` |


---

## Arcane.Regex

Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone).

```dataforge
adopt Arcane.Regex as Regex
```

**Constantes**

| Nome | Valor |
|------|-------|
| `DOTALL` | `re.DOTALL` |
| `IGNORECASE` | `re.IGNORECASE` |
| `MULTILINE` | `re.MULTILINE` |
| `patterns` | `{'email': '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-z…` |

**Funções (28)**

| Assinatura |
|------------|
| `clean_whitespace(string)` |
| `compile(pattern, flags=0)` |
| `count(pattern, string, flags=0)` |
| `escape(string)` |
| `extract(pattern, string, flags=0)` |
| `extract_emails(string)` |
| `extract_numbers(string)` |
| `extract_urls(string)` |
| `extract_words(string)` |
| `findall(pattern, string, flags=0)` |
| `finditer(pattern, string, flags=0)` |
| `is_cnpj(string)` |
| `is_cpf(string)` |
| `is_date(string)` |
| `is_email(string)` |
| `is_ipv4(string)` |
| `is_phone(string)` |
| `is_url(string)` |
| `mask(string, pattern, mask_char='*')` |
| `match(pattern, string, flags=0)` |
| `remove_html(string)` |
| `replace_all(pattern, repl, string)` |
| `search(pattern, string, flags=0)` |
| `split(pattern, string, maxsplit=0, flags=0)` |
| `sub(pattern, repl, string, count=0, flags=0)` |
| `subn(pattern, repl, string, count=0, flags=0)` |
| `test(pattern, string, flags=0)` |
| `word_count(string)` |


---

## Arcane.IO

Arquivos, diretórios, JSON, CSV e shell.

```dataforge
adopt Arcane.IO as IO
```

**Funções (27)**

| Assinatura |
|------------|
| `abs(path)` |
| `append(path, content)` |
| `basename(path)` |
| `copy(src, dst)` |
| `cwd()` |
| `delete(path)` |
| `dirname(path)` |
| `exists(path)` |
| `ext(path)` |
| `file_exists(path)` |
| `join(*parts)` |
| `list_dir(path='.')` |
| `listdir(path='.')` |
| `mkdir(path)` |
| `open(path, mode='r')` |
| `path(path)` |
| `read(path)` |
| `read_csv(path)` |
| `read_file(path)` |
| `read_json(path)` |
| `rename(old, new)` |
| `shell(command)` |
| `size(path)` |
| `write(path, content)` |
| `write_csv(path, data)` |
| `write_file(path, content)` |
| `write_json(path, data, indent=2)` |


---

## Arcane.Http

Servidor HTTP: rotas, middleware, JSON, arquivos estáticos.

```dataforge
adopt Arcane.Http as Http
```

**Funções (17)**

| Assinatura |
|------------|
| `cors(app)` |
| `create(name='DataForge App')` |
| `delete(app, path, handler)` |
| `get(app, path, handler)` |
| `html_response(html, status=200)` |
| `json_parser(app)` |
| `json_response(data, status=200)` |
| `listen(app, port=3000, host='0.0.0.0')` |
| `logger(app)` |
| `patch(app, path, handler)` |
| `post(app, path, handler)` |
| `put(app, path, handler)` |
| `route(app, method, path, handler)` |
| `static(app, directory)` |
| `stop(app)` |
| `templates(app, directory)` |
| `use(app, middleware)` |


---

## Arcane.Async

Promessas, filas, agendamento e execução concorrente.

```dataforge
adopt Arcane.Async as Async
```

**Funções (46)**

| Assinatura |
|------------|
| `all(promises)` |
| `any(promises)` |
| `batch(fn)` |
| `buffer_op(size)` |
| `catch(promise, callback)` |
| `channel(buffer_size=0)` |
| `combine_latest(*observables)` |
| `computed(signals, fn)` |
| `debounce_op(ms)` |
| `delay(ms, fn=None)` |
| `distinct_op()` |
| `effect(signals, fn)` |
| `emit(emitter, event, *data)` |
| `emit_event(emitter, event, *data)` |
| `emitter()` |
| `event_emitter()` |
| `filter_op(fn)` |
| `from_list(lst)` |
| `interval(ms, count=10)` |
| `map_op(fn)` |
| `merge(*observables)` |
| `observable(producer=None)` |
| `of(*values)` |
| `off(emitter, event, callback=None)` |
| `on(emitter, event, callback)` |
| `once_event(emitter, event, callback)` |
| `parallel(*fns)` |
| `pipe_stream(observable, *operators)` |
| `promise(executor)` |
| `race(promises)` |
| `receive(ch)` |
| `reject(error)` |
| `resolve(value)` |
| `retry_task(fn, max_retries=3, delay_ms=100)` |
| `scan_op(fn, initial)` |
| `send(ch, value)` |
| `sequential(*fns)` |
| `settled(promises)` |
| `signal(initial_value)` |
| `skip_op(n)` |
| `subject()` |
| `subscribe(observable, callback)` |
| `take_op(n)` |
| `task(fn)` |
| `then(promise, callback)` |
| `timeout(ms, fn)` |


---

## Arcane.Data

DataFrames, séries e transformações tabulares.

```dataforge
adopt Arcane.Data as Data
```

**Funções (13)**

| Assinatura |
|------------|
| `Frame(data=None, columns=None)` |
| `correlate(x, y)` |
| `describe(data)` |
| `group_by(data, key_func)` |
| `merge(left, right, on)` |
| `normalize(data, min_val=0, max_val=1)` |
| `one_hot(labels)` |
| `pivot(data, index_col, value_col, agg='sum')` |
| `read_csv(path, header=True)` |
| `read_json(path)` |
| `series(data, name='series')` |
| `split(data, ratio=0.8)` |
| `standardize(data)` |


---

## Arcane.Web

Cliente HTTP, URL encoding e JSON.

```dataforge
adopt Arcane.Web as Web
```

**Funções (11)**

| Assinatura |
|------------|
| `check(user_id=None)` |
| `close()` |
| `decode_url(text)` |
| `encode_url(text)` |
| `get(url, headers=None)` |
| `json_parse(text)` |
| `json_stringify(obj, indent=None)` |
| `post(url, data=None, headers=None)` |
| `request(url, method='GET', data=None, headers=None)` |
| `serve(port=8080, host='0.0.0.0')` |
| `socket(host, port)` |


---

## Arcane.Cortex

Blocos de rede neural, visão e NLP (implementações simplificadas).

```dataforge
adopt Arcane.Cortex as Cortex
```

**Constantes**

| Nome | Valor |
|------|-------|
| `neural` | `{'Sequential': <class 'dataforge.stdlib.arcane_cor…` |
| `nlp` | `{'tokenize': <function ArcaneCortex._nlp.<locals>.…` |
| `vision` | `{'load_image': <function ArcaneCortex._vision.<loc…` |

**Funções (2)**

| Assinatura |
|------------|
| `accuracy(predictions, labels)` |
| `evaluate(model, test_data)` |
