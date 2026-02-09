"""
Arcane.Analytics - Advanced Data Analysis Module
Statistical analysis, data visualization (text-based), pivot tables,
time series, linear regression, clustering, and data profiling.
"""

import math
import statistics
import csv
import json
from collections import Counter, defaultdict


class ArcaneAnalytics:
    """Advanced data analytics toolkit for DataForge."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Analytics",

            # ── DataFrame ───────────────────────────────────
            "DataFrame": AnalyticsFrame,
            "create_frame": cls._create_frame,
            "from_csv": cls._from_csv,
            "from_json": cls._from_json,
            "from_dict": cls._from_dict,
            "from_records": cls._from_records,

            # ── Estatísticas Descritivas ────────────────────
            "describe": cls._describe,
            "summary": cls._summary,
            "mean": cls._mean,
            "median": cls._median,
            "mode": cls._mode,
            "stdev": cls._stdev,
            "variance": cls._variance,
            "percentile": cls._percentile,
            "quartiles": cls._quartiles,
            "iqr": cls._iqr,
            "skewness": cls._skewness,
            "kurtosis": cls._kurtosis,
            "zscore": cls._zscore,
            "outliers": cls._outliers,

            # ── Correlação & Regressão ──────────────────────
            "correlation": cls._correlation,
            "covariance": cls._covariance,
            "linear_regression": cls._linear_regression,
            "predict_linear": cls._predict_linear,
            "r_squared": cls._r_squared,
            "correlation_matrix": cls._correlation_matrix,

            # ── Agregação & Agrupamento ─────────────────────
            "group_by": cls._group_by,
            "pivot_table": cls._pivot_table,
            "cross_tab": cls._cross_tab,
            "frequency_table": cls._frequency_table,
            "cumulative_sum": cls._cumulative_sum,
            "running_average": cls._running_average,
            "moving_average": cls._moving_average,

            # ── Normalização & Transformação ────────────────
            "normalize": cls._normalize,
            "standardize": cls._standardize,
            "min_max_scale": cls._min_max_scale,
            "log_transform": cls._log_transform,
            "bin_data": cls._bin_data,
            "rank": cls._rank,

            # ── Séries Temporais ────────────────────────────
            "trend": cls._trend,
            "seasonality": cls._seasonality,
            "diff": cls._diff,
            "lag": cls._lag,
            "autocorrelation": cls._autocorrelation,
            "exponential_smoothing": cls._exponential_smoothing,

            # ── Clustering (K-Means simples) ────────────────
            "kmeans": cls._kmeans,
            "silhouette_score": cls._silhouette_score,

            # ── Visualização Texto ──────────────────────────
            "bar_chart": cls._bar_chart,
            "histogram": cls._histogram,
            "line_chart": cls._line_chart,
            "scatter_plot": cls._scatter_plot,
            "heatmap": cls._heatmap,
            "box_plot": cls._box_plot,
            "sparkline": cls._sparkline,

            # ── Profiling & Qualidade ───────────────────────
            "profile": cls._profile,
            "missing_values": cls._missing_values,
            "data_types": cls._data_types,
            "unique_counts": cls._unique_counts,
            "value_counts": cls._value_counts,

            # ── Amostragem ──────────────────────────────────
            "sample": cls._sample,
            "stratified_sample": cls._stratified_sample,
            "bootstrap": cls._bootstrap,

            # ── Distância & Similaridade ────────────────────
            "euclidean_distance": cls._euclidean_distance,
            "manhattan_distance": cls._manhattan_distance,
            "cosine_similarity": cls._cosine_similarity,
        }

    # ═══════════════════════════════════════════════════════
    #  DataFrame Factory
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _create_frame(data, columns=None):
        return AnalyticsFrame(data, columns)

    @staticmethod
    def _from_csv(path, delimiter=",", has_header=True):
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
        if has_header and rows:
            return AnalyticsFrame(rows[1:], rows[0])
        return AnalyticsFrame(rows)

    @staticmethod
    def _from_json(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list) and data and isinstance(data[0], dict):
            cols = list(data[0].keys())
            rows = [[row.get(c) for c in cols] for row in data]
            return AnalyticsFrame(rows, cols)
        return data

    @staticmethod
    def _from_dict(d):
        cols = list(d.keys())
        n = max(len(v) for v in d.values()) if d else 0
        rows = []
        for i in range(n):
            row = [d[c][i] if i < len(d[c]) else None for c in cols]
            rows.append(row)
        return AnalyticsFrame(rows, cols)

    @staticmethod
    def _from_records(records):
        if not records:
            return AnalyticsFrame([])
        cols = list(records[0].keys())
        rows = [[r.get(c) for c in cols] for r in records]
        return AnalyticsFrame(rows, cols)

    # ═══════════════════════════════════════════════════════
    #  Estatísticas Descritivas
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _describe(data):
        nums = [x for x in data if isinstance(x, (int, float))]
        if not nums:
            return {"count": 0, "type": "non-numeric"}
        n = len(nums)
        s = sorted(nums)
        mean = sum(nums) / n
        var = sum((x - mean) ** 2 for x in nums) / max(n - 1, 1)
        return {
            "count": n,
            "mean": round(mean, 4),
            "std": round(math.sqrt(var), 4),
            "min": s[0],
            "25%": s[n // 4],
            "50%": s[n // 2],
            "75%": s[(3 * n) // 4],
            "max": s[-1],
            "sum": sum(nums),
            "variance": round(var, 4),
        }

    @staticmethod
    def _summary(data):
        nums = [x for x in data if isinstance(x, (int, float))]
        n = len(nums)
        if n == 0:
            return {"count": len(data), "non_numeric": len(data)}
        mean = sum(nums) / n
        return {
            "count": n,
            "mean": round(mean, 4),
            "min": min(nums),
            "max": max(nums),
            "range": max(nums) - min(nums),
            "sum": sum(nums),
        }

    @staticmethod
    def _mean(data):
        nums = [x for x in data if isinstance(x, (int, float))]
        return sum(nums) / len(nums) if nums else 0

    @staticmethod
    def _median(data):
        nums = sorted(x for x in data if isinstance(x, (int, float)))
        n = len(nums)
        if n == 0:
            return 0
        if n % 2 == 1:
            return nums[n // 2]
        return (nums[n // 2 - 1] + nums[n // 2]) / 2

    @staticmethod
    def _mode(data):
        c = Counter(data)
        if not c:
            return None
        max_count = max(c.values())
        modes = [k for k, v in c.items() if v == max_count]
        return modes[0] if len(modes) == 1 else modes

    @staticmethod
    def _stdev(data):
        nums = [x for x in data if isinstance(x, (int, float))]
        if len(nums) < 2:
            return 0
        mean = sum(nums) / len(nums)
        return math.sqrt(sum((x - mean) ** 2 for x in nums) / (len(nums) - 1))

    @staticmethod
    def _variance(data):
        nums = [x for x in data if isinstance(x, (int, float))]
        if len(nums) < 2:
            return 0
        mean = sum(nums) / len(nums)
        return sum((x - mean) ** 2 for x in nums) / (len(nums) - 1)

    @staticmethod
    def _percentile(data, p):
        s = sorted(x for x in data if isinstance(x, (int, float)))
        if not s:
            return 0
        k = (len(s) - 1) * (p / 100)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return s[int(k)]
        return s[int(f)] * (c - k) + s[int(c)] * (k - f)

    @staticmethod
    def _quartiles(data):
        s = sorted(x for x in data if isinstance(x, (int, float)))
        n = len(s)
        if n == 0:
            return {"Q1": 0, "Q2": 0, "Q3": 0}
        return {
            "Q1": s[n // 4],
            "Q2": s[n // 2],
            "Q3": s[(3 * n) // 4],
        }

    @staticmethod
    def _iqr(data):
        s = sorted(x for x in data if isinstance(x, (int, float)))
        n = len(s)
        if n == 0:
            return 0
        return s[(3 * n) // 4] - s[n // 4]

    @staticmethod
    def _skewness(data):
        nums = [x for x in data if isinstance(x, (int, float))]
        n = len(nums)
        if n < 3:
            return 0
        mean = sum(nums) / n
        std = math.sqrt(sum((x - mean) ** 2 for x in nums) / n)
        if std == 0:
            return 0
        return (n / ((n - 1) * (n - 2))) * sum(((x - mean) / std) ** 3 for x in nums)

    @staticmethod
    def _kurtosis(data):
        nums = [x for x in data if isinstance(x, (int, float))]
        n = len(nums)
        if n < 4:
            return 0
        mean = sum(nums) / n
        std = math.sqrt(sum((x - mean) ** 2 for x in nums) / n)
        if std == 0:
            return 0
        return (sum(((x - mean) / std) ** 4 for x in nums) / n) - 3

    @staticmethod
    def _zscore(data):
        nums = [x for x in data if isinstance(x, (int, float))]
        if len(nums) < 2:
            return [0] * len(nums)
        mean = sum(nums) / len(nums)
        std = math.sqrt(sum((x - mean) ** 2 for x in nums) / len(nums))
        if std == 0:
            return [0] * len(nums)
        return [round((x - mean) / std, 4) for x in nums]

    @staticmethod
    def _outliers(data, threshold=1.5):
        nums = sorted(x for x in data if isinstance(x, (int, float)))
        n = len(nums)
        if n < 4:
            return []
        q1, q3 = nums[n // 4], nums[(3 * n) // 4]
        iqr = q3 - q1
        lower = q1 - threshold * iqr
        upper = q3 + threshold * iqr
        return [x for x in nums if x < lower or x > upper]

    # ═══════════════════════════════════════════════════════
    #  Correlação & Regressão
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _correlation(x, y):
        n = min(len(x), len(y))
        if n < 2:
            return 0
        mx = sum(x[:n]) / n
        my = sum(y[:n]) / n
        cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
        sx = math.sqrt(sum((xi - mx) ** 2 for xi in x[:n]))
        sy = math.sqrt(sum((yi - my) ** 2 for yi in y[:n]))
        if sx == 0 or sy == 0:
            return 0
        return round(cov / (sx * sy), 6)

    @staticmethod
    def _covariance(x, y):
        n = min(len(x), len(y))
        if n < 2:
            return 0
        mx = sum(x[:n]) / n
        my = sum(y[:n]) / n
        return sum((x[i] - mx) * (y[i] - my) for i in range(n)) / (n - 1)

    @staticmethod
    def _linear_regression(x, y):
        n = min(len(x), len(y))
        if n < 2:
            return {"slope": 0, "intercept": 0}
        mx = sum(x[:n]) / n
        my = sum(y[:n]) / n
        num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
        den = sum((x[i] - mx) ** 2 for i in range(n))
        if den == 0:
            return {"slope": 0, "intercept": my}
        slope = num / den
        intercept = my - slope * mx
        return {"slope": round(slope, 6), "intercept": round(intercept, 6)}

    @staticmethod
    def _predict_linear(model, x_val):
        if isinstance(x_val, list):
            return [round(model["slope"] * xi + model["intercept"], 4) for xi in x_val]
        return round(model["slope"] * x_val + model["intercept"], 4)

    @staticmethod
    def _r_squared(x, y):
        n = min(len(x), len(y))
        if n < 2:
            return 0
        mx = sum(x[:n]) / n
        my = sum(y[:n]) / n
        num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
        den = sum((x[i] - mx) ** 2 for i in range(n))
        if den == 0:
            return 0
        slope = num / den
        intercept = my - slope * mx
        ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        ss_tot = sum((y[i] - my) ** 2 for i in range(n))
        if ss_tot == 0:
            return 1
        return round(1 - ss_res / ss_tot, 6)

    @staticmethod
    def _correlation_matrix(data_dict):
        keys = list(data_dict.keys())
        matrix = {}
        for k1 in keys:
            matrix[k1] = {}
            for k2 in keys:
                x, y = data_dict[k1], data_dict[k2]
                n = min(len(x), len(y))
                if n < 2:
                    matrix[k1][k2] = 0
                    continue
                mx = sum(x[:n]) / n
                my = sum(y[:n]) / n
                cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
                sx = math.sqrt(sum((xi - mx) ** 2 for xi in x[:n]))
                sy = math.sqrt(sum((yi - my) ** 2 for yi in y[:n]))
                matrix[k1][k2] = round(cov / (sx * sy), 4) if sx and sy else 0
        return matrix

    # ═══════════════════════════════════════════════════════
    #  Agregação & Agrupamento
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _group_by(data, key_fn):
        groups = defaultdict(list)
        for item in data:
            k = key_fn(item)
            groups[k].append(item)
        return dict(groups)

    @staticmethod
    def _pivot_table(data, index_fn, value_fn, agg="sum"):
        groups = defaultdict(list)
        for item in data:
            groups[index_fn(item)].append(value_fn(item))
        agg_fn = {
            "sum": sum, "mean": lambda v: sum(v) / len(v),
            "count": len, "min": min, "max": max,
        }.get(agg, sum)
        return {k: round(agg_fn(v), 4) for k, v in groups.items()}

    @staticmethod
    def _cross_tab(data, row_fn, col_fn):
        table = defaultdict(lambda: defaultdict(int))
        for item in data:
            table[row_fn(item)][col_fn(item)] += 1
        return {k: dict(v) for k, v in table.items()}

    @staticmethod
    def _frequency_table(data):
        c = Counter(data)
        total = len(data)
        return {k: {"count": v, "frequency": round(v / total, 4)} for k, v in c.most_common()}

    @staticmethod
    def _cumulative_sum(data):
        result = []
        total = 0
        for x in data:
            total += x
            result.append(total)
        return result

    @staticmethod
    def _running_average(data):
        result = []
        total = 0
        for i, x in enumerate(data, 1):
            total += x
            result.append(round(total / i, 4))
        return result

    @staticmethod
    def _moving_average(data, window=3):
        result = []
        for i in range(len(data)):
            start = max(0, i - window + 1)
            chunk = data[start:i + 1]
            result.append(round(sum(chunk) / len(chunk), 4))
        return result

    # ═══════════════════════════════════════════════════════
    #  Normalização & Transformação
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _normalize(data, low=0, high=1):
        mn, mx = min(data), max(data)
        if mx == mn:
            return [low] * len(data)
        return [round(low + (x - mn) / (mx - mn) * (high - low), 6) for x in data]

    @staticmethod
    def _standardize(data):
        mean = sum(data) / len(data)
        std = math.sqrt(sum((x - mean) ** 2 for x in data) / len(data))
        if std == 0:
            return [0.0] * len(data)
        return [round((x - mean) / std, 6) for x in data]

    @staticmethod
    def _min_max_scale(data, feature_range=(0, 1)):
        mn, mx = min(data), max(data)
        lo, hi = feature_range
        if mx == mn:
            return [lo] * len(data)
        return [round(lo + (x - mn) / (mx - mn) * (hi - lo), 6) for x in data]

    @staticmethod
    def _log_transform(data, base=None):
        if base:
            return [round(math.log(max(x, 1e-10), base), 6) for x in data]
        return [round(math.log(max(x, 1e-10)), 6) for x in data]

    @staticmethod
    def _bin_data(data, bins=5):
        mn, mx = min(data), max(data)
        width = (mx - mn) / bins if mx != mn else 1
        result = []
        for x in data:
            b = min(int((x - mn) / width), bins - 1)
            result.append(b)
        return result

    @staticmethod
    def _rank(data, method="average"):
        indexed = sorted(enumerate(data), key=lambda p: p[1])
        ranks = [0] * len(data)
        i = 0
        while i < len(indexed):
            j = i
            while j < len(indexed) and indexed[j][1] == indexed[i][1]:
                j += 1
            if method == "average":
                avg_rank = (i + j + 1) / 2
                for k in range(i, j):
                    ranks[indexed[k][0]] = avg_rank
            elif method == "min":
                for k in range(i, j):
                    ranks[indexed[k][0]] = i + 1
            elif method == "max":
                for k in range(i, j):
                    ranks[indexed[k][0]] = j
            else:
                for k in range(i, j):
                    ranks[indexed[k][0]] = k + 1
            i = j
        return ranks

    # ═══════════════════════════════════════════════════════
    #  Séries Temporais
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _trend(data):
        n = len(data)
        if n < 2:
            return {"direction": "flat", "slope": 0}
        x = list(range(n))
        mx = sum(x) / n
        my = sum(data) / n
        num = sum((x[i] - mx) * (data[i] - my) for i in range(n))
        den = sum((x[i] - mx) ** 2 for i in range(n))
        slope = num / den if den else 0
        direction = "up" if slope > 0.01 else ("down" if slope < -0.01 else "flat")
        return {"direction": direction, "slope": round(slope, 6)}

    @staticmethod
    def _seasonality(data, period=7):
        if len(data) < period * 2:
            return {"detected": False}
        avgs = []
        for offset in range(period):
            vals = [data[i] for i in range(offset, len(data), period)]
            avgs.append(sum(vals) / len(vals))
        overall = sum(data) / len(data)
        strength = max(abs(a - overall) for a in avgs) / max(abs(overall), 1)
        return {"detected": strength > 0.1, "period": period, "strength": round(strength, 4), "pattern": [round(a, 2) for a in avgs]}

    @staticmethod
    def _diff(data, periods=1):
        return [data[i] - data[i - periods] for i in range(periods, len(data))]

    @staticmethod
    def _lag(data, k=1):
        return [None] * k + data[:-k] if k > 0 else data[-k:] + [None] * abs(k)

    @staticmethod
    def _autocorrelation(data, lag=1):
        n = len(data)
        if n <= lag:
            return 0
        mean = sum(data) / n
        c0 = sum((data[i] - mean) ** 2 for i in range(n))
        if c0 == 0:
            return 0
        ck = sum((data[i] - mean) * (data[i - lag] - mean) for i in range(lag, n))
        return round(ck / c0, 6)

    @staticmethod
    def _exponential_smoothing(data, alpha=0.3):
        if not data:
            return []
        result = [data[0]]
        for i in range(1, len(data)):
            result.append(round(alpha * data[i] + (1 - alpha) * result[-1], 6))
        return result

    # ═══════════════════════════════════════════════════════
    #  K-Means Clustering
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _kmeans(data, k=3, max_iter=100):
        import random
        if not data or k <= 0:
            return {"centroids": [], "labels": [], "iterations": 0}

        dim = len(data[0]) if isinstance(data[0], (list, tuple)) else 1
        points = [list(p) if isinstance(p, (list, tuple)) else [p] for p in data]

        centroids = random.sample(points, min(k, len(points)))
        labels = [0] * len(points)

        def dist(a, b):
            return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(len(a))))

        for iteration in range(max_iter):
            # Assign
            new_labels = []
            for p in points:
                dists = [dist(p, c) for c in centroids]
                new_labels.append(dists.index(min(dists)))

            if new_labels == labels:
                break
            labels = new_labels

            # Update centroids
            for j in range(k):
                cluster = [points[i] for i in range(len(points)) if labels[i] == j]
                if cluster:
                    centroids[j] = [round(sum(c[d] for c in cluster) / len(cluster), 6) for d in range(dim)]

        return {
            "centroids": centroids,
            "labels": labels,
            "iterations": iteration + 1,
            "k": k,
        }

    @staticmethod
    def _silhouette_score(data, labels):
        n = len(data)
        if n < 2:
            return 0
        points = [list(p) if isinstance(p, (list, tuple)) else [p] for p in data]

        def dist(a, b):
            return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(len(a))))

        scores = []
        unique_labels = list(set(labels))
        if len(unique_labels) < 2:
            return 0

        for i in range(n):
            same = [j for j in range(n) if labels[j] == labels[i] and j != i]
            a_i = sum(dist(points[i], points[j]) for j in same) / max(len(same), 1)

            b_i = float("inf")
            for lbl in unique_labels:
                if lbl == labels[i]:
                    continue
                others = [j for j in range(n) if labels[j] == lbl]
                if others:
                    avg_dist = sum(dist(points[i], points[j]) for j in others) / len(others)
                    b_i = min(b_i, avg_dist)

            if max(a_i, b_i) == 0:
                scores.append(0)
            else:
                scores.append((b_i - a_i) / max(a_i, b_i))

        return round(sum(scores) / len(scores), 4)

    # ═══════════════════════════════════════════════════════
    #  Visualização em Texto
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _bar_chart(data, labels=None, width=40, char="█"):
        if not data:
            return ""
        mx = max(abs(x) for x in data) or 1
        lines = []
        for i, val in enumerate(data):
            label = str(labels[i]) if labels and i < len(labels) else str(i)
            bar_len = int(abs(val) / mx * width)
            bar = char * bar_len
            lines.append(f"{label:>12} | {bar} {val}")
        return "\n".join(lines)

    @staticmethod
    def _histogram(data, bins=10, width=40, char="█"):
        if not data:
            return ""
        mn, mx = min(data), max(data)
        if mn == mx:
            return f"[{mn}] | {'█' * width} ({len(data)})"
        bin_width = (mx - mn) / bins
        counts = [0] * bins
        for x in data:
            b = min(int((x - mn) / bin_width), bins - 1)
            counts[b] += 1
        max_count = max(counts) or 1
        lines = []
        for i in range(bins):
            lo = round(mn + i * bin_width, 2)
            hi = round(lo + bin_width, 2)
            bar_len = int(counts[i] / max_count * width)
            lines.append(f"[{lo:>7.2f}-{hi:>7.2f}] | {'█' * bar_len} ({counts[i]})")
        return "\n".join(lines)

    @staticmethod
    def _line_chart(data, width=60, height=15):
        if not data:
            return ""
        mn, mx = min(data), max(data)
        rng = mx - mn or 1
        lines = []
        for row in range(height, -1, -1):
            threshold = mn + (row / height) * rng
            line_chars = []
            for val in data[:width]:
                if abs(val - threshold) < rng / (height * 2):
                    line_chars.append("●")
                elif val >= threshold:
                    line_chars.append("│")
                else:
                    line_chars.append(" ")
            label = f"{threshold:>8.1f}"
            lines.append(f"{label} |{''.join(line_chars)}")
        lines.append("         +" + "─" * min(len(data), width))
        return "\n".join(lines)

    @staticmethod
    def _scatter_plot(x, y, width=40, height=20):
        if not x or not y:
            return ""
        n = min(len(x), len(y))
        x_mn, x_mx = min(x[:n]), max(x[:n])
        y_mn, y_mx = min(y[:n]), max(y[:n])
        x_rng = x_mx - x_mn or 1
        y_rng = y_mx - y_mn or 1
        grid = [[" " for _ in range(width)] for _ in range(height)]
        for i in range(n):
            col = min(int((x[i] - x_mn) / x_rng * (width - 1)), width - 1)
            row = min(int((y[i] - y_mn) / y_rng * (height - 1)), height - 1)
            grid[height - 1 - row][col] = "●"
        lines = []
        for row in grid:
            lines.append("│" + "".join(row))
        lines.append("└" + "─" * width)
        return "\n".join(lines)

    @staticmethod
    def _heatmap(matrix, row_labels=None, col_labels=None):
        shades = " ░▒▓█"
        if not matrix:
            return ""
        flat = [v for row in matrix for v in row if isinstance(v, (int, float))]
        mn = min(flat) if flat else 0
        mx = max(flat) if flat else 1
        rng = mx - mn or 1
        lines = []
        if col_labels:
            lines.append("     " + " ".join(f"{c:>4}" for c in col_labels))
        for i, row in enumerate(matrix):
            label = str(row_labels[i])[:4] if row_labels and i < len(row_labels) else f"{i:>4}"
            cells = []
            for v in row:
                idx = min(int((v - mn) / rng * (len(shades) - 1)), len(shades) - 1)
                cells.append(shades[idx] * 2)
            lines.append(f"{label} |{'  '.join(cells)}")
        return "\n".join(lines)

    @staticmethod
    def _box_plot(data, width=40):
        s = sorted(data)
        n = len(s)
        if n == 0:
            return ""
        mn, mx = s[0], s[-1]
        q1, q2, q3 = s[n // 4], s[n // 2], s[(3 * n) // 4]
        rng = mx - mn or 1

        def pos(v):
            return int((v - mn) / rng * width)

        line = [" "] * (width + 1)
        line[pos(mn)] = "├"
        line[pos(mx)] = "┤"
        for i in range(pos(mn) + 1, pos(q1)):
            line[i] = "─"
        for i in range(pos(q1), pos(q3) + 1):
            line[i] = "█"
        line[pos(q2)] = "│"
        for i in range(pos(q3) + 1, pos(mx)):
            line[i] = "─"
        return f"Min={mn}  Q1={q1}  Med={q2}  Q3={q3}  Max={mx}\n{''.join(line)}"

    @staticmethod
    def _sparkline(data):
        if not data:
            return ""
        blocks = "▁▂▃▄▅▆▇█"
        mn, mx = min(data), max(data)
        rng = mx - mn or 1
        return "".join(blocks[min(int((x - mn) / rng * 7), 7)] for x in data)

    # ═══════════════════════════════════════════════════════
    #  Profiling & Qualidade
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _profile(data):
        total = len(data)
        types = Counter(type(x).__name__ for x in data)
        missing = sum(1 for x in data if x is None or x == "")
        unique = len(set(str(x) for x in data))
        return {
            "total": total,
            "missing": missing,
            "unique": unique,
            "completeness": round((total - missing) / max(total, 1) * 100, 2),
            "types": dict(types),
        }

    @staticmethod
    def _missing_values(data):
        return sum(1 for x in data if x is None or x == "" or (isinstance(x, float) and math.isnan(x)))

    @staticmethod
    def _data_types(data):
        return dict(Counter(type(x).__name__ for x in data))

    @staticmethod
    def _unique_counts(data):
        return len(set(str(x) for x in data))

    @staticmethod
    def _value_counts(data):
        return dict(Counter(data).most_common())

    # ═══════════════════════════════════════════════════════
    #  Amostragem
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _sample(data, n=5, replace=False):
        import random
        if replace:
            return [random.choice(data) for _ in range(n)]
        return random.sample(data, min(n, len(data)))

    @staticmethod
    def _stratified_sample(data, labels, n_per_group=2):
        import random
        groups = defaultdict(list)
        for item, label in zip(data, labels):
            groups[label].append(item)
        result = []
        for grp in groups.values():
            result.extend(random.sample(grp, min(n_per_group, len(grp))))
        return result

    @staticmethod
    def _bootstrap(data, n_samples=1000, stat_fn=None):
        import random
        if stat_fn is None:
            stat_fn = lambda d: sum(d) / len(d) if d else 0
        stats = []
        for _ in range(n_samples):
            sample = [random.choice(data) for _ in range(len(data))]
            stats.append(stat_fn(sample))
        return {
            "mean": round(sum(stats) / len(stats), 6),
            "std": round(math.sqrt(sum((s - sum(stats) / len(stats)) ** 2 for s in stats) / len(stats)), 6),
            "ci_lower": round(sorted(stats)[int(0.025 * len(stats))], 6),
            "ci_upper": round(sorted(stats)[int(0.975 * len(stats))], 6),
        }

    # ═══════════════════════════════════════════════════════
    #  Distância & Similaridade
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _euclidean_distance(a, b):
        return round(math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(min(len(a), len(b))))), 6)

    @staticmethod
    def _manhattan_distance(a, b):
        return sum(abs(a[i] - b[i]) for i in range(min(len(a), len(b))))

    @staticmethod
    def _cosine_similarity(a, b):
        n = min(len(a), len(b))
        dot = sum(a[i] * b[i] for i in range(n))
        na = math.sqrt(sum(x ** 2 for x in a[:n]))
        nb = math.sqrt(sum(x ** 2 for x in b[:n]))
        if na == 0 or nb == 0:
            return 0
        return round(dot / (na * nb), 6)


# ═══════════════════════════════════════════════════════════
#  AnalyticsFrame (Enhanced DataFrame)
# ═══════════════════════════════════════════════════════════

class AnalyticsFrame:
    """Enhanced DataFrame for data analysis in DataForge."""

    def __init__(self, data=None, columns=None):
        self.data = [list(row) for row in (data or [])]
        if columns:
            self.columns = list(columns)
        elif self.data:
            self.columns = [f"col_{i}" for i in range(len(self.data[0]))]
        else:
            self.columns = []

    # ── Acesso ────────────────────────────────────────────

    def head(self, n=5):
        return AnalyticsFrame(self.data[:n], self.columns)

    def tail(self, n=5):
        return AnalyticsFrame(self.data[-n:], self.columns)

    def shape(self):
        return [len(self.data), len(self.columns)]

    def column(self, name):
        idx = self.columns.index(name)
        return [row[idx] for row in self.data]

    def row(self, i):
        return dict(zip(self.columns, self.data[i]))

    def select(self, *cols):
        idxs = [self.columns.index(c) for c in cols]
        new_data = [[row[i] for i in idxs] for row in self.data]
        return AnalyticsFrame(new_data, list(cols))

    def rename(self, mapping):
        new_cols = [mapping.get(c, c) for c in self.columns]
        return AnalyticsFrame(self.data, new_cols)

    # ── Filtro & Ordenação ────────────────────────────────

    def where(self, col, op, value):
        idx = self.columns.index(col)
        ops = {
            "==": lambda a, b: a == b, "!=": lambda a, b: a != b,
            ">": lambda a, b: float(a) > float(b), "<": lambda a, b: float(a) < float(b),
            ">=": lambda a, b: float(a) >= float(b), "<=": lambda a, b: float(a) <= float(b),
            "contains": lambda a, b: str(b) in str(a),
        }
        fn = ops.get(op, ops["=="])
        return AnalyticsFrame([r for r in self.data if fn(r[idx], value)], self.columns)

    def sort_by(self, col, descending=False):
        idx = self.columns.index(col)
        return AnalyticsFrame(sorted(self.data, key=lambda r: r[idx], reverse=descending), self.columns)

    def filter(self, fn):
        return AnalyticsFrame([r for r in self.data if fn(dict(zip(self.columns, r)))], self.columns)

    # ── Transformação ─────────────────────────────────────

    def add_column(self, name, values_or_fn):
        if callable(values_or_fn):
            vals = [values_or_fn(dict(zip(self.columns, r))) for r in self.data]
        else:
            vals = values_or_fn
        new_data = [list(row) + [vals[i] if i < len(vals) else None] for i, row in enumerate(self.data)]
        return AnalyticsFrame(new_data, self.columns + [name])

    def drop_column(self, name):
        idx = self.columns.index(name)
        new_cols = [c for i, c in enumerate(self.columns) if i != idx]
        new_data = [[c for i, c in enumerate(row) if i != idx] for row in self.data]
        return AnalyticsFrame(new_data, new_cols)

    def map_column(self, col, fn):
        idx = self.columns.index(col)
        new_data = [list(row) for row in self.data]
        for row in new_data:
            row[idx] = fn(row[idx])
        return AnalyticsFrame(new_data, self.columns)

    def apply(self, fn):
        return AnalyticsFrame([fn(dict(zip(self.columns, r))) for r in self.data], self.columns)

    # ── Agregação ─────────────────────────────────────────

    def group_by(self, col, agg_col, agg="sum"):
        idx = self.columns.index(col)
        val_idx = self.columns.index(agg_col)
        groups = defaultdict(list)
        for row in self.data:
            try:
                groups[row[idx]].append(float(row[val_idx]))
            except (ValueError, TypeError):
                pass
        agg_fn = {"sum": sum, "mean": lambda v: sum(v) / len(v), "count": len, "min": min, "max": max}.get(agg, sum)
        return {k: round(agg_fn(v), 4) for k, v in groups.items()}

    def describe(self):
        result = {}
        for i, col in enumerate(self.columns):
            vals = []
            for row in self.data:
                try:
                    vals.append(float(row[i]))
                except (ValueError, TypeError):
                    pass
            if vals:
                result[col] = ArcaneAnalytics._describe(vals)
        return result

    def value_counts(self, col):
        idx = self.columns.index(col)
        return dict(Counter(row[idx] for row in self.data).most_common())

    # ── Merge & Join ──────────────────────────────────────

    def merge(self, other, on):
        idx_l = self.columns.index(on)
        idx_r = other.columns.index(on)
        right_map = {}
        for row in other.data:
            right_map[row[idx_r]] = row
        new_cols = self.columns + [c for c in other.columns if c != on]
        result = []
        for row in self.data:
            key = row[idx_l]
            if key in right_map:
                rr = right_map[key]
                result.append(list(row) + [rr[i] for i, c in enumerate(other.columns) if c != on])
        return AnalyticsFrame(result, new_cols)

    def concat(self, other):
        return AnalyticsFrame(self.data + other.data, self.columns)

    # ── Export ────────────────────────────────────────────

    def to_csv(self, path):
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)
            writer.writerows(self.data)
        return path

    def to_json(self, path=None):
        records = [dict(zip(self.columns, row)) for row in self.data]
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            return path
        return records

    def to_list(self):
        return self.data

    def to_dict(self):
        return [dict(zip(self.columns, row)) for row in self.data]

    # ── Representação ─────────────────────────────────────

    def __repr__(self):
        header = " | ".join(f"{c:>12}" for c in self.columns)
        sep = "-" * len(header)
        rows = []
        for row in self.data[:10]:
            rows.append(" | ".join(f"{str(v):>12}" for v in row))
        if len(self.data) > 10:
            rows.append(f"... ({len(self.data)} linhas no total)")
        return f"{header}\n{sep}\n" + "\n".join(rows)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.column(key)
        if isinstance(key, int):
            return self.data[key]
        if isinstance(key, slice):
            return AnalyticsFrame(self.data[key], self.columns)
        raise TypeError(f"Chave inválida: {type(key)}")
