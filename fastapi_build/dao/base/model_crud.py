#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright DataGrand Tech Inc. All Rights Reserved.
Author: Zoe
File: manager.py
Time: 2024/12/2
"""
from typing import Union, List, Dict, Any, Optional, TypeVar, Type, TYPE_CHECKING

from sqlalchemy import update, delete, ColumnElement

from dao.base.queryset import QuerySet

try:
    from sqlalchemy.engine import Row, Result
    from sqlalchemy.sql import Select
except:  # noqa
    from sqlalchemy import Select, Result, Row
from sqlalchemy.ext.asyncio.session import AsyncSession

from core.context import g
from exceptions.custom_exception import NotFoundError

if TYPE_CHECKING:
    from models import BaseModel  # noqa
    from sqlalchemy.schema import Table  # noqa

T = TypeVar("T", bound="Union[BaseModel,Table]")
Rs = TypeVar("Rs", bound="Result[Union[BaseModel,Table, Any]]")


class ModelManager(object):
    model_cls: Type[T] = None  # noqa
    base_filter = ()

    @property
    def _base_filter(self):
        return list(self.base_filter)

    def get_query(self, query_field: Optional[Union[List, tuple]] = None):
        query = g.session_sync.query(self.model_cls).filter(*self.base_filter)
        if query_field:
            query = g.session_sync.query(*query_field)
        return query

    def create(
            self,
            commit: bool = True,
            **properties: Dict[Union[ColumnElement, str], Any],
    ) -> Rs:
        model = self.model_cls  # pylint: disable=not-callable
        obj = model(**properties)

        try:
            g.session_sync.add(obj)
            g.session_sync.flush()
            if commit:
                g.session_sync.commit()
        except Exception as ex:  # pragma: no cover
            g.session_sync.rollback()
            raise ex
        return obj

    @staticmethod
    def update_obj(
            model: Rs,
            properties: Dict[Union[ColumnElement, str], Any],
            commit: bool = True
    ) -> Rs:
        if not model:
            return model
        for key, value in properties.items():
            setattr(model, key if isinstance(key, str) else key.name, value)
        try:
            g.session_sync.merge(model)
            if commit:
                g.session_sync.commit()
        except Exception as ex:  # pragma: no cover
            g.session_sync.rollback()
            raise ex
        return model

    def update_by_id(
            self,
            model_id: Union[int, str],
            properties: Dict[Union[ColumnElement, str], Any] = None,
            commit: bool = True,
            raise_not_found: bool = False
    ) -> int:
        obj = QuerySet(model_cls=self.model_cls, filters=self._base_filter).get_by_id(model_id, raise_not_found=raise_not_found)
        new_obj = self.update_obj(obj, properties, commit=commit)
        return new_obj

    def update_by_ids(
            self,
            model_ids: List[Union[int, str]],
            properties: Dict[Union[ColumnElement, str], Any] = None,
            commit: bool = True,
    ) -> int:
        query = self.get_query()
        id_col = getattr(self.model_cls, "id", None)
        modify_count = query.filter(id_col.in_(model_ids)).update(
            properties, synchronize_session=False
        )
        if commit:
            try:
                g.session_sync.flush()
                g.session_sync.commit()
            except Exception as ex:
                g.session_sync.rollback()
                raise ex
        return modify_count

    @staticmethod
    def delete_obj(model: Rs, commit: bool = True) -> Rs:
        try:
            g.session_sync.delete(model)
            if commit:
                g.session_sync.commit()
        except Exception as ex:  # pragma: no cover
            g.session_sync.rollback()
            raise ex
        return model

    def delete_by_id(
            self,
            model_id: Union[int, str],
            commit: bool = True,
            raise_not_found: bool = False
    ) -> int:
        obj = QuerySet(model_cls=self.model_cls, filters=self._base_filter).get_by_id(model_id, raise_not_found=raise_not_found)
        return self.delete_obj(obj, commit=commit)

    def delete_by_ids(
            self,
            model_ids: List[Union[int, str]],
            commit: bool = True,
    ) -> int:
        query = g.session_sync.query(self.model_cls)
        id_col = getattr(self.model_cls, "id", None)
        try:
            modify_count = query.filter(id_col.in_(model_ids)).delete(
                synchronize_session=False
            )
            if commit:
                g.session_sync.commit()
        except Exception as ex:
            g.session_sync.rollback()
            raise ex
        return modify_count

    def soft_delete_obj(
            self,
            model: Rs,
            commit: bool = True,
            delete_field: str = "is_delete",
    ) -> Rs:
        res = self.update_obj(model, commit=commit, properties={delete_field: True})
        return res

    def soft_delete_by_id(
            self,
            model_id: Union[int, str],
            delete_field: str = "is_delete",
            commit: bool = True,
            raise_not_found: bool = False
    ) -> int:
        query = self.get_query()
        id_col = getattr(self.model_cls, "id", None)
        try:
            query = query.filter(id_col == model_id)
            if not query.first() and raise_not_found:
                raise NotFoundError()
            modify_count = query.update(
                {delete_field: 1}
            )
            if commit:
                g.session_sync.commit()
        except Exception as ex:
            g.session_sync.rollback()
            raise ex
        return modify_count

    def soft_delete_by_ids(
            self,
            model_ids: List[Union[int, str]],
            delete_field: str = "is_delete",
            commit: bool = True,
    ) -> int:
        query = self.get_query()
        id_col = getattr(self.model_cls, "id", None)
        try:
            modify_count = query.filter(id_col.in_(list(model_ids))).update(
                {delete_field: 1},
                synchronize_session=False
            )
            if commit:
                g.session_sync.commit()
        except Exception as ex:
            g.session_sync.rollback()
            raise ex
        return modify_count

    async def a_create(
            self,
            commit: bool = True,
            **properties: Dict[Union[ColumnElement, str], Any]
    ) -> Rs:
        session: AsyncSession = g.session
        model = self.model_cls
        obj = model(**properties)
        try:
            session.add(obj)
            await session.flush()
            if commit:
                await session.commit()
        except Exception as ex:
            await session.rollback()
            raise ex
        await session.refresh(obj)
        return obj

    @staticmethod
    async def a_update_obj(
            model: Rs,
            properties: Dict[Union[ColumnElement, str], Any],
            commit: bool = True
    ) -> Rs:
        session: AsyncSession = g.session
        for key, value in properties.items():
            setattr(model, key if isinstance(key, str) else key.name, value)
        try:
            if commit:
                await session.commit()
            await session.refresh(model)
        except Exception as ex:  # pragma: no cover
            await session.rollback()
            raise ex
        return model

    async def a_update_by_id(
            self,
            model_id: Union[int, str],
            commit: bool = True,
            raise_not_found: bool = False,
            properties: dict = None,

    ) -> int:
        obj = await QuerySet(model_cls=self.model_cls, filters=self._base_filter).aget_by_id(model_id, raise_not_found=raise_not_found)
        return await self.a_update_obj(obj, commit=commit, properties=properties)

    async def a_update_by_ids(
            self,
            model_ids: List[Union[int, str]],
            properties: Dict[str, Any] = None,
            commit: bool = True,
    ) -> int:
        session: AsyncSession = g.session
        try:
            col = getattr(self.model_cls, "id")
            stmt = (
                update(self.model_cls)
                .where(col.in_(model_ids), *self.base_filter)
                .values(**properties)
                .execution_options(synchronize_session="fetch")
            )
            result = await session.execute(stmt)
            if commit:
                await session.commit()
        except Exception as ex:
            await g.session.rollback()
            raise ex
        else:
            return result.rowcount  # noqa

    @staticmethod
    async def a_delete_obj(
            model: Rs,
            commit: bool = True
    ) -> Rs:
        session: AsyncSession = g.session
        try:
            await session.delete(model)
            if commit:
                await session.commit()
        except Exception as ex:
            await session.rollback()
            raise ex
        return model

    async def a_delete_by_id(
            self,
            model_id: Union[int, str],
            commit: bool = True,
            raise_not_found: bool = False
    ) -> int:
        obj = await QuerySet(model_cls=self.model_cls, filters=self._base_filter).aget_by_id(model_id, raise_not_found=raise_not_found)
        return await self.a_delete_obj(obj, commit=commit)

    async def a_delete_by_ids(
            self,
            model_ids: List[Union[int, str]],
            commit: bool = True,
    ) -> int:
        session: AsyncSession = g.session
        try:
            query = delete(self.model_cls).where(self.model_cls.id.in_(model_ids))
            result = await session.execute(query)
            if commit:
                await session.commit()
        except Exception as ex:
            await session.rollback()
            raise ex
        return result.rowcount  # noqa

    async def a_soft_delete_obj(
            self,
            model: Rs,
            commit: bool = True,
            delete_field: str = "is_delete",
    ) -> Rs:
        res = await self.a_update_obj(model, commit=commit, properties={delete_field: True})
        return res

    async def a_soft_delete_by_id(
            self,
            model_id: Union[int, str],
            delete_field: str = "is_delete",
            commit: bool = True,
            raise_not_found: bool = False
    ) -> int:
        res = await self.a_update_by_id(model_id, commit=commit, raise_not_found=raise_not_found,
                                        properties={delete_field: True})
        return res

    async def a_soft_delete_by_ids(
            self,
            model_ids: List[Union[int, str]],
            delete_field: str = "is_delete",
            commit: bool = True,
    ) -> int:
        res = await self.a_update_by_ids(model_ids, commit=commit,
                                         properties={delete_field: True})
        return res
