# -- coding: utf-8 --
# @Time : 2024/5/27 11:38
# @Author : PinBar
# @File : base_dao.py

from typing import Union, List, Dict, Any, Optional, TypeVar, Type

from sqlalchemy import desc, asc, select, func, update, delete, Row
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from .sql_tools import query_to_dict_list, query_first_to_dict, query_to_value_list
from exceptions.custom_exception import NotFoundError, MultipleReturnedError

T = TypeVar("T", bound="Base")


class BaseDao:
    """
    Base BaseController, implements CRUD operations using SQLAlchemy
    """

    model_cls: Type[T] = None
    session: Session = None
    async_session: async_sessionmaker[AsyncSession] = None
    base_filter = ()

    def get_query(self, query_field: Optional[Union[List, tuple]] = None):
        """
        Get a query object filtered by base_filter.

        :param query_field: Fields to be selected in the query        :return:  object
        """
        query = self.session.query(self.model_cls).filter(*self.base_filter)
        if query_field:
            query = self.session.query(*query_field)
        return query

    def get(
            self,
            *args,
            query_field: Optional[Union[List, tuple]] = None,
            to_dict: bool = False,
            raise_not_found: bool = False
    ) -> Union[model_cls, None]:
        """
        Get a single record by specified filter criteria.

        :param args: Filter conditions
        :param query_field: Fields to be selected in the query
        :param to_dict: Whether to return the result as a dictionary
        :param raise_not_found: Whether to raise NotFoundError if no result is found
        :return: Single record or None
        """
        query = self.get_query(query_field)
        query = query.filter(*args)
        if not query.count() and raise_not_found:
            raise NotFoundError()
        if query.count() > 1:
            raise MultipleReturnedError()
        if query and to_dict:
            return (
                query_first_to_dict(query.first()) if query_field
                else query_first_to_dict(query.first(), query_type='model')
            )
        return query.first()

    def get_by_id(
            self,
            model_id: Union[int, str],
            query_field: Optional[Union[List, tuple]] = None,
            to_dict: bool = False,
            id_field: str = None,
            raise_not_found: bool = False
    ) -> Union[model_cls, None]:
        """
        Get a single record by its ID.

        :param model_id: ID of the record
        :param query_field: Fields to be selected in the query
        :param to_dict: Whether to return the result as a dictionary
        :param id_field: Field name of the ID column
        :param raise_not_found: Whether to raise NotFoundError if no result is found
        :return: Single record or None
        """
        id_col = getattr(self.model_cls, id_field or "id", None)
        query = self.get_query(query_field)

        queryset = query.filter(id_col == model_id)
        obj = queryset.first()
        if not obj and raise_not_found:
            raise NotFoundError()

        if to_dict and obj:
            if query_field:
                return query_first_to_dict(obj)
            else:
                return query_first_to_dict(obj, query_type='model')

        return obj

    def get_by_ids(
            self,
            model_ids: List[Union[int, str]],
            query_field: Optional[Union[List, tuple]] = None,
            to_dict: bool = False,
            order_by: Optional[Union[str, List[str], tuple]] = None,
            values_list: bool = False,
            id_field: str = None,
    ) -> List[Union[model_cls, dict, list]]:
        """
        Get multiple records by their IDs.

        :param model_ids: List of IDs
        :param query_field: Fields to be selected in the query
        :param to_dict: Whether to return the result as a dictionary
        :param order_by: Order by conditions
        :param values_list: Whether to return the result as a list of values
        :param id_field: Field name of the ID column
        :return: List of records or an empty list
        """
        id_col = getattr(self.model_cls, id_field or "id", None)
        if id_col is None:
            return []
        query = self.get_query(query_field)
        queryset = query.filter(id_col.in_(model_ids))
        queryset = self.order_by(order=order_by, queryset=queryset)

        if to_dict:
            return (
                query_to_dict_list(queryset)
                if query_field
                else query_to_dict_list(queryset, query_type='model')
            )

        if values_list:
            return (
                query_to_value_list(queryset) if query_field else query_to_value_list(queryset, query_type='model')
            )

        return queryset.all()

    def get_by_field(
            self,
            model_id: Union[int, str],
            field: Optional[str] = None,
            to_dict: bool = False,
            query_field: Optional[Union[List, tuple]] = None,
    ) -> Union[None, list[dict], list[Row[tuple[Any]]]]:
        """
        Get records by a specific field.

        :param model_id: ID of the record
        :param field: Field name to filter by
        :param to_dict: Whether to return the result as a dictionary
        :param query_field: Fields to be selected in the query
        :return: List of records or a single record or None
        """
        id_col = getattr(self.model_cls, field or "id", None)
        if not id_col:
            return None
        query = self.get_query(query_field)
        queryset = query.filter(id_col == model_id)
        if to_dict:
            if query_field:
                return query_to_dict_list(queryset)
            else:
                return query_to_dict_list(queryset, query_type='model')
        return queryset.all()

    def get_by_fields(
            self,
            model_ids: List[Union[int, str]],
            field: Optional[str] = None,
            query_field: Optional[Union[List, tuple]] = None,
            to_dict: bool = False,
            order_by: Optional[Union[str, List[str], tuple]] = None
    ) -> Union[List[model_cls], List[dict], None]:
        """
        Get records by a list of IDs and a specific field.

        :param model_ids: List of IDs
        :param field: Field name to filter by
        :param query_field: Fields to be selected in the query
        :param to_dict: Whether to return the result as a dictionary
        :param order_by: Order by conditions
        :return: List of records or None
        """
        id_col = getattr(self.model_cls, field or "id", None)
        if not id_col:
            return None
        query = self.get_query(query_field)
        queryset = query.filter(id_col.in_(model_ids))
        queryset = self.order_by(order=order_by, queryset=queryset)

        if to_dict:
            return (
                query_to_dict_list(queryset)
                if query_field
                else query_to_dict_list(queryset, query_type='model')
            )
        return queryset.all()

    def get_all(
            self,
            to_dict: bool = False,
            query_field: Optional[Union[List, tuple]] = None,
            order_by: Optional[Union[str, List[str], tuple]] = None
    ) -> List[Union[model_cls, dict]]:
        """
        Get all records that fit the base_filter.

        :param to_dict: Whether to return the result as a dictionary
        :param query_field: Fields to be selected in the query
        :param order_by: Order by conditions
        :return: List of records
        """
        queryset = self.get_query(query_field)
        if to_dict:
            return (
                query_to_dict_list(queryset)
                if query_field
                else query_to_dict_list(queryset, query_type='model')
            )

        queryset = self.order_by(order=order_by, queryset=queryset)
        return queryset.all()

    def create(
            self,
            commit: bool = True,
            **properties: Dict[str, Any],
    ) -> model_cls:
        """
        Create a new record.

        :param commit: Whether to commit the transaction
        :param properties: Properties of the new record
        :return: Created record
        :raises: Exception if creation fails
        """
        model = self.model_cls  # pylint: disable=not-callable
        obj = model(**properties)

        try:
            self.session.add(obj)
            self.session.flush()
            if commit:
                self.session.commit()
        except Exception as ex:  # pragma: no cover
            self.session.rollback()
            raise ex
        return obj

    def update(
            self,
            queryset,
            properties: Dict[str, Any] = None,
            is_commit: bool = True,
    ) -> int:
        """
        Update records in the queryset.

        :param queryset: Queryset to be updated
        :param properties: Properties to be updated
        :param is_commit: Whether to commit the transaction
        :return: Number of records updated
        :raises: Exception if update fails
        """
        try:
            modify_count = queryset.filter(*self.base_filter).update(
                properties, synchronize_session=False
            )
            if is_commit:
                self.session.commit()
        except Exception as ex:
            self.session.rollback()
            raise ex
        return modify_count

    def update_obj(
            self,
            model: model_cls,
            properties: Dict[str, Any],
            commit: bool = True
    ) -> model_cls:
        """
        Update a single model instance.

        :param model: Model instance to be updated
        :param properties: Properties to be updated
        :param commit: Whether to commit the transaction
        :return: Updated model instance
        :raises: Exception if update fails
        """
        if not model:
            return model
        for key, value in properties.items():
            setattr(model, key, value)
        try:
            self.session.merge(model)
            if commit:
                self.session.commit()
        except Exception as ex:  # pragma: no cover
            self.session.rollback()
            raise ex
        return model

    def update_by_id(
            self,
            model_id: Union[int, str],
            properties: Dict[str, Any] = None,
            is_commit: bool = True,
            id_field: str = "id",
            raise_not_found: bool = False
    ) -> int:
        """
        Update a record by its ID.

        :param model_id: ID of the record to be updated
        :param properties: Properties to be updated
        :param is_commit: Whether to commit the transaction
        :param id_field: Field name of the ID column
        :param raise_not_found: Whether to raise NotFoundError if no result is found
        :return: Number of records updated
        :raises: Exception if update fails
        """
        query = self.get_query()
        id_col = getattr(self.model_cls, id_field or "id", None)
        query = query.filter(id_col == model_id)
        if not query.count() and raise_not_found:
            raise NotFoundError()
        modify_count = query.update(properties)
        if is_commit:
            try:
                self.session.flush()
                self.session.commit()
            except Exception as ex:
                self.session.rollback()
                raise ex
        return modify_count

    def update_by_ids(
            self,
            model_ids: List[Union[int, str]],
            properties: Dict[str, Any] = None,
            commit: bool = True,
            id_field: str = "id",
    ) -> int:
        """
        Update multiple records by their IDs.

        :param model_ids: List of IDs
        :param properties: Properties to be updated
        :param commit: Whether to commit the transaction
        :param id_field: Field name of the ID column
        :return: Number of records updated
        :raises: Exception if update fails
        """
        query = self.get_query()
        id_col = getattr(self.model_cls, id_field or "id", None)
        modify_count = query.filter(id_col.in_(model_ids)).update(
            properties, synchronize_session=False
        )
        if commit:
            try:
                self.session.flush()
                self.session.commit()
            except Exception as ex:
                self.session.rollback()
                raise ex
        return modify_count

    def delete_obj(self, model: model_cls, commit: bool = True) -> model_cls:
        """
        Physically delete a model instance.

        :param model: Model instance to be deleted
        :param commit: Whether to commit the transaction
        :return: Deleted model instance
        :raises: Exception if delete fails
        """
        try:
            self.session.delete(model)
            if commit:
                self.session.commit()
        except Exception as ex:  # pragma: no cover
            self.session.rollback()
            raise ex
        return model

    def delete_by_id(
            self,
            model_id: Union[int, str],
            is_commit: bool = True,
            id_field: str = "id",
            raise_not_found: bool = False
    ) -> int:
        """
        Physically delete a record by its ID.

        :param model_id: ID of the record to be deleted
        :param is_commit: Whether to commit the transaction
        :param id_field: Field name of the ID column
        :param raise_not_found: Whether to raise NotFoundError if no result is found
        :return: Number of records deleted
        :raises: Exception if delete fails
        """
        query = self.session.query(self.model_cls)
        id_col = getattr(self.model_cls, id_field or "id", None)
        try:
            query = query.filter(id_col == model_id)
            if not query.count() and raise_not_found:
                raise NotFoundError()
            modify_count = query.delete()
            if is_commit:
                self.session.commit()
        except Exception as ex:
            self.session.rollback()
            raise ex
        return modify_count

    def delete_by_ids(
            self,
            model_ids: List[Union[int, str]],
            is_commit: bool = True,
            id_field: Optional[str] = None
    ) -> int:
        """
        Physically delete multiple records by their IDs.

        :param model_ids: List of IDs
        :param is_commit: Whether to commit the transaction
        :param id_field: Field name of the ID column
        :return: Number of records deleted
        :raises: Exception if delete fails
        """
        query = self.session.query(self.model_cls)
        id_col = getattr(self.model_cls, id_field or "id", None)
        try:
            modify_count = query.filter(id_col.in_(model_ids)).delete(
                synchronize_session=False
            )
            if is_commit:
                self.session.commit()
        except Exception as ex:
            self.session.rollback()
            raise ex
        return modify_count

    def soft_delete_by_id(
            self,
            model_id: Union[int, str],
            delete_field: str = "is_delete",
            is_commit: bool = True,
            id_field: str = "id",
            raise_not_found: bool = False
    ) -> int:
        """
        Logically delete a record by its ID.

        :param model_id: ID of the record to be logically deleted
        :param delete_field: Field name indicating logical deletion
        :param is_commit: Whether to commit the transaction
        :param id_field: Field name of the ID column
        :param raise_not_found: Whether to raise NotFoundError if no result is found
        :return: Number of records logically deleted
        :raises: Exception if logical delete fails
        """
        query = self.get_query()
        id_col = getattr(self.model_cls, id_field or "id", None)
        try:
            query = query.filter(id_col == model_id)
            if not query and raise_not_found:
                raise NotFoundError()
            modify_count = query.update(
                {delete_field: 1}
            )
            if is_commit:
                self.session.commit()
        except Exception as ex:
            self.session.rollback()
            raise ex
        return modify_count

    def soft_delete_by_ids(
            self,
            model_ids: List[Union[int, str]],
            delete_field: str = "is_delete",
            is_commit: bool = True,
            id_field: str = "id"
    ) -> int:
        """
        Logically delete multiple records by their IDs.

        :param model_ids: List of IDs
        :param delete_field: Field name indicating logical deletion
        :param is_commit: Whether to commit the transaction
        :param id_field: Field name of the ID column
        :return: Number of records logically deleted
        :raises: Exception if logical delete fails
        """
        query = self.get_query()
        id_col = getattr(self.model_cls, id_field or "id", None)
        try:
            modify_count = query.filter(id_col.in_(list(model_ids))).update(
                {delete_field: 1},
                synchronize_session=False
            )
            if is_commit:
                self.session.commit()
        except Exception as ex:
            self.session.rollback()
            raise ex
        return modify_count

    @staticmethod
    def order_by(
            order: Optional[Union[str, List[str], tuple]] = None,
            queryset=None
    ):
        """
        Apply order by conditions to the queryset.

        :param order: Order by conditions
        :param queryset: Queryset to be ordered        :return:  queryset
        """
        order_conditions = []
        if isinstance(order, str):
            order_conditions = (
                [desc(order.replace("-", ""))]
                if order.startswith("-")
                else [asc(order)]
            )
        if isinstance(order, (list, tuple)):
            order_conditions = [
                desc(i.replace("-", "")) if i.startswith("-") else asc(i) for i in order
            ]
        return queryset.order_by(*order_conditions)

    def aget_query(
            self,
            query_field: Optional[Union[List, tuple]] = None
    ):
        """
        Get an async query object filtered by base_filter.

        :param query_field: Fields to be selected in the query
        :return: Async query object
        """
        if query_field:
            return select(*query_field).filter(*self.base_filter)
        return select(self.model_cls).filter(*self.base_filter)

    async def aget(
            self,
            *args,
            query_field: Optional[Union[List, tuple]] = None,
            to_dict: bool = False,
            raise_not_found: bool = False
    ) -> Union[model_cls, None]:
        """
        Async get a single record by specified filter criteria.

        :param args: Filter conditions
        :param query_field: Fields to be selected in the query
        :param to_dict: Whether to return the result as a dictionary
        :param raise_not_found: Whether to raise NotFoundError if no result is found
        :return: Single record or None
        """
        async with self.async_session() as session:
            query = self.aget_query(query_field)
            count_query = select(func.count()).select_from(self.model_cls).filter(*self.base_filter, *args)
            count = await session.execute(count_query)
            count = count.scalar()
            if count > 1:
                raise MultipleReturnedError()
            if query_field:
                query = select(*query_field)
            query = query.filter(*args)
            result = await session.execute(query)
            if query_field:
                row = result.first()
            else:
                row = result.first()[0]
            if not row and raise_not_found:
                raise NotFoundError()
            if row and to_dict:
                return (
                    query_first_to_dict(row) if query_field
                    else query_first_to_dict(row, query_type='model')
                )
            return row

    async def aget_by_id(
            self,
            model_id: Union[int, str],
            query_field: Optional[Union[List, tuple]] = None,
            to_dict: bool = False,
            id_field: str = None,
            raise_not_found: bool = False
    ) -> Union[model_cls, None]:
        """
        Async get a single record by its ID.

        :param model_id: ID of the record
        :param query_field: Fields to be selected in the query
        :param to_dict: Whether to return the result as a dictionary
        :param id_field: Field name of the ID column
        :param raise_not_found: Whether to raise NotFoundError if no result is found
        :return: Single record or None
        """
        async with self.async_session() as session:
            id_col = getattr(self.model_cls, id_field or "id", None)
            query = self.aget_query(query_field)
            query = query.filter(id_col == model_id)
            result = await session.execute(query)
            if query_field:
                obj = result.first()
            else:
                obj = result.first()[0]
            if not obj and raise_not_found:
                raise NotFoundError()
            if to_dict and obj:
                if query_field:
                    return query_first_to_dict(obj)
                else:
                    return query_first_to_dict(obj, query_type='model')
            return obj

    async def aget_by_ids(
            self,
            model_ids: List[Union[int, str]],
            query_field: Optional[Union[List, tuple]] = None,
            to_dict: bool = False,
            order_by: Optional[Union[str, List[str], tuple]] = None,
            values_list: bool = False,
            id_field: str = None,
    ) -> List[Union[model_cls, dict, list]]:
        """
        Async get multiple records by their IDs.

        :param model_ids: List of IDs
        :param query_field: Fields to be selected in the query
        :param to_dict: Whether to return the result as a dictionary
        :param order_by: Order by conditions
        :param values_list: Whether to return the result as a list of values
        :param id_field: Field name of the ID column
        :return: List of records or an empty list
        """
        async with self.async_session() as session:
            id_col = getattr(self.model_cls, id_field or "id", None)
            if id_col is None:
                return []
            query = self.aget_query(query_field)
            query = query.filter(id_col.in_(model_ids))
            queryset = self.order_by(order=order_by, queryset=query)
            result = await session.execute(queryset)
            rows = result.all() if query_field else [i[0] for i in result.all()]
            if to_dict:
                return (
                    query_to_dict_list(rows)
                    if query_field
                    else query_to_dict_list(rows, query_type='model')
                )
            if values_list:
                return (
                    query_to_value_list(rows) if query_field else query_to_value_list(rows, query_type='model')
                )
            return rows

    async def a_create(
            self,
            commit: bool = True,
            **properties: Dict[str, Any]
    ) -> model_cls:
        """
        Async create a new record.

        :param commit: Whether to commit the transaction
        :param properties: Properties of the new record
        :return: Created record
        :raises: Exception if creation fails
        """
        async with self.async_session() as session:
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
            return obj

    async def a_update(
            self,
            queryset: select,
            properties: Dict[str, Any] = None,
            id_col: str = 'id',
            is_commit: bool = True,
    ) -> int:
        """
        Async update records in the queryset.

        :param queryset: Queryset to be updated
        :param properties: Properties to be updated
        :param id_col: Field name of the ID column
        :param is_commit: Whether to commit the transaction
        :return: Number of records updated
        :raises: Exception if update fails
        """
        async with self.async_session() as session:
            try:
                subquery = queryset.subquery()
                col = getattr(self.model_cls, id_col)
                stmt = (
                    update(self.model_cls)
                    .where(col.in_(getattr(subquery.c, id_col)))
                    .values(**properties)
                    .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(stmt)
                if is_commit:
                    await session.commit()
            except Exception as ex:
                self.session.rollback()
                raise ex
            else:
                rowcount: int = result.rowcount
                return rowcount

    async def a_update_obj(
            self,
            model: model_cls,
            properties: Dict[str, Any],
            commit: bool = True
    ) -> model_cls:
        """
        Async update a single model instance.

        :param model: Model instance to be updated
        :param properties: Properties to be updated
        :param commit: Whether to commit the transaction
        :return: Updated model instance
        :raises: Exception if update fails
        """
        async with self.async_session() as session:
            for key, value in properties.items():
                setattr(model, key, value)
            try:
                await session.merge(model)
                if commit:
                    await session.commit()
            except Exception as ex:  # pragma: no cover
                await session.rollback()
                raise ex
            return model

    async def a_update_by_id(
            self,
            model_id: Union[int, str],
            properties: Dict[str, Any] = None,
            commit: bool = True,
            id_field: str = "id",
            raise_not_found: bool = False
    ) -> int:
        """
        Async update a record by its ID.

        :param model_id: ID of the record to be updated
        :param properties: Properties to be updated
        :param commit: Whether to commit the transaction
        :param id_field: Field name of the ID column
        :param raise_not_found: Whether to raise NotFoundError if no result is found
        :return: Number of records updated
        :raises: Exception if update fails
        """
        if raise_not_found:
            await self.aget_by_id(model_id, id_field=id_field)
        async with self.async_session() as session:
            try:
                col = getattr(self.model_cls, id_field)
                stmt = (
                    update(self.model_cls)
                    .where(col == model_id, *self.base_filter)
                    .values(**properties)
                    .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(stmt)
                if commit:
                    await session.commit()
            except Exception as ex:
                self.session.rollback()
                raise ex
            else:
                return result.rowcount

    async def a_update_by_ids(
            self,
            model_ids: List[Union[int, str]],
            properties: Dict[str, Any] = None,
            commit: bool = True,
            id_field: str = "id",
    ) -> int:
        """
        Async update multiple records by their IDs.

        :param model_ids: List of IDs
        :param properties: Properties to be updated
        :param commit: Whether to commit the transaction
        :param id_field: Field name of the ID column
        :return: Number of records updated
        :raises: Exception if update fails
        """
        async with self.async_session() as session:
            try:
                col = getattr(self.model_cls, id_field)
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
                self.session.rollback()
                raise ex
            else:
                return result.rowcount

    async def a_delete_obj(
            self,
            model: model_cls,
            commit: bool = True
    ) -> model_cls:
        """
        Async physically delete a model instance.

        :param model: Model instance to be deleted
        :param commit: Whether to commit the transaction
        :return: Deleted model instance
        :raises: Exception if delete fails
        """
        async with self.async_session() as session:
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
            id_field: str = "id",
            raise_not_found: bool = False
    ) -> int:
        """
        Async physically delete a record by its ID.

        :param model_id: ID of the record to be deleted
        :param commit: Whether to commit the transaction
        :param id_field: Field name of the ID column
        :param raise_not_found: Whether to raise NotFoundError if no result is found
        :return: Number of records deleted
        :raises: Exception if delete fails
        """
        if raise_not_found:
            await self.aget_by_id(model_id, id_field=id_field, raise_not_found=raise_not_found)
        async with self.async_session() as session:
            try:
                id_col = getattr(self.model_cls, id_field or "id", None)
                query = delete(self.model_cls).where(id_col == model_id)
                result = await session.execute(query)
                if commit:
                    await session.commit()
            except Exception as ex:
                await session.rollback()
                raise ex
            return result.rowcount

    async def a_delete_by_ids(
            self,
            model_ids: List[Union[int, str]],
            commit: bool = True,
            id_field: str = "id"
    ) -> int:
        """
        Async physically delete multiple records by their IDs.

        :param model_ids: List of IDs
        :param commit: Whether to commit the transaction
        :param id_field: Field name of the ID column
        :return: Number of records deleted
        :raises: Exception if delete fails
        """
        async with self.async_session() as session:
            try:
                id_col = getattr(self.model_cls, id_field or "id", None)
                query = delete(self.model_cls).where(id_col.in_(model_ids))
                result = await session.execute(query)
                if commit:
                    await session.commit()
            except Exception as ex:
                await session.rollback()
                raise ex
            return result.rowcount

    async def a_soft_delete_obj(
            self,
            model: model_cls,
            commit: bool = True,
            delete_field: str = "is_delete",
    ) -> model_cls:
        """
        Async logically delete a model instance.

        :param model: Model instance to be logically deleted
        :param commit: Whether to commit the transaction
        :param delete_field: Field name indicating logical deletion
        :return: Logically deleted model instance
        """
        res = await self.a_update_obj(model, commit=commit, properties={delete_field: True})
        return res

    async def a_soft_delete_by_id(
            self,
            model_id: Union[int, str],
            delete_field: str = "is_delete",
            commit: bool = True,
            id_field: str = "id",
            raise_not_found: bool = False
    ) -> int:
        """
        Async logically delete a record by its ID.

        :param model_id: ID of the record to be logically deleted
        :param delete_field: Field name indicating logical deletion
        :param commit: Whether to commit the transaction
        :param id_field: Field name of the ID column
        :param raise_not_found: Whether to raise NotFoundError if no result is found
        :return: Number of records logically deleted
        """
        res = await self.a_update_by_id(model_id, id_field=id_field, commit=commit, raise_not_found=raise_not_found,
                                        properties={delete_field: True})
        return res

    async def a_soft_delete_by_ids(
            self,
            model_ids: List[Union[int, str]],
            delete_field: str = "is_delete",
            commit: bool = True,
            id_field: str = "id",
    ) -> int:
        """
        Async logically delete multiple records by their IDs.

        :param model_ids: List of IDs
        :param delete_field: Field name indicating logical deletion
        :param commit: Whether to commit the transaction
        :param id_field: Field name of the ID column
        :return: Number of records logically deleted
        """
        res = await self.a_update_by_ids(model_ids, id_field=id_field, commit=commit,
                                         properties={delete_field: True})
        return res
