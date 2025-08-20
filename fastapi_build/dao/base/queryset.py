#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright DataGrand Tech Inc. All Rights Reserved.
Author: Zoe
File: queryset.py
Time: 2024/11/26
"""
from itertools import chain
from typing import Type, Union, Optional, TypeVar, Any, TYPE_CHECKING, overload, Dict

from sqlalchemy import select, exists, not_, update, delete
from sqlalchemy.sql.elements import BinaryExpression, ColumnElement

try:
    from sqlalchemy.sql import Select
except:  # noqa
    from sqlalchemy import Select

if TYPE_CHECKING:
    from models import BaseModel  # noqa
    from sqlalchemy.schema import Table  # noqa

from core.context import g
from dao.base.database_fetch import database
from exceptions.custom_exception import NotFoundError

T = TypeVar("T", bound="Union[BaseModel,Table]")
Rs = TypeVar("Rs", bound="Result[Union[BaseModel,Table, Any]]")

Self = TypeVar("Self", bound="QuerySet")


class QuerySet:

    def __init__(
            self, filters: list[BinaryExpression] = None, model_cls: Type["T"] = None
    ):
        self._order_by: Optional[list[ColumnElement]] = []
        self._query: Optional[Select] = None
        self._filters = filters or []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._fields: Optional[Union[list[ColumnElement], list[str]]] = []
        self.model_cls = model_cls
        self._iterator = None

    def _get_model_field(self, *fields: Union[ColumnElement, str]) -> list[ColumnElement]:
        model_fields = []
        for field in fields:
            if isinstance(field, str):
                model_fields.append(getattr(self.model_cls, field))
            else:
                model_fields.append(field)
        return model_fields

    def _get_values_query(self, *fields: Union[ColumnElement, str]) -> Select:
        if fields:
            query_columns = self._get_model_field(*fields)
            query = self._build_query(query_columns)
        else:
            query = self.query
        return query

    def _build_query(self, select_columns: list[ColumnElement] = None) -> Select:
        entities = (
            select(self.model_cls) if not select_columns else select(*select_columns)
        )
        if self._fields:
            columns = []
            for field in self._fields:
                if isinstance(field, str):
                    col = getattr(self.model_cls, field, None)
                    columns.append(col)
                else:
                    columns.append(field)
            entities = select(*columns)
        where = []
        if self._filters:
            where.extend(self._filters)
        query = entities.where(*where)
        if self._order_by:
            query = query.order_by(*self._order_by)
        if self._limit:
            query = query.limit(self._limit)
        if self._offset:
            query = query.offset(self._offset)
        return query

    @overload
    def query(self) -> Select:
        ...

    @property
    def query(self) -> Select:
        if self._query is None:
            self._query = self._build_query()
        return self._query

    def __iter__(self):
        return self

    def __next__(self):
        if not self._iterator:
            self._iterator = g.session_sync.execute(self.query).scalars().yield_per(10)
        return next(self._iterator)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._iterator:
            self._iterator = await g.session.stream(self.query)
        row = await self._iterator.__anext__()
        return database.convert_one(row)

    def with_columns(self, *columns: Union[ColumnElement, str]) -> Self:
        columns = self._get_model_field(*columns)
        self._fields = columns
        return self

    def _get(self, *where_clauses: Union[ColumnElement, str], **kw):
        where = list(where_clauses)
        for key, value in kw.items():
            where.append(self._get_model_field(key)[0] == value)
        self._limit = 1
        self._filters.extend(where)

    def get(self, *where_clauses: Union[ColumnElement, str], to_dict: bool = False, raise_not_found: bool = False,
            **kw) -> T:
        self._get(*where_clauses, **kw)
        obj = database.fetchone(self.query, to_dict=to_dict)
        if not obj and raise_not_found:
            raise NotFoundError()
        return obj

    async def aget(self, *where_clauses: Union[ColumnElement, str], to_dict: bool = False,
                   raise_not_found: bool = False,
                   **kw) -> T:
        self._get(*where_clauses, **kw)
        obj = await database.a_fetchone(self.query, to_dict=to_dict)
        if not obj and raise_not_found:
            raise NotFoundError()
        return obj

    def get_by_id(self, _id: Union[int, str], to_dict: bool = False,
                  raise_not_found: bool = False) -> Optional[T]:
        self._get(self.model_cls.id == _id)
        obj = database.fetchone(self.query, to_dict=to_dict)
        if not obj and raise_not_found:
            raise NotFoundError()
        return obj

    async def aget_by_id(self, _id: Union[int, str], to_dict: bool = False,
                         raise_not_found: bool = False) -> Optional[T]:
        self._get(self.model_cls.id == _id)
        obj = await database.a_fetchone(self.query, to_dict=to_dict)
        if not obj and raise_not_found:
            raise NotFoundError()
        return obj

    def filter(self, *where_clause: BinaryExpression) -> Self:
        self._filters.extend(list(where_clause))
        return self

    def all(self) -> list[T]:
        return database.fetchall(self.query)

    async def a_all(self) -> list["T"]:
        return database.a_fetchall(self.query)

    def first(self, to_dict: bool = False) -> Optional[Union["T", Any]]:
        query = self.query.limit(1)
        return database.fetchone(query, to_dict=to_dict)

    async def afirst(self, to_dict: bool = False) -> Optional[Union["T", Any]]:
        query = self.query.limit(1)
        return await database.a_fetchone(query, to_dict=to_dict)

    def last(self, field: Union[str, ColumnElement] = None, to_dict: bool = False) -> Optional[Union["T", Any]]:
        if field:
            field = self._get_model_field(field)[0]
        if not field:
            field = self.model_cls.id
        query = self.query.order_by(field.desc()).limit(1)
        return database.fetchone(query, to_dict=to_dict)

    async def alast(
            self, field: Union[str, ColumnElement] = None, to_dict: bool = False
    ) -> Optional[Union["T", Any]]:
        if field:
            field = self._get_model_field(field)[0]
        if not field:
            field = self.model_cls.id
        query = self.query.order_by(field.desc()).limit(1)
        return await database.a_fetchone(query, to_dict=to_dict)

    def values(self, *fields: Union[ColumnElement, str]) -> list[dict]:
        query = self._get_values_query(*fields)
        return database.fetchall(query, to_dict=True)

    async def avalues(self, *fields: Union[ColumnElement, str]) -> list[dict]:
        query = self._get_values_query(*fields)
        return await database.a_fetchall(query, to_dict=True)

    def values_list(self, *fields: Union[ColumnElement, str], flat: bool = False) -> Union[list[list], list]:
        query = self._get_values_query(*fields)
        data = database.fetchall(query, value_list=True)
        if flat:
            return list(chain(*data))
        return data

    async def avalues_list(
            self, *fields: Union[ColumnElement, str], flat: bool = False
    ) -> Union[list[list], list]:
        query = self._get_values_query(*fields)
        data = await database.a_fetchall(query, value_list=True)
        if flat:
            return list(chain(*data))
        return data

    def count(self) -> int:
        return database.fetch_count(self.query)

    async def acount(self) -> int:
        return await database.a_fetch_count(self.query)

    def exists(self) -> bool:
        query = select(exists().where(*self._filters))
        return database.scalar(query)

    async def aexists(self) -> bool:
        query = select(exists().where(*self._filters))
        return await database.ascalar(query)

    def exclude(self, *where_clause: BinaryExpression) -> Self:
        self._filters.append(not_(*where_clause))
        return self

    def order_by(self, *fields: Union[BinaryExpression, str]) -> Self:
        for field in fields:
            if isinstance(field, str):
                if field.strip():
                    if field.startswith("-"):
                        column = self._get_model_field(field[1:])[0]
                        self._order_by.append(column.desc())
                    else:
                        column = self._get_model_field(field)[0]
                        self._order_by.append(column)
            else:
                self._order_by.append(field)
        return self

    def limit(self, n: int) -> Self:
        self._limit = n
        return self

    def offset(self, n: int) -> Self:
        self._offset = n
        return self

    def aggregate(self, *aggregates) -> dict:
        """
        Performs aggregate calculations such as sum, avg, min, max.

        :param aggregates: Aggregation functions applied to columns.
        :return: A dictionary with aggregate results.
        """
        aggregate_query = select(*aggregates).where(*self._filters)
        result = database.fetchone(aggregate_query, to_dict=True)
        return result

    async def a_aggregate(self, *aggregates) -> dict:
        """
        Asynchronous aggregate calculations such as sum, avg, min, max.

        :param aggregates: Aggregation functions applied to columns.
        :return: A dictionary with aggregate results.
        """
        aggregate_query = select(*aggregates).where(*self._filters)
        result = await database.a_fetchone(aggregate_query, to_dict=True)
        return result

    def pagination(self, page: int = None, per_page: int = None) -> tuple[int, list[dict]]:
        total, data = database.pagination(self.query, page, per_page)
        return total, data

    async def a_pagination(self, page: int = None, per_page: int = None) -> tuple[int, list[dict]]:
        total, data = await database.a_pagination(self.query, page, per_page)
        return total, data

    async def aupdate(self, **properties) -> int:
        stmt = update(self.model_cls).where(*self._filters).values(**properties).execution_options(
            synchronize_session="fetch")
        return await database.aexecute_update(stmt)

    def update(self,  **properties) -> int:
        stmt = update(self.model_cls).where(*self._filters).values(**properties).execution_options(
            synchronize_session="fetch")
        return database.execute_update(stmt)

    def delete(self) -> int:
        stmt = delete(self.model_cls).where(*self._filters)
        return database.execute_update(stmt)

    async def adelete(self):
        stmt = delete(self.model_cls).where(*self._filters)
        return await database.aexecute_update(stmt)

    def soft_delete(self) -> int:
        return self.update(**{self.model_cls.is_delete: True})

    async def asoft_delete(self) -> int:
        return await self.aupdate(**{self.model_cls.is_delete: True})

    def as_sql(self):
        return self._build_query()
