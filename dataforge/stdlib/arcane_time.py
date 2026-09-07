"""
Arcane.Time — datas, horas, durações e cronometragem.

Sem dependências externas: usa apenas datetime, time e zoneinfo da stdlib.
Datas são representadas como vaults com __type__, para atravessarem o runtime
do DataForge como qualquer outro valor.
"""

import calendar
import time as _time
from datetime import date as _date, datetime as _datetime, timedelta, timezone


def _wrap_datetime(d: _datetime):
    return {
        "__type__": "DateTime",
        "year": d.year, "month": d.month, "day": d.day,
        "hour": d.hour, "minute": d.minute, "second": d.second,
        "microsecond": d.microsecond,
        "weekday": d.weekday(),
        "iso": d.isoformat(),
        "timestamp": d.timestamp() if d.tzinfo or True else 0,
    }


def _unwrap(valor) -> _datetime:
    if isinstance(valor, dict) and valor.get("__type__") in ("DateTime", "Date"):
        return _datetime(valor["year"], valor["month"], valor["day"],
                         valor.get("hour", 0), valor.get("minute", 0),
                         valor.get("second", 0), valor.get("microsecond", 0))
    if isinstance(valor, (int, float)):
        return _datetime.fromtimestamp(valor)
    if isinstance(valor, str):
        return _datetime.fromisoformat(valor)
    raise ValueError(f"Não é uma data: {valor!r}")


def _wrap_duration(delta: timedelta):
    total = delta.total_seconds()
    return {
        "__type__": "Duration",
        "days": delta.days,
        "seconds": delta.seconds,
        "total_seconds": total,
        "total_minutes": total / 60,
        "total_hours": total / 3600,
        "total_days": total / 86400,
        "human": _humanize(total),
    }


def _humanize(segundos: float) -> str:
    segundos = int(abs(segundos))
    if segundos < 60:
        return f"{segundos}s"
    if segundos < 3600:
        return f"{segundos // 60}min {segundos % 60}s"
    if segundos < 86400:
        return f"{segundos // 3600}h {(segundos % 3600) // 60}min"
    return f"{segundos // 86400}d {(segundos % 86400) // 3600}h"


class _Stopwatch:
    def __init__(self):
        self._inicio = None
        self._acumulado = 0.0
        self._rodando = False

    def start(self):
        if not self._rodando:
            self._inicio = _time.perf_counter()
            self._rodando = True
        return self

    def stop(self):
        if self._rodando:
            self._acumulado += _time.perf_counter() - self._inicio
            self._rodando = False
        return self._acumulado

    def reset(self):
        self._inicio = None
        self._acumulado = 0.0
        self._rodando = False
        return self

    def elapsed(self):
        if self._rodando:
            return self._acumulado + (_time.perf_counter() - self._inicio)
        return self._acumulado

    def elapsed_ms(self):
        return self.elapsed() * 1000


class ArcaneTime:
    """Módulo de data e hora."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Time",

            # ── Agora ──
            "now": cls._now,
            "today": cls._today,
            "utcnow": cls._utcnow,
            "timestamp": lambda: _time.time(),
            "monotonic": lambda: _time.monotonic(),

            # ── Construção ──
            "date": cls._date,
            "datetime": cls._datetime,
            "from_timestamp": lambda ts: _wrap_datetime(_datetime.fromtimestamp(ts)),
            "from_iso": lambda t: _wrap_datetime(_datetime.fromisoformat(t)),
            "parse": cls._parse,

            # ── Formatação ──
            "format": cls._format,
            "to_iso": lambda d: _unwrap(d).isoformat(),
            "to_date_string": lambda d: _unwrap(d).strftime("%d/%m/%Y"),
            "to_time_string": lambda d: _unwrap(d).strftime("%H:%M:%S"),
            "to_br": lambda d: _unwrap(d).strftime("%d/%m/%Y %H:%M:%S"),

            # ── Componentes ──
            "year": lambda d: _unwrap(d).year,
            "month": lambda d: _unwrap(d).month,
            "day": lambda d: _unwrap(d).day,
            "hour": lambda d: _unwrap(d).hour,
            "minute": lambda d: _unwrap(d).minute,
            "second": lambda d: _unwrap(d).second,
            "weekday": lambda d: _unwrap(d).weekday(),
            "weekday_name": cls._weekday_name,
            "month_name": cls._month_name,
            "day_of_year": lambda d: _unwrap(d).timetuple().tm_yday,
            "week_of_year": lambda d: int(_unwrap(d).strftime("%V")),
            "quarter": lambda d: (_unwrap(d).month - 1) // 3 + 1,

            # ── Aritmética ──
            "add_days": lambda d, n: _wrap_datetime(_unwrap(d) + timedelta(days=n)),
            "add_hours": lambda d, n: _wrap_datetime(_unwrap(d) + timedelta(hours=n)),
            "add_minutes": lambda d, n: _wrap_datetime(_unwrap(d) + timedelta(minutes=n)),
            "add_seconds": lambda d, n: _wrap_datetime(_unwrap(d) + timedelta(seconds=n)),
            "add_weeks": lambda d, n: _wrap_datetime(_unwrap(d) + timedelta(weeks=n)),
            "add_months": cls._add_months,
            "add_years": lambda d, n: cls._add_months(d, n * 12),
            "diff": cls._diff,
            "days_between": lambda a, b: abs((_unwrap(b) - _unwrap(a)).days),

            # ── Comparação ──
            "is_before": lambda a, b: _unwrap(a) < _unwrap(b),
            "is_after": lambda a, b: _unwrap(a) > _unwrap(b),
            "is_same_day": cls._is_same_day,
            "is_weekend": lambda d: _unwrap(d).weekday() >= 5,
            "is_leap_year": lambda a: calendar.isleap(
                a if isinstance(a, int) else _unwrap(a).year),

            # ── Limites ──
            "start_of_day": cls._start_of_day,
            "end_of_day": cls._end_of_day,
            "start_of_month": cls._start_of_month,
            "end_of_month": cls._end_of_month,
            "days_in_month": lambda a, m: calendar.monthrange(a, m)[1],

            # ── Duração ──
            "duration": cls._duration,
            "humanize": lambda s: _humanize(s),
            "age": cls._age,

            # ── Cronômetro ──
            "stopwatch": lambda: _Stopwatch(),
            "measure": cls._measure,
            "sleep": lambda s: (_time.sleep(s), None)[1],

            # ── Fuso ──
            "timezone_offset": cls._tz_offset,
            "to_utc": lambda d: _wrap_datetime(
                _unwrap(d).astimezone(timezone.utc).replace(tzinfo=None)),
        }

    @staticmethod
    def _now():
        return _wrap_datetime(_datetime.now())

    @staticmethod
    def _utcnow():
        return _wrap_datetime(_datetime.now(timezone.utc).replace(tzinfo=None))

    @staticmethod
    def _today():
        agora = _datetime.now()
        return _wrap_datetime(_datetime(agora.year, agora.month, agora.day))

    @staticmethod
    def _date(ano, mes, dia):
        return _wrap_datetime(_datetime(ano, mes, dia))

    @staticmethod
    def _datetime(ano, mes, dia, hora=0, minuto=0, segundo=0):
        return _wrap_datetime(_datetime(ano, mes, dia, hora, minuto, segundo))

    @staticmethod
    def _parse(texto, formato=None):
        if formato:
            return _wrap_datetime(_datetime.strptime(texto, formato))
        for tentativa in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                          "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
            try:
                return _wrap_datetime(_datetime.strptime(texto, tentativa))
            except ValueError:
                continue
        raise ValueError(f"Não consegui interpretar a data: {texto!r}")

    @staticmethod
    def _format(d, formato="%Y-%m-%d %H:%M:%S"):
        return _unwrap(d).strftime(formato)

    @staticmethod
    def _weekday_name(d, curto=False):
        nomes = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
                 "sexta-feira", "sábado", "domingo"]
        curtos = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
        indice = _unwrap(d).weekday()
        return curtos[indice] if curto else nomes[indice]

    @staticmethod
    def _month_name(d, curto=False):
        nomes = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                 "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        mes = d if isinstance(d, int) else _unwrap(d).month
        nome = nomes[mes - 1]
        return nome[:3] if curto else nome

    @staticmethod
    def _add_months(d, n):
        base = _unwrap(d)
        total = base.month - 1 + n
        ano = base.year + total // 12
        mes = total % 12 + 1
        dia = min(base.day, calendar.monthrange(ano, mes)[1])
        return _wrap_datetime(base.replace(year=ano, month=mes, day=dia))

    @staticmethod
    def _diff(a, b):
        return _wrap_duration(_unwrap(b) - _unwrap(a))

    @staticmethod
    def _is_same_day(a, b):
        x, y = _unwrap(a), _unwrap(b)
        return (x.year, x.month, x.day) == (y.year, y.month, y.day)

    @staticmethod
    def _start_of_day(d):
        base = _unwrap(d)
        return _wrap_datetime(base.replace(hour=0, minute=0, second=0, microsecond=0))

    @staticmethod
    def _end_of_day(d):
        base = _unwrap(d)
        return _wrap_datetime(base.replace(hour=23, minute=59, second=59, microsecond=999999))

    @staticmethod
    def _start_of_month(d):
        base = _unwrap(d)
        return _wrap_datetime(base.replace(day=1, hour=0, minute=0, second=0, microsecond=0))

    @staticmethod
    def _end_of_month(d):
        base = _unwrap(d)
        ultimo = calendar.monthrange(base.year, base.month)[1]
        return _wrap_datetime(base.replace(day=ultimo, hour=23, minute=59, second=59))

    @staticmethod
    def _duration(dias=0, horas=0, minutos=0, segundos=0):
        return _wrap_duration(timedelta(days=dias, hours=horas,
                                        minutes=minutos, seconds=segundos))

    @staticmethod
    def _age(nascimento, referencia=None):
        nasc = _unwrap(nascimento)
        hoje = _unwrap(referencia) if referencia else _datetime.now()
        anos = hoje.year - nasc.year
        if (hoje.month, hoje.day) < (nasc.month, nasc.day):
            anos -= 1
        return anos

    @staticmethod
    def _measure(acao):
        inicio = _time.perf_counter()
        resultado = acao()
        return {"__type__": "Measurement",
                "result": resultado,
                "seconds": _time.perf_counter() - inicio,
                "ms": (_time.perf_counter() - inicio) * 1000}

    @staticmethod
    def _tz_offset():
        return -_time.timezone / 3600
