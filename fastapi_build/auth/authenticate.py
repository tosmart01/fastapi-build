# -- coding: utf-8 --
# @Time : 2024/5/27 14:10
# @Author : PinBar
# @File : auth.py
# from functools import wraps
#
# from fastapi import Request
#
# from auth.hashers import verify_password, decode_access_token
# from db.models.user import User
# from exceptions.custom_exception import AuthDenyError
#
#
# def get_current_user(user_id) -> User:
#     return User.objects.get_by_id(user_id, raise_not_found=True)
#
#
# def login_required(func):
#     @wraps(func)
#     def wrapped_view(request: Request, *args, **kwargs):
#         token = request.headers.get('Authorization')
#         if not token:
#             raise AuthDenyError()
#         token = token.split('Bearer ')[1].strip()
#         try:
#             user_info = decode_access_token(token)
#         except Exception:
#             raise AuthDenyError()
#         else:
#             user = get_current_user(user_info['user_id'])
#             request.state.user = user
#             return func(request, *args, **kwargs)
#
#     return wrapped_view
#
#
# def login(username: str, password: str) -> bool:
#     user = User.objects.get_by_id(username, id_field='username')
#     return verify_password(password, user.password)
