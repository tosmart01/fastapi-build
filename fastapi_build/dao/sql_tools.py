# -- coding: utf-8 --
# @Time : 2024/5/27 11:39
# @Author : PinBar
# @File : sql_tools.py
import sqlalchemy
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.query import Query as BaseQuery

version = sqlalchemy.__version__


def query_to_dict_list(query, query_type: str = 'row') -> list[dict]:
    """查询字段并转换为[{data1}, {data2}...]
    只可在查询对象为字段时使用
    """
    if query_type == 'model':
        return [row.to_dict() for row in query]
    if query_type == 'row':
        if version >= '1.4':
            # 使用 _mapping 属性
            dict_list = [dict(row._mapping) for row in query]
            return dict_list
        return [dict(zip(v.keys(), v)) for v in query]
    return []


def query_to_value_list(query, query_type: str = 'row') -> list[list]:
    if query_type == 'model':
        return [[getattr(row, i) for i in row.__table__.columns.keys()] for row in query]
    if query_type == 'row':
        if version >= '1.4':
            # 使用 _mapping 属性
            dict_list = [list(dict(row._mapping).values()) for row in query]
            return dict_list
        return [list(v) for v in query]
    return []


def query_first_to_dict(query, query_type: str = 'row'):
    if query_type == 'model':
        return query.to_dict()
    if query_type == 'row':
        if version >= '1.4':
            # 使用 _mapping 属性
            return query._mapping
        return dict(zip(query.keys(), query))
    return {}


def pagination(query: BaseQuery, page: int = 1, per_page: int = 10, query_type: str = 'row'):
    """
    基于sqlalchemy.BaseQuery.paginate封装的分页器方法，兼容排序的处理
    如果page<1，则不执行分页方法，按照query_col方法获取结果
    返回数据内容和分页配置信息
    :param query: 查询对象
    :param page: 页数，从1开始
    :param per_page: 页容量，默认20
        :param query_type: row | model

    :return: 数据对象和分页信息
    """
    offset = (page - 1) * per_page
    total = query.count()
    paginate = query.offset(offset).limit(per_page)
    result = query_to_dict_list(paginate, query_type=query_type)
    return total, result


async def a_pagination(session: AsyncSession, query: select, page: int = 1, per_page: int = 10,
                       query_type: str = 'row'):
    """
    基于sqlalchemy.BaseQuery.paginate封装的分页器方法，兼容排序的处理
    如果page<1，则不执行分页方法，按照query_col方法获取结果
    返回数据内容和分页配置信息
    :param query: 查询对象
    :param page: 页数，从1开始
    :param per_page: 页容量，默认20
    :param query_type: row | model
    :param session
    :return: 数据对象和分页信息
    """
    offset = (page - 1) * per_page
    subquery = query.subquery()
    count_query = select(func.count()).select_from(subquery)
    result = await session.execute(count_query)
    total = result.scalar()

    paginate = query.offset(offset).limit(per_page)
    results = await session.execute(paginate)
    rows = results.all() if query_type == 'row' else [i[0] for i in results.all()]
    return total, rows
