"""
Arcane.Test - Testing Framework Module
Mini test framework for DataForge with assertions, test suites, and reporting.
"""

import time
import math
import traceback


class ArcaneTest:
    """Testing framework for DataForge programs."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Test",

            # Test suite management
            "suite": cls._create_suite,
            "run": cls._run_suite,
            "add_test": cls._add_test,
            "run_suite": cls._run_suite_standalone,

            # Assertions
            "assert_eq": cls._assert_eq,
            "assert_neq": cls._assert_neq,
            "assert_true": cls._assert_true,
            "assert_false": cls._assert_false,
            "assert_void": cls._assert_void,
            "assert_not_void": cls._assert_not_void,
            "assert_type": cls._assert_type,
            "assert_greater": cls._assert_greater,
            "assert_less": cls._assert_less,
            "assert_between": cls._assert_between,
            "assert_contains": cls._assert_contains,
            "assert_not_contains": cls._assert_not_contains,
            "assert_length": cls._assert_length,
            "assert_empty": cls._assert_empty,
            "assert_not_empty": cls._assert_not_empty,
            "assert_close": cls._assert_close,
            "assert_match": cls._assert_match,
            "assert_throws": cls._assert_throws,
            "assert_keys": cls._assert_keys,
            "assert_all": cls._assert_all,
            "assert_any": cls._assert_any,
            "assert_sorted": cls._assert_sorted,
            "assert_unique": cls._assert_unique,
            "assert_instance": cls._assert_instance,
            "assert_deep_eq": cls._assert_deep_eq,

            # Utilities
            "benchmark": cls._benchmark,
            "mock": cls._mock,
            "spy": cls._spy,
            "describe": cls._describe,
            "it": cls._it,
        }

    @staticmethod
    def _create_suite(name="Test Suite"):
        """Create a new test suite."""
        return {
            "__type__": "TestSuite",
            "name": name,
            "tests": [],
            "passed": 0,
            "failed": 0,
            "errors": [],
            "start_time": 0,
            "end_time": 0,
        }

    @staticmethod
    def _add_test(suite, name, spec):
        """Add a test to a suite. spec can be a dict with 'expected'/'actual' or a callable."""
        suite["tests"].append({"name": name, "spec": spec})

    @staticmethod
    def _run_suite_standalone(suite):
        """Run a test suite that has had tests added via add_test."""
        suite["start_time"] = time.time()
        suite["passed"] = 0
        suite["failed"] = 0
        suite["errors"] = []

        print(f"\n{'='*60}")
        print(f"  🧪 {suite['name']}")
        print(f"{'='*60}")

        for test_info in suite.get("tests", []):
            name = test_info.get("name", "unnamed")
            spec = test_info.get("spec")

            try:
                if callable(spec):
                    spec()
                elif isinstance(spec, dict) and "expected" in spec and "actual" in spec:
                    expected = spec["expected"]
                    actual = spec["actual"]
                    if expected != actual:
                        raise AssertionError(f"Expected {expected!r}, got {actual!r}")
                suite["passed"] += 1
                print(f"  \033[1;32m✓\033[0m {name}")
            except AssertionError as e:
                suite["failed"] += 1
                suite["errors"].append({"test": name, "error": str(e)})
                print(f"  \033[1;31m✗\033[0m {name}")
                print(f"    → {e}")
            except Exception as e:
                suite["failed"] += 1
                suite["errors"].append({"test": name, "error": str(e)})
                print(f"  \033[1;31m✗\033[0m {name} (error)")
                print(f"    → {e}")

        suite["end_time"] = time.time()
        elapsed = (suite["end_time"] - suite["start_time"]) * 1000

        total = suite["passed"] + suite["failed"]
        print(f"\n{'—'*60}")
        if suite["failed"] == 0:
            print(f"  \033[1;32m✓ All {total} tests passed\033[0m ({elapsed:.1f}ms)")
        else:
            print(f"  \033[1;31m✗ {suite['failed']}/{total} tests failed\033[0m ({elapsed:.1f}ms)")
        print(f"{'='*60}\n")

        return suite

    @staticmethod
    def _run_suite(suite, tests):
        """Run a test suite with a list of test functions."""
        suite["start_time"] = time.time()
        suite["passed"] = 0
        suite["failed"] = 0
        suite["errors"] = []

        print(f"\n{'='*60}")
        print(f"  🧪 {suite['name']}")
        print(f"{'='*60}")

        for test_info in tests:
            if isinstance(test_info, dict):
                name = test_info.get("name", "unnamed")
                func = test_info.get("test")
            elif isinstance(test_info, (list, tuple)) and len(test_info) >= 2:
                name = test_info[0]
                func = test_info[1]
            else:
                continue

            try:
                if callable(func):
                    func()
                suite["passed"] += 1
                print(f"  \033[1;32m✓\033[0m {name}")
            except AssertionError as e:
                suite["failed"] += 1
                suite["errors"].append({"test": name, "error": str(e)})
                print(f"  \033[1;31m✗\033[0m {name}")
                print(f"    → {e}")
            except Exception as e:
                suite["failed"] += 1
                suite["errors"].append({"test": name, "error": str(e)})
                print(f"  \033[1;31m✗\033[0m {name} (error)")
                print(f"    → {e}")

        suite["end_time"] = time.time()
        elapsed = (suite["end_time"] - suite["start_time"]) * 1000

        total = suite["passed"] + suite["failed"]
        print(f"\n{'—'*60}")
        if suite["failed"] == 0:
            print(f"  \033[1;32m✓ All {total} tests passed\033[0m ({elapsed:.1f}ms)")
        else:
            print(f"  \033[1;31m✗ {suite['failed']}/{total} tests failed\033[0m ({elapsed:.1f}ms)")
        print(f"{'='*60}\n")

        return suite

    # ── Assertions ────────────────────────────────────────

    @staticmethod
    def _assert_eq(actual, expected, msg=None):
        if actual != expected:
            m = msg or f"Expected {expected!r}, got {actual!r}"
            raise AssertionError(m)

    @staticmethod
    def _assert_neq(actual, expected, msg=None):
        if actual == expected:
            m = msg or f"Expected values to differ, both are {actual!r}"
            raise AssertionError(m)

    @staticmethod
    def _assert_true(value, msg=None):
        if not value:
            raise AssertionError(msg or f"Expected truthy, got {value!r}")

    @staticmethod
    def _assert_false(value, msg=None):
        if value:
            raise AssertionError(msg or f"Expected falsy, got {value!r}")

    @staticmethod
    def _assert_void(value, msg=None):
        if value is not None:
            raise AssertionError(msg or f"Expected void, got {value!r}")

    @staticmethod
    def _assert_not_void(value, msg=None):
        if value is None:
            raise AssertionError(msg or "Expected non-void, got void")

    @staticmethod
    def _assert_type(value, expected_type, msg=None):
        type_map = {
            int: "Integer", float: "Float", str: "String",
            bool: "Boolean", list: "Cluster", dict: "Vault",
            type(None): "Void",
        }
        actual = type_map.get(type(value), type(value).__name__)
        if actual.lower() != expected_type.lower():
            raise AssertionError(msg or f"Expected type {expected_type}, got {actual}")

    @staticmethod
    def _assert_greater(a, b, msg=None):
        if not (a > b):
            raise AssertionError(msg or f"Expected {a!r} > {b!r}")

    @staticmethod
    def _assert_less(a, b, msg=None):
        if not (a < b):
            raise AssertionError(msg or f"Expected {a!r} < {b!r}")

    @staticmethod
    def _assert_between(value, low, high, msg=None):
        if not (low <= value <= high):
            raise AssertionError(msg or f"Expected {value!r} between {low!r} and {high!r}")

    @staticmethod
    def _assert_contains(collection, item, msg=None):
        if item not in collection:
            raise AssertionError(msg or f"Expected collection to contain {item!r}")

    @staticmethod
    def _assert_not_contains(collection, item, msg=None):
        if item in collection:
            raise AssertionError(msg or f"Expected collection to NOT contain {item!r}")

    @staticmethod
    def _assert_length(collection, expected, msg=None):
        actual = len(collection)
        if actual != expected:
            raise AssertionError(msg or f"Expected length {expected}, got {actual}")

    @staticmethod
    def _assert_empty(collection, msg=None):
        if len(collection) != 0:
            raise AssertionError(msg or f"Expected empty, got length {len(collection)}")

    @staticmethod
    def _assert_not_empty(collection, msg=None):
        if len(collection) == 0:
            raise AssertionError(msg or "Expected non-empty collection")

    @staticmethod
    def _assert_close(actual, expected, tolerance=0.001, msg=None):
        if abs(actual - expected) > tolerance:
            raise AssertionError(msg or f"Expected {expected} ± {tolerance}, got {actual}")

    @staticmethod
    def _assert_match(string, pattern, msg=None):
        import re
        if not re.search(pattern, string):
            raise AssertionError(msg or f"String '{string}' does not match pattern '{pattern}'")

    @staticmethod
    def _assert_throws(func, msg=None):
        try:
            func()
            raise AssertionError(msg or "Expected function to throw an error")
        except AssertionError:
            raise
        except Exception:
            pass  # Expected

    @staticmethod
    def _assert_keys(d, *expected_keys, msg=None):
        for key in expected_keys:
            if key not in d:
                raise AssertionError(msg or f"Missing key '{key}' in dict")

    @staticmethod
    def _assert_all(collection, predicate, msg=None):
        for item in collection:
            if not predicate(item):
                raise AssertionError(msg or f"Not all items satisfy predicate. Failed on: {item!r}")

    @staticmethod
    def _assert_any(collection, predicate, msg=None):
        if not any(predicate(item) for item in collection):
            raise AssertionError(msg or "No items satisfy predicate")

    @staticmethod
    def _assert_sorted(collection, reverse=False, msg=None):
        expected = sorted(collection, reverse=reverse)
        if list(collection) != expected:
            raise AssertionError(msg or f"Collection is not sorted")

    @staticmethod
    def _assert_unique(collection, msg=None):
        seen = set()
        for item in collection:
            key = str(item)
            if key in seen:
                raise AssertionError(msg or f"Duplicate found: {item!r}")
            seen.add(key)

    @staticmethod
    def _assert_instance(obj, blueprint_name, msg=None):
        if hasattr(obj, 'blueprint'):
            if obj.blueprint.name != blueprint_name:
                raise AssertionError(msg or f"Expected instance of {blueprint_name}, got {obj.blueprint.name}")
        else:
            raise AssertionError(msg or f"Not an instance: {type(obj).__name__}")

    @staticmethod
    def _assert_deep_eq(a, b, msg=None):
        if isinstance(a, dict) and isinstance(b, dict):
            if set(a.keys()) != set(b.keys()):
                raise AssertionError(msg or f"Dict keys differ: {set(a.keys())} vs {set(b.keys())}")
            for key in a:
                ArcaneTest._assert_deep_eq(a[key], b[key], msg)
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                raise AssertionError(msg or f"List lengths differ: {len(a)} vs {len(b)}")
            for x, y in zip(a, b):
                ArcaneTest._assert_deep_eq(x, y, msg)
        elif a != b:
            raise AssertionError(msg or f"Values differ: {a!r} vs {b!r}")

    # ── Utilities ────────────────────────────────────────

    @staticmethod
    def _benchmark(func, iterations=1000):
        """Benchmark a function."""
        start = time.time()
        for _ in range(iterations):
            func()
        elapsed = (time.time() - start) * 1000
        return {
            "iterations": iterations,
            "total_ms": round(elapsed, 2),
            "avg_ms": round(elapsed / iterations, 4),
            "ops_per_sec": round(iterations / (elapsed / 1000), 0) if elapsed > 0 else 0,
        }

    @staticmethod
    def _mock(return_value=None):
        """Create a mock function."""
        calls = []
        def mock_fn(*args, **kwargs):
            calls.append({"args": list(args), "kwargs": kwargs})
            return return_value
        mock_fn.calls = calls
        mock_fn.call_count = lambda: len(calls)
        mock_fn.called_with = lambda: calls[-1] if calls else None
        mock_fn.reset = lambda: calls.clear()
        return mock_fn

    @staticmethod
    def _spy(func):
        """Wrap a function to track calls while preserving behavior."""
        calls = []
        def spy_fn(*args, **kwargs):
            result = func(*args, **kwargs)
            calls.append({"args": list(args), "kwargs": kwargs, "result": result})
            return result
        spy_fn.calls = calls
        spy_fn.call_count = lambda: len(calls)
        return spy_fn

    @staticmethod
    def _describe(name, tests):
        """BDD-style describe block. Accepts name + list of [desc, func] pairs or a callable."""
        print(f"\n  📋 {name}")
        if callable(tests):
            tests()
        elif isinstance(tests, list):
            passed = 0
            failed = 0
            for test_info in tests:
                if isinstance(test_info, (list, tuple)) and len(test_info) >= 2:
                    desc, func = test_info[0], test_info[1]
                    try:
                        if callable(func):
                            func()
                        passed += 1
                        print(f"    \033[1;32m✓\033[0m {desc}")
                    except Exception as e:
                        failed += 1
                        print(f"    \033[1;31m✗\033[0m {desc}")
                        print(f"      → {e}")
            total = passed + failed
            if failed == 0:
                print(f"  \033[1;32m✓ {total}/{total} passed\033[0m")
            else:
                print(f"  \033[1;31m✗ {failed}/{total} failed\033[0m")

    @staticmethod
    def _it(description, test_func):
        """BDD-style it block."""
        try:
            test_func()
            print(f"    \033[1;32m✓\033[0m {description}")
            return True
        except Exception as e:
            print(f"    \033[1;31m✗\033[0m {description}")
            print(f"      → {e}")
            return False


class AssertionError(Exception):
    """Custom assertion error for DataForge tests."""
    pass
