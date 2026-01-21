"""Operator package shim + daily focus assistant entry.

This package is intentionally named ``operator`` to provide the CLI entry
``python -m operator.main``. To avoid breaking imports that expect the
standard library ``operator`` module, we implement a lightweight shim that:

- re-exports functions from the builtin ``_operator`` C module (e.g., ``eq``,
  ``lt``, ``add``, etc.), and
- provides pure-Python implementations of ``attrgetter``, ``itemgetter``, and
  ``methodcaller``.

By only importing ``_operator`` (not other stdlib modules), we avoid circular
imports during package initialization.
"""

from __future__ import annotations

# Import only the builtin C extension to avoid circular imports.
import _operator as _op  # type: ignore


# Re-export everything public from _operator
__all__ = [name for name in dir(_op) if not name.startswith("_")]
globals().update({name: getattr(_op, name) for name in __all__})


def length_hint(obj, default=0):  # type: ignore[misc]
    """Best-effort length_hint compatible with stdlib operator.length_hint.

    - If ``len(obj)`` works, return it.
    - Else if ``obj.__length_hint__`` exists and returns a non-negative int, return it.
    - Else return ``default``.
    """
    try:
        return len(obj)  # type: ignore[arg-type]
    except Exception:
        pass
    hint = getattr(obj, "__length_hint__", None)
    if callable(hint):
        try:
            value = int(hint())  # type: ignore[misc]
            if value >= 0:
                return value
        except Exception:
            pass
    return default


def itemgetter(*items):  # type: ignore[misc]
    """Return a callable that fetches item(s) from its operand.

    Mirrors behavior of stdlib operator.itemgetter for common cases.
    """

    if len(items) == 1:
        item = items[0]

        def g(obj):
            return obj[item]

        return g

    def g(obj):
        return tuple(obj[i] for i in items)

    return g


def attrgetter(*attrs):  # type: ignore[misc]
    """Return a callable that fetches attribute(s) from its operand.

    Supports dotted paths (e.g., "a.b.c").
    """

    def get_attr(obj, path: str):
        for name in path.split("."):
            obj = getattr(obj, name)
        return obj

    if len(attrs) == 1:
        attr = attrs[0]

        def g(obj):
            return get_attr(obj, attr)

        return g

    def g(obj):
        return tuple(get_attr(obj, a) for a in attrs)

    return g


def methodcaller(name, /, *args, **kwargs):  # type: ignore[misc]
    """Return a callable that calls the named method on its operand."""

    def call(obj):
        return getattr(obj, name)(*args, **kwargs)

    return call


# Ensure these helper names are exported as well
__all__.extend(["itemgetter", "attrgetter", "methodcaller", "length_hint"])  # type: ignore[arg-type]
