"""
Arcane.Async - Async & Reactive Programming Module
Promises, observables, event emitters, task scheduling for DataForge.
"""

import time
import threading
import queue
import functools


class ArcaneAsync:
    """Async and reactive programming tools for DataForge."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Async",

            # Promise
            "promise": cls._promise,
            "resolve": cls._resolve,
            "reject": cls._reject,
            "then": cls._then,
            "catch": cls._catch,
            "all": cls._all,
            "race": cls._race,
            "any": cls._any_promise,
            "settled": cls._all_settled,

            # Observable / Stream
            "observable": cls._observable,
            "of": cls._of,
            "from_list": cls._from_list,
            "interval": cls._interval,
            "subject": cls._subject,
            "subscribe": cls._subscribe,
            "pipe_stream": cls._pipe_stream,

            # Stream operators
            "map_op": cls._map_op,
            "filter_op": cls._filter_op,
            "take_op": cls._take_op,
            "skip_op": cls._skip_op,
            "distinct_op": cls._distinct_op,
            "debounce_op": cls._debounce_op,
            "buffer_op": cls._buffer_op,
            "scan_op": cls._scan_op,
            "merge": cls._merge,
            "combine_latest": cls._combine_latest,

            # Event emitter
            "emitter": cls._emitter,
            "on": cls._on,
            "off": cls._off,
            "emit": cls._emit,
            "once_event": cls._once_event,

            # Task / Scheduler
            "task": cls._task,
            "delay": cls._delay,
            "timeout": cls._timeout,
            "retry_task": cls._retry_task,
            "parallel": cls._parallel,
            "sequential": cls._sequential,

            # Signal (reactive state)
            "signal": cls._signal,
            "computed": cls._computed,
            "effect": cls._effect,
            "batch": cls._batch,
        }

    # ── Promise ──────────────────────────────────────────

    @staticmethod
    def _promise(executor):
        """Create a promise."""
        p = {
            "__type__": "Promise",
            "state": "pending",
            "value": None,
            "error": None,
            "callbacks": [],
            "error_callbacks": [],
        }

        def resolve_fn(value):
            if p["state"] == "pending":
                p["state"] = "resolved"
                p["value"] = value
                for cb in p["callbacks"]:
                    cb(value)

        def reject_fn(error):
            if p["state"] == "pending":
                p["state"] = "rejected"
                p["error"] = error
                for cb in p["error_callbacks"]:
                    cb(error)

        try:
            executor(resolve_fn, reject_fn)
        except Exception as e:
            reject_fn(str(e))

        return p

    @staticmethod
    def _resolve(value):
        """Create a resolved promise."""
        return {
            "__type__": "Promise",
            "state": "resolved",
            "value": value,
            "error": None,
            "callbacks": [],
            "error_callbacks": [],
        }

    @staticmethod
    def _reject(error):
        """Create a rejected promise."""
        return {
            "__type__": "Promise",
            "state": "rejected",
            "value": None,
            "error": error,
            "callbacks": [],
            "error_callbacks": [],
        }

    @staticmethod
    def _then(promise, callback):
        """Chain a callback to a promise."""
        if promise["state"] == "resolved":
            try:
                result = callback(promise["value"])
                if isinstance(result, dict) and result.get("__type__") == "Promise":
                    return result
                return ArcaneAsync._resolve(result)
            except Exception as e:
                return ArcaneAsync._reject(str(e))
        elif promise["state"] == "pending":
            promise["callbacks"].append(callback)
        return promise

    @staticmethod
    def _catch(promise, callback):
        """Add error handler to promise."""
        if promise["state"] == "rejected":
            try:
                result = callback(promise["error"])
                return ArcaneAsync._resolve(result)
            except Exception as e:
                return ArcaneAsync._reject(str(e))
        elif promise["state"] == "pending":
            promise["error_callbacks"].append(callback)
        return promise

    @staticmethod
    def _all(promises):
        """Wait for all promises to resolve."""
        results = []
        for p in promises:
            if p["state"] == "rejected":
                return ArcaneAsync._reject(p["error"])
            results.append(p.get("value"))
        return ArcaneAsync._resolve(results)

    @staticmethod
    def _race(promises):
        """Return first settled promise."""
        for p in promises:
            if p["state"] != "pending":
                return p
        return ArcaneAsync._resolve(None)

    @staticmethod
    def _any_promise(promises):
        """Return first resolved promise."""
        errors = []
        for p in promises:
            if p["state"] == "resolved":
                return p
            if p["state"] == "rejected":
                errors.append(p["error"])
        if len(errors) == len(promises):
            return ArcaneAsync._reject(errors)
        return ArcaneAsync._resolve(None)

    @staticmethod
    def _all_settled(promises):
        """Get status of all promises."""
        results = []
        for p in promises:
            results.append({
                "state": p["state"],
                "value": p.get("value"),
                "error": p.get("error"),
            })
        return results

    # ── Observable / Stream ──────────────────────────────

    @staticmethod
    def _observable(producer=None):
        """Create an observable stream."""
        obs = {
            "__type__": "Observable",
            "subscribers": [],
            "values": [],
            "completed": False,
        }

        if producer:
            def next_fn(value):
                obs["values"].append(value)
                for sub in obs["subscribers"]:
                    sub(value)
            def complete_fn():
                obs["completed"] = True
            producer(next_fn, complete_fn)

        return obs

    @staticmethod
    def _of(*values):
        """Create observable from values."""
        return {
            "__type__": "Observable",
            "subscribers": [],
            "values": list(values),
            "completed": True,
        }

    @staticmethod
    def _from_list(lst):
        """Create observable from list."""
        return {
            "__type__": "Observable",
            "subscribers": [],
            "values": list(lst),
            "completed": True,
        }

    @staticmethod
    def _interval(ms, count=10):
        """Create observable that emits at intervals (simulated)."""
        values = list(range(count))
        return {
            "__type__": "Observable",
            "subscribers": [],
            "values": values,
            "completed": True,
            "interval_ms": ms,
        }

    @staticmethod
    def _subject():
        """Create a Subject (both observable and observer)."""
        s = {
            "__type__": "Subject",
            "subscribers": [],
            "values": [],
            "completed": False,
        }

        def next_val(value):
            s["values"].append(value)
            for sub in s["subscribers"]:
                sub(value)

        s["next"] = next_val
        return s

    @staticmethod
    def _subscribe(observable, callback):
        """Subscribe to an observable."""
        observable["subscribers"].append(callback)
        # Replay existing values
        for val in observable.get("values", []):
            callback(val)
        return {"unsubscribe": lambda: observable["subscribers"].remove(callback) if callback in observable["subscribers"] else None}

    @staticmethod
    def _pipe_stream(observable, *operators):
        """Apply operators to an observable stream."""
        values = list(observable.get("values", []))
        for op in operators:
            values = op(values)
        return {
            "__type__": "Observable",
            "subscribers": [],
            "values": values,
            "completed": True,
        }

    # ── Stream Operators ─────────────────────────────────

    @staticmethod
    def _map_op(fn):
        return lambda values: [fn(v) for v in values]

    @staticmethod
    def _filter_op(fn):
        return lambda values: [v for v in values if fn(v)]

    @staticmethod
    def _take_op(n):
        return lambda values: values[:n]

    @staticmethod
    def _skip_op(n):
        return lambda values: values[n:]

    @staticmethod
    def _distinct_op():
        def distinct(values):
            seen = set()
            result = []
            for v in values:
                key = str(v)
                if key not in seen:
                    seen.add(key)
                    result.append(v)
            return result
        return distinct

    @staticmethod
    def _debounce_op(ms):
        """Debounce (simulated - takes last value in window)."""
        return lambda values: values[-1:] if values else []

    @staticmethod
    def _buffer_op(size):
        def buffer(values):
            return [values[i:i+size] for i in range(0, len(values), size)]
        return buffer

    @staticmethod
    def _scan_op(fn, initial):
        def scan(values):
            result = []
            acc = initial
            for v in values:
                acc = fn(acc, v)
                result.append(acc)
            return result
        return scan

    @staticmethod
    def _merge(*observables):
        """Merge multiple observables."""
        all_values = []
        for obs in observables:
            all_values.extend(obs.get("values", []))
        return {
            "__type__": "Observable",
            "subscribers": [],
            "values": all_values,
            "completed": all(o.get("completed", False) for o in observables),
        }

    @staticmethod
    def _combine_latest(*observables):
        """Combine latest values from observables."""
        latest = []
        for obs in observables:
            vals = obs.get("values", [])
            latest.append(vals[-1] if vals else None)
        return {
            "__type__": "Observable",
            "subscribers": [],
            "values": [latest],
            "completed": True,
        }

    # ── Event Emitter ────────────────────────────────────

    @staticmethod
    def _emitter():
        """Create an event emitter."""
        return {
            "__type__": "EventEmitter",
            "listeners": {},
        }

    @staticmethod
    def _on(emitter, event, callback):
        """Register event listener."""
        if event not in emitter["listeners"]:
            emitter["listeners"][event] = []
        emitter["listeners"][event].append(callback)
        return emitter

    @staticmethod
    def _off(emitter, event, callback=None):
        """Remove event listener."""
        if event in emitter["listeners"]:
            if callback:
                emitter["listeners"][event] = [
                    cb for cb in emitter["listeners"][event] if cb != callback
                ]
            else:
                emitter["listeners"][event] = []
        return emitter

    @staticmethod
    def _emit(emitter, event, *data):
        """Emit an event."""
        for cb in emitter.get("listeners", {}).get(event, []):
            cb(*data)
        return emitter

    @staticmethod
    def _once_event(emitter, event, callback):
        """Register one-time event listener."""
        def wrapper(*args):
            callback(*args)
            ArcaneAsync._off(emitter, event, wrapper)
        return ArcaneAsync._on(emitter, event, wrapper)

    # ── Task / Scheduler ─────────────────────────────────

    @staticmethod
    def _task(fn):
        """Create an async task."""
        return {
            "__type__": "Task",
            "fn": fn,
            "state": "idle",
            "result": None,
            "error": None,
        }

    @staticmethod
    def _delay(ms, fn=None):
        """Create a delayed task (simulated)."""
        time.sleep(ms / 1000.0)
        if fn:
            return fn()
        return None

    @staticmethod
    def _timeout(ms, fn):
        """Run function with timeout."""
        result = [None]
        error = [None]

        def run():
            try:
                result[0] = fn()
            except Exception as e:
                error[0] = str(e)

        t = threading.Thread(target=run)
        t.start()
        t.join(timeout=ms / 1000.0)

        if t.is_alive():
            return ArcaneAsync._reject("Timeout exceeded")
        if error[0]:
            return ArcaneAsync._reject(error[0])
        return ArcaneAsync._resolve(result[0])

    @staticmethod
    def _retry_task(fn, max_retries=3, delay_ms=100):
        """Retry a task on failure."""
        last_error = None
        for i in range(max_retries):
            try:
                result = fn()
                return ArcaneAsync._resolve(result)
            except Exception as e:
                last_error = str(e)
                if i < max_retries - 1:
                    time.sleep(delay_ms / 1000.0)
        return ArcaneAsync._reject(f"Failed after {max_retries} retries: {last_error}")

    @staticmethod
    def _parallel(*fns):
        """Execute functions in parallel (simulated with threads)."""
        results = [None] * len(fns)
        errors = [None] * len(fns)
        threads = []

        for i, fn in enumerate(fns):
            def run(idx=i, func=fn):
                try:
                    results[idx] = func()
                except Exception as e:
                    errors[idx] = str(e)
            t = threading.Thread(target=run)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        for e in errors:
            if e:
                return ArcaneAsync._reject(e)
        return ArcaneAsync._resolve(results)

    @staticmethod
    def _sequential(*fns):
        """Execute functions sequentially."""
        results = []
        for fn in fns:
            try:
                results.append(fn())
            except Exception as e:
                return ArcaneAsync._reject(str(e))
        return ArcaneAsync._resolve(results)

    # ── Signal (Reactive State) ──────────────────────────

    @staticmethod
    def _signal(initial_value):
        """Create a reactive signal."""
        s = {
            "__type__": "Signal",
            "value": initial_value,
            "subscribers": [],
        }

        def get():
            return s["value"]

        def set_val(new_value):
            old = s["value"]
            s["value"] = new_value
            if old != new_value:
                for sub in s["subscribers"]:
                    sub(new_value, old)

        def subscribe(fn):
            s["subscribers"].append(fn)

        s["get"] = get
        s["set"] = set_val
        s["subscribe"] = subscribe
        return s

    @staticmethod
    def _computed(signals, fn):
        """Create a computed signal derived from other signals."""
        def get_values():
            return [s["get"]() if callable(s.get("get")) else s.get("value") for s in signals]

        c = {
            "__type__": "Computed",
            "value": fn(*get_values()),
            "subscribers": [],
        }

        def update(*_):
            c["value"] = fn(*get_values())
            for sub in c["subscribers"]:
                sub(c["value"])

        for sig in signals:
            if "subscribe" in sig:
                sig["subscribe"](lambda *_: update())

        c["get"] = lambda: c["value"]
        return c

    @staticmethod
    def _effect(signals, fn):
        """Create a side effect that runs when signals change."""
        def update(*_):
            values = [s["get"]() if callable(s.get("get")) else s.get("value") for s in signals]
            fn(*values)

        for sig in signals:
            if "subscribe" in sig:
                sig["subscribe"](lambda *_: update())

        # Run immediately
        update()

    @staticmethod
    def _batch(fn):
        """Batch multiple reactive updates."""
        fn()
