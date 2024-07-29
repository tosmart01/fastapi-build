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
        model_cls = self._type_adapter.core_schema.get('cls')
        errors = exc.errors()
        if model_cls:
            errors += [{"model": model_cls, "custom_type": "model"}]
        else:
            field = self.alias
            msg = exc.errors()[0]["msg"]
            errors.append({"custom_type": "not_model", "custom_msg": f"{field} {msg}"})
        return None, _regenerate_error_with_loc(
            errors=errors, loc_prefix=loc
        )

ModelField.validate = validate

