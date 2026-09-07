import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Analytics",
  description: "Análise de dados: estatística, regressão, clustering e gráficos.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Analytics as An

x := [1, 2, 3, 4, 5]
y := [2, 4, 6, 8, 10]

out round(An.correlation(x, y), 4)
out An.quartiles(x)
out An.outliers([10, 11, 12, 200])

modelo := An.linear_regression(x, y)
out round(modelo["slope"], 2), round(An.predict_linear(modelo, 6), 2)`, title: `exemplo` },
  {"h2": "Funções (65)"},
  {"table": {"head": ["Assinatura"], "rows": [["`DataFrame(data=None, columns=None)`"], ["`autocorrelation(data, lag=1)`"], ["`bar_chart(data, labels=None, width=40, char='█')`"], ["`bin_data(data, bins=5)`"], ["`bootstrap(data, n_samples=1000, stat_fn=None)`"], ["`box_plot(data, width=40)`"], ["`correlation(x, y)`"], ["`correlation_matrix(data_dict)`"], ["`cosine_similarity(a, b)`"], ["`covariance(x, y)`"], ["`create_frame(data, columns=None)`"], ["`cross_tab(data, row_fn, col_fn)`"], ["`cumulative_sum(data)`"], ["`data_types(data)`"], ["`describe(data)`"], ["`diff(data, periods=1)`"], ["`euclidean_distance(a, b)`"], ["`exponential_smoothing(data, alpha=0.3)`"], ["`frequency_table(data)`"], ["`from_csv(path, delimiter=',', has_header=True)`"], ["`from_dict(d)`"], ["`from_json(path)`"], ["`from_records(records)`"], ["`group_by(data, key_fn)`"], ["`heatmap(matrix, row_labels=None, col_labels=None)`"], ["`histogram(data, bins=10, width=40, char='█')`"], ["`iqr(data)`"], ["`kmeans(data, k=3, max_iter=100)`"], ["`kurtosis(data)`"], ["`lag(data, k=1)`"], ["`line_chart(data, width=60, height=15)`"], ["`linear_regression(x, y)`"], ["`log_transform(data, base=None)`"], ["`manhattan_distance(a, b)`"], ["`mean(data)`"], ["`median(data)`"], ["`min_max_scale(data, feature_range=(0, 1))`"], ["`missing_values(data)`"], ["`mode(data)`"], ["`moving_average(data, window=3)`"], ["`normalize(data, low=0, high=1)`"], ["`outliers(data, threshold=1.5)`"], ["`percentile(data, p)`"], ["`pivot_table(data, index_fn, value_fn, agg='sum')`"], ["`predict_linear(model, x_val)`"], ["`profile(data)`"], ["`quartiles(data)`"], ["`r_squared(x, y)`"], ["`rank(data, method='average')`"], ["`running_average(data)`"], ["`sample(data, n=5, replace=False)`"], ["`scatter_plot(x, y, width=40, height=20)`"], ["`seasonality(data, period=7)`"], ["`silhouette_score(data, labels)`"], ["`skewness(data)`"], ["`sparkline(data)`"], ["`standardize(data)`"], ["`stdev(data)`"], ["`stratified_sample(data, labels, n_per_group=2)`"], ["`summary(data)`"], ["`trend(data)`"], ["`unique_counts(data)`"], ["`value_counts(data)`"], ["`variance(data)`"], ["`zscore(data)`"]]}},
];

const headings = [{ id: 'funcoes-65', text: "Funções (65)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Analytics"}
      description={"Análise de dados: estatística, regressão, clustering e gráficos."}
      href={"/biblioteca/analytics"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
