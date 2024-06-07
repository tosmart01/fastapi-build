from .http_status import *

# API内部错误，以1101开头
RequestSuccess = 0
CheckerError = 7001
UnknownError = 1001
ParamCheckError = 1101
ParamTypeError = 1102
DataBaseError = 1103
DataExistsError = 1104
AccessDenied = 1105
RequestTimeout = 1106
ExternalServerError = 1107
InsideServerError = 1108
ServiceUnavailable = 1109
MethodNotAllowed = 1110
DataNotFound = 1111
DataUpdateError = 1112
DataChangeError = 1113
DataDelError = 1114


# 用户错误，以1200开头
UserError = 1201
ExpireToken = 1202
TokenNotExists = 1203
PermissionDeny = 1204
UserNotExists = 1205
PasswordError = 1206
UserExistsError = 1207
UserNameNotExists = 1208
UserChangeError = 1209
UserDelError = 1210
SourcePasswordError = 1211
ChangePasswordError = 1212

# 角色错误，以1300开头
RoleNotExists = 1301
RoleNameExists = 1302
RoleChangeError = 1303
RoleDelError = 1304
RoleExistsError = 1305


MESSAGE = {
    RequestSuccess: {"message": "请求成功", "http_code": HTTP_200_OK},
    UnknownError: {"message": "未知错误", "http_code": HTTP_400_BAD_REQUEST},
    # API内部错误，以1101开头
    ParamCheckError: {"message": "参数错误", "http_code": HTTP_400_BAD_REQUEST},
    ParamTypeError: {"message": "数据格式不正确", "http_code": HTTP_400_BAD_REQUEST},
    DataBaseError: {"message": "数据库错误", "http_code": HTTP_400_BAD_REQUEST},
    DataExistsError: {"message": "数据已存在", "http_code": HTTP_400_BAD_REQUEST},
    AccessDenied: {"message": "请求被拒绝", "http_code": HTTP_403_FORBIDDEN},
    RequestTimeout: {"message": "等待超时", "http_code": HTTP_408_REQUEST_TIMEOUT},
    ExternalServerError: {
        "message": "外部服务异常",
        "http_code": HTTP_500_INTERNAL_SERVER_ERROR,
    },
    InsideServerError: {
        "message": "内部服务异常",
        "http_code": HTTP_500_INTERNAL_SERVER_ERROR,
    },
    ServiceUnavailable: {
        "message": "接口异常，请稍后再试",
        "http_code": HTTP_503_SERVICE_UNAVAILABLE,
    },
    MethodNotAllowed: {
        "message": "方法不允许",
        "http_code": HTTP_405_METHOD_NOT_ALLOWED,
    },
    DataNotFound: {"message": "资源不存在", "http_code": HTTP_403_FORBIDDEN},
    DataUpdateError: {"message": "资源更新失败", "http_code": HTTP_400_BAD_REQUEST},
    DataChangeError: {"message": "资源修改失败", "http_code": HTTP_400_BAD_REQUEST},
    DataDelError: {"message": "资源删除失败", "http_code": HTTP_400_BAD_REQUEST},
    # 用户错误，以1200开头
    UserError: {"message": "用户错误", "http_code": HTTP_400_BAD_REQUEST},
    ExpireToken: {
        "message": "令牌过期或权限变动，请重新登录",
        "http_code": HTTP_401_UNAUTHORIZED,
    },
    TokenNotExists: {
        "message": "token不存在或已失效",
        "http_code": HTTP_401_UNAUTHORIZED,
    },
    PermissionDeny: {"message": "用户权限不足", "http_code": HTTP_403_FORBIDDEN},
    UserNotExists: {
        "message": "用户不存在或已注销，请联系管理员",
        "http_code": HTTP_403_FORBIDDEN,
    },
    PasswordError: {"message": "密码错误", "http_code": HTTP_403_FORBIDDEN},
    UserExistsError: {"message": "用户已存在", "http_code": HTTP_403_FORBIDDEN},
    UserNameNotExists: {"message=": "用户不存在", "http_code": HTTP_403_FORBIDDEN},
    UserChangeError: {"message": "修改用户失败", "http_code": HTTP_403_FORBIDDEN},
    UserDelError: {"message": "删除用户失败", "http_code": HTTP_403_FORBIDDEN},
    SourcePasswordError: {"message": "原密码错误", "http_code": HTTP_403_FORBIDDEN},
    ChangePasswordError: {"message": "修改密码失败", "http_code": HTTP_403_FORBIDDEN},
    RoleNotExists: {"message": "角色不存在", "http_code": HTTP_403_FORBIDDEN},
    RoleNameExists: {"message": "角色名已存在", "http_code": HTTP_403_FORBIDDEN},
    RoleChangeError: {"message": "角色修改失败", "http_code": HTTP_403_FORBIDDEN},
    RoleDelError: {"message": "角色删除失败", "http_code": HTTP_403_FORBIDDEN},
    RoleExistsError: {"message": "角色存在相关用户", "http_code": HTTP_403_FORBIDDEN},
}
