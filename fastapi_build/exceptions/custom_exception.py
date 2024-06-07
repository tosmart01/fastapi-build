# -- coding: utf-8 --
# @Time : 2021/9/30 2:44 下午
# @Author : PinBar
# @File : exceptions.py

from .base import ApiError
from .error_code import (
    ParamCheckError,
    DataNotFound,
    DataExistsError,
    PermissionDeny,
    TokenNotExists,
    ExpireToken,
    CheckerError,
)
from .http_status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_200_OK,
)


class PermissionDenyError(ApiError):
    default_code = PermissionDeny
    default_message = "权限错误"
    default_http_code = HTTP_403_FORBIDDEN


class AuthDenyError(ApiError):
    default_code = TokenNotExists
    default_message = "用户未登录"
    default_http_code = HTTP_401_UNAUTHORIZED


class ParamsError(ApiError):
    default_code = ParamCheckError
    default_message = "参数错误"
    default_http_code = HTTP_400_BAD_REQUEST


class NotFoundError(ApiError):
    default_code = DataNotFound
    default_message = "请求资源不存在"
    default_http_code = HTTP_404_NOT_FOUND


class MultipleReturnedError(ApiError):
    default_code = DataNotFound
    default_message = "查询资源过多"
    default_http_code = HTTP_400_BAD_REQUEST

class PasswordError(ApiError):
    default_code = DataNotFound
    default_message = "密码错误"
    default_http_code = HTTP_400_BAD_REQUEST


class DataUniqueError(ApiError):
    default_code = DataExistsError
    default_message = "资源已存在"
    default_http_code = HTTP_400_BAD_REQUEST


class ValidatePhoneError(ApiError):
    default_code = ParamCheckError
    default_message = "请输出正确的手机号"
    default_http_code = HTTP_400_BAD_REQUEST


class ValidateEmailError(ApiError):
    default_code = ParamCheckError
    default_message = "请输出正确的邮箱"
    default_http_code = HTTP_400_BAD_REQUEST


class DriverLogoutError(ApiError):
    default_code = ExpireToken
    default_message = "其他设备登录，自动下线"
    default_http_code = HTTP_401_UNAUTHORIZED


class TextCheckError(ApiError):
    default_code = CheckerError
    default_message = "当前内容包含违规信息，请调整输入后重试"
    default_http_code = HTTP_200_OK


class FileValidError(ApiError):
    default_code = CheckerError
    default_message = "文件格式不合法"
    default_http_code = HTTP_400_BAD_REQUEST


if __name__ == "__main__":
    A = ParamsError()
    print(isinstance(A, ApiError))
    print(A)
