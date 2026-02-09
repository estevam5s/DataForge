"""
Arcane.Data - Data Science Module
DataFrames, data manipulation, and analysis tools.
"""

import math
import csv
import json


class ArcaneData:
    """Data science and analysis module."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Data",
            "Frame": DataFrame,
            "read_csv": cls._read_csv,
            "read_json": cls._read_json,
            "series": cls._series,
            "describe": cls._describe,
            "correlate": cls._correlate,
            "normalize": cls._normalize,
            "standardize": cls._standardize,
            "one_hot": cls._one_hot,
            "split": cls._train_test_split,
            "pivot": cls._pivot,
            "group_by": cls._group_by,
            "merge": cls._merge,
        }

    @staticmethod
    def _read_csv(path, header=True):
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        if header and rows:
            cols = rows[0]
            data = rows[1:]
            return DataFrame(data, cols)
        return DataFrame(rows)

    @staticmethod
    def _read_json(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list) and data and isinstance(data[0], dict):
            cols = list(data[0].keys())
            rows = [[row.get(c) for c in cols] for row in data]
            return DataFrame(rows, cols)
        return data

    @staticmethod
    def _series(data, name="series"):
        return {"__type__": "Series", "name": name, "data": list(data)}

    @staticmethod
    def _describe(data):
        """Statistical summary of numeric data."""
        nums = [x for x in data if isinstance(x, (int, float))]
        if not nums:
            return {"count": 0}
        n = len(nums)
        mean = sum(nums) / n
        sorted_nums = sorted(nums)
        median = sorted_nums[n // 2] if n % 2 else (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2
        variance = sum((x - mean) ** 2 for x in nums) / max(n - 1, 1)
        return {
            "count": n,
            "mean": mean,
            "median": median,
            "min": min(nums),
            "max": max(nums),
            "std": math.sqrt(variance),
            "variance": variance,
            "sum": sum(nums),
        }

    @staticmethod
    def _correlate(x, y):
        """Pearson correlation between two lists."""
        n = min(len(x), len(y))
        if n == 0:
            return 0
        mean_x = sum(x[:n]) / n
        mean_y = sum(y[:n]) / n
        cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n
        std_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x[:n]) / n)
        std_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y[:n]) / n)
        if std_x == 0 or std_y == 0:
            return 0
        return cov / (std_x * std_y)

    @staticmethod
    def _normalize(data, min_val=0, max_val=1):
        """Min-max normalization."""
        mn, mx = min(data), max(data)
        if mx == mn:
            return [min_val] * len(data)
        return [min_val + (x - mn) / (mx - mn) * (max_val - min_val) for x in data]

    @staticmethod
    def _standardize(data):
        """Z-score standardization."""
        mean = sum(data) / len(data)
        std = math.sqrt(sum((x - mean) ** 2 for x in data) / len(data))
        if std == 0:
            return [0] * len(data)
        return [(x - mean) / std for x in data]

    @staticmethod
    def _one_hot(labels):
        """One-hot encoding."""
        unique = sorted(set(labels))
        mapping = {v: i for i, v in enumerate(unique)}
        result = []
        for label in labels:
            vec = [0] * len(unique)
            vec[mapping[label]] = 1
            result.append(vec)
        return result

    @staticmethod
    def _train_test_split(data, ratio=0.8):
        """Split data into train/test."""
        import random
        shuffled = list(data)
        random.shuffle(shuffled)
        split_idx = int(len(shuffled) * ratio)
        return shuffled[:split_idx], shuffled[split_idx:]

    @staticmethod
    def _pivot(data, index_col, value_col, agg="sum"):
        """Simple pivot table."""
        groups = {}
        for row in data:
            key = row[index_col] if isinstance(row, dict) else row[index_col]
            val = row[value_col] if isinstance(row, dict) else row[value_col]
            if key not in groups:
                groups[key] = []
            groups[key].append(float(val) if isinstance(val, (int, float, str)) else 0)

        result = {}
        for key, vals in groups.items():
            if agg == "sum":
                result[key] = sum(vals)
            elif agg == "mean":
                result[key] = sum(vals) / len(vals)
            elif agg == "count":
                result[key] = len(vals)
            elif agg == "min":
                result[key] = min(vals)
            elif agg == "max":
                result[key] = max(vals)
        return result

    @staticmethod
    def _group_by(data, key_func):
        """Group data by a key function."""
        groups = {}
        for item in data:
            key = key_func(item)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        return groups

    @staticmethod
    def _merge(left, right, on):
        """Merge two datasets on a key."""
        result = []
        right_map = {}
        for row in right:
            key = row.get(on) if isinstance(row, dict) else row[on]
            right_map[key] = row

        for row in left:
            key = row.get(on) if isinstance(row, dict) else row[on]
            if key in right_map:
                merged = {**row, **right_map[key]} if isinstance(row, dict) else row + right_map[key]
                result.append(merged)
        return result


class DataFrame:
    """Simple DataFrame implementation for DataForge."""

    def __init__(self, data=None, columns=None):
        self.data = data or []
        self.columns = columns or [f"col_{i}" for i in range(len(self.data[0]) if self.data else 0)]
        self._type = "Frame"

    def head(self, n=5):
        return DataFrame(self.data[:n], self.columns)

    def tail(self, n=5):
        return DataFrame(self.data[-n:], self.columns)

    def shape(self):
        return (len(self.data), len(self.columns))

    def column(self, name):
        if name in self.columns:
            idx = self.columns.index(name)
            return [row[idx] for row in self.data]
        raise KeyError(f"Column '{name}' not found")

    def filter(self, func):
        return DataFrame([row for row in self.data if func(row)], self.columns)

    def map(self, func):
        return DataFrame([func(row) for row in self.data], self.columns)

    def sort(self, col, reverse=False):
        idx = self.columns.index(col) if isinstance(col, str) else col
        return DataFrame(sorted(self.data, key=lambda r: r[idx], reverse=reverse), self.columns)

    def add_column(self, name, values):
        new_data = [row + [v] for row, v in zip(self.data, values)]
        return DataFrame(new_data, self.columns + [name])

    def to_list(self):
        return self.data

    def to_dict(self):
        return [dict(zip(self.columns, row)) for row in self.data]

    def describe(self):
        result = {}
        for i, col in enumerate(self.columns):
            vals = []
            for row in self.data:
                try:
                    vals.append(float(row[i]))
                except (ValueError, TypeError):
                    continue
            if vals:
                result[col] = ArcaneData._describe(vals)
        return result

    def __repr__(self):
        header = " | ".join(str(c) for c in self.columns)
        sep = "-" * len(header)
        rows = []
        for row in self.data[:10]:
            rows.append(" | ".join(str(v) for v in row))
        if len(self.data) > 10:
            rows.append(f"... ({len(self.data)} rows total)")
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
            return DataFrame(self.data[key], self.columns)
        raise TypeError(f"Invalid key type: {type(key)}")
