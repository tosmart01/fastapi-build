# -- coding: utf-8 --
# @Time : 2024/5/16 10:14
# @Author : PinBar
# @File : decorator.py
from fastapi.routing import *


def api_description(response_model: Any = Default(None),
                    status_code: Optional[int] = None,
                    tags: Optional[List[Union[str, Enum]]] = None,
                    dependencies: Optional[Sequence[params.Depends]] = None,
                    summary: Optional[str] = None,
                    description: Optional[str] = None,
                    response_description: str = "Successful Response",
                    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
                    deprecated: Optional[bool] = None,
                    operation_id: Optional[str] = None,
                    response_model_include: Optional[IncEx] = None,
                    response_model_exclude: Optional[IncEx] = None,
                    response_model_by_alias: bool = True,
                    response_model_exclude_unset: bool = False,
                    response_model_exclude_defaults: bool = False,
                    response_model_exclude_none: bool = False,
                    include_in_schema: bool = True,
                    response_class: Union[Type[Response], DefaultPlaceholder] = Default(
                        JSONResponse
                    ),
                    name: Optional[str] = None,
                    route_class_override: Optional[Type[APIRoute]] = None,
                    callbacks: Optional[List[BaseRoute]] = None,
                    openapi_extra: Optional[Dict[str, Any]] = None,
                    generate_unique_id_function: Union[
                        Callable[[APIRoute], str], DefaultPlaceholder
                    ] = Default(generate_unique_id)):
    def wrapper(func):
        names = [
            ('response_model', response_model),
            ('status_code', status_code),
            ('tags', tags),
            ('dependencies', dependencies),
            ('summary', summary),
            ('description', description),
            ('response_description', response_description),
            ('responses', responses),
            ('deprecated', deprecated),
            ('operation_id', operation_id),
            ('response_model_include', response_model_include),
            ('response_model_exclude', response_model_exclude),
            ('response_model_by_alias', response_model_by_alias),
            ('response_model_exclude_unset', response_model_exclude_unset),
            ('response_model_exclude_defaults', response_model_exclude_defaults),
            ('response_model_exclude_none', response_model_exclude_none),
            ('include_in_schema', include_in_schema),
            ('response_class', response_class),
            ('name', name),
            ('route_class_override', route_class_override),
            ('callbacks', callbacks),
            ('openapi_extra', openapi_extra),
            ('generate_unique_id_function', generate_unique_id_function)
        ]
        params = {}
        for field, value in names:
            if value:
                params[field] = value
        setattr(func, '_extra_params', params)
        return func

    return wrapper
