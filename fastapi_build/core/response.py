# -- coding: utf-8 --
# @Time : 2024/5/16 11:16
# @Author : PinBar
# @File : response.py
from typing import Any, Annotated

from pydantic import BaseModel, WrapValidator
from pydantic_core.core_schema import ValidatorFunctionWrapHandler, ValidationInfo


def maybe_strip_whitespace(
        v: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> int:
    return v


def Res(data_model, validate: bool = True):
    class ResponseModel(BaseModel):
        code: int = 0
        data: data_model
        message: str = "Success"

        class Config:
            orm_mode = True

    class ResponseSoftModel(BaseModel):
        code: int = 0
        data: Annotated[data_model, WrapValidator(maybe_strip_whitespace)] = None
        message: str = "Success"

        class Config:
            orm_mode = True

    if validate:
        return ResponseModel
    else:
        return ResponseSoftModel
