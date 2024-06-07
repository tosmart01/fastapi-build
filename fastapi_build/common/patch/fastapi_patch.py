# -- coding: utf-8 --
# @Time : 2024/5/30 18:51
# @Author : PinBar
# @File : fastapi_patch.py
from fastapi._compat import *
from fastapi._compat import _regenerate_error_with_loc


def validate(
        self,
        value: Any,
        values: Dict[str, Any] = {},  # noqa: B006
        *,
        loc: Tuple[Union[int, str], ...] = (),
) -> Tuple[Any, Union[List[Dict[str, Any]], None]]:
    try:
        return (
            self._type_adapter.validate_python(value, from_attributes=True),
            None,
        )
    except ValidationError as exc:
        errors = exc.errors(include_url=False) + [{"model": self._type_adapter.core_schema.get('cls') }]
        return None, _regenerate_error_with_loc(
            errors=errors, loc_prefix=loc
        )

ModelField.validate = validate

