import datetime
import json
import types
from uuid import UUID

import lazy_object_proxy
from future.utils import iteritems

from simpleflow.futures import Future


def serialize_complex_object(obj):
    if isinstance(
        obj, bytes
    ):  # Python 3 only (serialize_complex_object not called here in Python 2)
        return obj.decode("utf-8", errors="replace")
    if isinstance(obj, datetime.datetime):
        r = obj.isoformat()
        if obj.microsecond:
            r = r[:23] + r[26:]  # milliseconds only
        if r.endswith("+00:00"):
            r = r[:-6] + "Z"
        return r
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, datetime.time):
        r = obj.isoformat()
        if obj.microsecond:
            r = r[:12]
        return r
    elif isinstance(obj, types.GeneratorType):
        return [i for i in obj]
    elif isinstance(obj, Future):
        return obj.result
    elif isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, lazy_object_proxy.Proxy):
        return str(obj)
    elif isinstance(obj, (set, frozenset)):
        return list(obj)
    raise TypeError(
        "Type %s couldn't be serialized. This might be a bug in simpleflow,"
        " if so please file a new issue on GitHub!" % type(obj)
    )


def _resolve_proxy(obj):
    if isinstance(obj, dict):
        return {k: _resolve_proxy(v) for k, v in iteritems(obj)}
    if isinstance(obj, (list, tuple)):
        return [_resolve_proxy(v) for v in obj]
    if isinstance(obj, lazy_object_proxy.Proxy):
        return str(obj)
    return obj


def json_dumps(obj, pretty=False, compact=True, sort_keys=True, **kwargs):
    """
    JSON dump to string.
    """
    if "default" not in kwargs:
        kwargs["default"] = serialize_complex_object
    if pretty:
        kwargs["indent"] = 4
        kwargs["separators"] = (",", ": ")
    elif compact:
        kwargs["separators"] = (",", ":")

    try:
        return json.dumps(obj, sort_keys=sort_keys, **kwargs)
    except TypeError:
        # lazy_object_proxy.Proxy subclasses basestring: serialize_complex_object isn't called on python2
        # and some versions of pypy
        obj = _resolve_proxy(obj)
        return json.dumps(obj, sort_keys=sort_keys, **kwargs)


def json_loads_or_raw(data):
    """
    Try to get a JSON object from a string.
    If this isn't JSON, return the raw string.
    """
    if not data:
        return None
    try:
        return json.loads(data)
    except Exception:
        return data
