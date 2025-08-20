
from typing import TypeVar, Type, Optional, Union, Any, TYPE_CHECKING

from sqlalchemy import BinaryExpression, ColumnElement

from dao import QuerySet
from dao import ModelManager

if TYPE_CHECKING:
    from sqlalchemy.schema import Table
    from models import BaseModel  # noqa

T = TypeVar("T", bound="BaseModel | Table")


class BaseDao(ModelManager):
    """
    Base BaseController, implements CRUD operations using SQLAlchemy
    """

    model_cls: Type[T] = None
    base_filter = ()

    def filter(self, *where_clause: BinaryExpression) -> QuerySet:
        """
        Apply filter conditions to the query.

        :param where_clause: One or more filter conditions.
        :return: QuerySet with applied filters.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter(*where_clause, )

    def all(self) -> list["Table"]:
        """
        Retrieve all rows for the model.

        :return: List of all rows in the table.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().all()

    def first(self, to_dict: bool = False) -> Optional[Union["T", Any]]:
        """
        Retrieve the first row of the query.

        :param to_dict: Whether to return the result as a dictionary.
        :return: The first row or None if no rows match.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().first(to_dict)

    async def afirst(self, to_dict: bool = False) -> Optional[Union["T", Any]]:
        """
        Asynchronously retrieve the first row of the query.

        :param to_dict: Whether to return the result as a dictionary.
        :return: The first row or None if no rows match.
        """
        return await QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().afirst(to_dict)

    def last(
            self, field: Union[str, ColumnElement] = None, to_dict: bool = False
    ) -> Optional[Union["T", Any]]:
        """
        Retrieve the last row of the query.

        :param field: Field to order by for determining the last row.
        :param to_dict: Whether to return the result as a dictionary.
        :return: The last row or None if no rows match.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().last(field, to_dict)

    async def alast(
            self, field: Union[str, ColumnElement] = None, to_dict: bool = False
    ) -> Optional[Union["T", Any]]:
        """
        Asynchronously retrieve the last row of the query.

        :param field: Field to order by for determining the last row.
        :param to_dict: Whether to return the result as a dictionary.
        :return: The last row or None if no rows match.
        """
        return await QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().alast(field, to_dict)

    def values(self, *fields: Union[ColumnElement, str]) -> list[dict]:
        """
        Retrieve rows as dictionaries based on selected fields.

        :return: List of dictionaries representing rows.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().values(*fields)

    async def avalues(self, *fields: Union[ColumnElement, str]) -> list[dict]:
        """
        Asynchronously retrieve rows as dictionaries based on selected fields.

        :return: List of dictionaries representing rows.
        """
        return await QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().avalues(*fields)

    def values_list(
            self, *fields: Union[ColumnElement, str], flat: bool = False
    ) -> Union[list[list], list]:
        """
        Retrieve rows as lists based on selected fields.

        :param flat: If True, flatten the list structure.
        :return: List of lists or a flattened list.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().values_list(*fields, flat=flat)

    async def avalues_list(
            self, *fields: Union[ColumnElement, str], flat: bool = False
    ) -> Union[list[list], list]:
        """
        Asynchronously retrieve rows as lists based on selected fields.

        :param flat: If True, flatten the list structure.
        :return: List of lists or a flattened list.
        """
        return await QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().avalues_list(*fields,
                                                                                                         flat=flat)

    def count(self) -> int:
        """
        Count the number of rows matching the query.

        :return: The count of rows.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().count()

    async def acount(self) -> int:
        """
        Asynchronously count the number of rows matching the query.

        :return: The count of rows.
        """
        return await QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().acount()

    def exists(self) -> bool:
        """
        Check if any rows match the query.

        :return: True if rows exist, otherwise False.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().exists()

    async def aexists(self) -> bool:
        """
        Asynchronously check if any rows match the query.

        :return: True if rows exist, otherwise False.
        """
        return await QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().aexists()

    def exclude(self, *where_clause: BinaryExpression) -> QuerySet:
        """
        Exclude rows matching certain conditions.

        :param where_clause: Conditions to exclude from the query.
        :return: QuerySet with exclusions applied.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().exclude(*where_clause)

    def order_by(self, *fields: Union[str, ColumnElement]) -> QuerySet:
        """
        Apply ordering to the query.

        :param fields: Fields to order by.
        :return: QuerySet with ordering applied.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().order_by(*fields)

    def limit(self, n: int) -> QuerySet:
        """
        Limit the number of rows returned by the query.

        :param n: The maximum number of rows to return.
        :return: QuerySet with the limit applied.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().limit(n)

    def offset(self, n: int) -> QuerySet:
        """
        Skip a certain number of rows in the query results.

        :param n: The number of rows to skip.
        :return: QuerySet with the offset applied.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().offset(n)

    def aggregate(self, *aggregates) -> dict:
        """
        Perform aggregate calculations on the query.

        :return: Dictionary with aggregate results.
        """
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().aggregate(*aggregates)

    async def a_aggregate(self, *aggregates) -> dict:
        """
        Asynchronously perform aggregate calculations on the query.

        :return: Dictionary with aggregate results.
        """
        return await QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().a_aggregate(*aggregates)

    def pagination(
            self, page: int = None, per_page: int = None
    ) -> tuple[int, list[dict]]:
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().pagination(page, per_page)

    async def a_pagination(
            self, page: int = None, per_page: int = None
    ) -> tuple[int, list[dict]]:
        return await QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().a_pagination(page, per_page)

    def with_columns(self, *columns: Union[ColumnElement, str]) -> QuerySet:
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().with_columns(*columns)

    def get(
            self,
            *where_clauses: Union[ColumnElement, str],
            to_dict: bool = False,
            raise_not_found: bool = False,
            **kw
    ) -> T:
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().get(
            *where_clauses, to_dict=to_dict, raise_not_found=raise_not_found, **kw
        )

    async def aget(
            self,
            *where_clauses: Union[ColumnElement, str],
            to_dict: bool = False,
            raise_not_found: bool = False,
            **kw
    ) -> T:
        return await QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().aget(
            *where_clauses, to_dict=to_dict, raise_not_found=raise_not_found, **kw
        )

    def get_by_id(
            self, _id: Union[int, str], to_dict: bool = False, raise_not_found: bool = False
    ) -> Optional[T]:
        return QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().get_by_id(
            _id, to_dict=to_dict, raise_not_found=raise_not_found
        )

    async def aget_by_id(
            self, _id: Union[int, str], to_dict: bool = False, raise_not_found: bool = False
    ) -> Optional[T]:
        return await QuerySet(model_cls=self.model_cls, filters=self._base_filter).filter().aget_by_id(
            _id, to_dict=to_dict, raise_not_found=raise_not_found
        )
