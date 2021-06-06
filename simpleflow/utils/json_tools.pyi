from typing import Any, AnyStr, Text

def json_dumps(
    obj: Any,
    pretty: bool = False,
    compact: bool = True,
    sort_keys: bool = True,
    **kwargs
) -> Text: ...
def json_loads_or_raw(data: AnyStr) -> Any: ...
