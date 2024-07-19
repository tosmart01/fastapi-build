# -- coding: utf-8 --
# @Time : 2024/5/27 11:39
# @Author : PinBar
# @File : sql_tools.py
from typing import Union

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query

from core.context import g

try:
    from sqlalchemy.engine import Row, Result
    from sqlalchemy.sql import Select
except:
    from sqlalchemy import Select, Result, Row

from db.backends.mysql import session, async_session_maker


class QueryConverter:
    """
    Utility class to convert SQLAlchemy query results to different formats.
    """

    def query_obj_to_dict(self, obj: Row):
        if self.check_model_instance(obj):
            return obj.to_dict()
        else:
            return obj._asdict()

    def query_to_value_list(self, query: Query) -> list[list]:
        """
        Convert SQLAlchemy Query object to a list of lists (each inner list represents a row of values).

        Args:
            query (Query): SQLAlchemy Query object.

        Returns:
            list[list]: List of lists where each inner list represents a row of values.

        Example:
            query = session.query(User.username, User.email).filter(User.is_active == True)
            print(query_to_value_list(query))
            [['John', '<EMAIL>']]
        """
        result = query.all()
        if not result:
            return []
        first = result[0]
        is_model_instance = self.check_model_instance(first)
        if is_model_instance:
            return [list(row.to_dict().values()) for row in result]
        else:
            return [list(v._asdict().values()) for v in result]

    def query_to_dict_list(self, query: Query) -> list[dict]:
        """
        Convert SQLAlchemy Query object to a list of dictionaries (each dictionary represents a row of data).

        Args:
            query (Query): SQLAlchemy Query object.

        Returns:
            list[dict]: List of dictionaries where each dictionary represents a row of data.

        Example:
            query = session.query(User.username, User.email).filter(User.is_active == True)
            print(query_to_dict_list(query))
            [{'username': 'John', 'email': '<EMAIL>'}]
        """
        result = query.all()
        if not result:
            return []
        first = result[0]
        is_model_instance = self.check_model_instance(first)
        if is_model_instance:
            return [row.to_dict() for row in result]
        else:
            return [v._asdict() for v in result]

    def check_model_instance(self, obj: Row) -> bool:
        """
        Check if an object is an instance of a SQLAlchemy model.

        Args:
            obj (Row): Object to check.

        Returns:
            bool: True if the object is an instance of a SQLAlchemy model, False otherwise.
        """
        return hasattr(obj, '__table__')

    async def async_execute(self, session: AsyncSession, query: select) -> Result:
        """
        Execute an asynchronous SQLAlchemy query.

        Args:
            session (AsyncSession): AsyncSession object to execute the query with.
            query (select): SQLAlchemy select query to execute.

        Returns:
            Result: Result object containing the query results.
        """
        if session:
            result = await session.execute(query)
        else:
            result = await g.session.execute(query)
        return result

    def convert_all(self, result: list[Row], to_dict: bool = False, value_list: bool = False):
        """
        Convert a list of SQLAlchemy Row objects to a desired format (list of dictionaries or list of lists).

        Args:
            result (list[Row]): List of SQLAlchemy Row objects.
            to_dict (bool, optional): Convert to dictionaries if True. Defaults to False.
            value_list (bool, optional): Convert to lists of values if True. Defaults to False.

        Returns:
            List of dictionaries, lists, or Row objects based on the conversion settings.

        Example:
            query = select(User.username, User.email).where(User.id.in_([1,2]))
            result = session.execute(query).all()
            print(convert_all(result, to_dict=True))
            [{'username': 'John', 'email': '<EMAIL>'}]
        """
        if not result:
            return result
        first_row = result[0]
        objects = []
        is_model_instance = self.check_model_instance(first_row[0])
        for row in result:
            row = row[0] if is_model_instance else row
            if to_dict:
                data = row._asdict() if not is_model_instance else row.to_dict()
                objects.append(data)
            elif value_list:
                data = list(row._asdict().values()) if not is_model_instance else list(row.to_dict().values())
                objects.append(data)
            else:
                objects.append(row)
        return objects

    def convert_one(self, row: Row, to_dict: bool = False):
        """
        Convert a single SQLAlchemy Row object to a desired format (dictionary or Row object).

        Args:
            row (Row): SQLAlchemy Row object.
            to_dict (bool, optional): Convert to dictionary if True. Defaults to False.

        Returns:
            Dictionary or Row object based on the conversion settings.

        Example:
            query = select(User.username, User.email).where(User.id.in_([1,2]))
            result = session.execute(query).first()
            print(convert_one(result, to_dict=True))
            {'username': 'John', 'email': '<EMAIL>'}
        """
        if not row:
            return row
        is_model_instance = self.check_model_instance(row[0])
        row = row if not is_model_instance else row[0]
        if to_dict:
            return row._asdict() if not is_model_instance else row.to_dict()
        return row

    def fetchall(self, query: Select, to_dict: bool = False, value_list: bool = False) -> Union[
        list[Row], list[dict], list[list]]:
        """
        Fetch all results of a SQLAlchemy Select query and convert them to the desired format.

        Args:
            query (Select): SQLAlchemy Select query.
            to_dict (bool, optional): Convert results to dictionaries if True. Defaults to False.
            value_list (bool, optional): Convert results to lists of values if True. Defaults to False.

        Returns:
            Union[list[Row], list[dict], list[list]]: List of rows in the desired format.

        Example:
            query = select(User.username, User.email).where(User.id.in_([1,2]))
            print(fetchall(query, to_dict=True))
            [{'username': 'John', 'email': '<EMAIL>'}]
        """
        result = session.execute(query)
        result = result.all()
        return self.convert_all(result, to_dict, value_list)

    async def a_fetchall(self, query: Select, to_dict: bool = False, value_list: bool = False,
                         _session: AsyncSession = None) -> Union[
        list[Row], list[dict], list[list]]:
        """
        Asynchronously fetch all results of a SQLAlchemy Select query and convert them to the desired format.

        Args:
            query (Select): SQLAlchemy Select query.
            to_dict (bool, optional): Convert results to dictionaries if True. Defaults to False.
            value_list (bool, optional): Convert results to lists of values if True. Defaults to False.
            _session (AsyncSession, optional): AsyncSession object to execute the query with. Defaults to None.

        Returns:
            Union[list[Row], list[dict], list[list]]: List of rows in the desired format.

        Example:
            query = select(User.username, User.email).where(User.id.in_([1,2]))
            result = await a_fetchall(query, to_dict=True)
            result
            [{'username': 'John', 'email': '<EMAIL>'}]
        """
        result = await self.async_execute(_session, query)
        result = result.all()
        return self.convert_all(result, to_dict, value_list)

    def fetchone(self, query: Select, to_dict: bool = False) -> Union[Row, dict]:
        """
        Fetch the first result of a SQLAlchemy Select query and convert it to the desired format.

        Args:
            query (Select): SQLAlchemy Select query.
            to_dict (bool, optional): Convert result to dictionary if True. Defaults to False.

        Returns:
            Union[Row, dict]: First row in the desired format.

        Example:
            query = select(User.username, User.email).where(User.id.in_([1,2]))
            result = fetchone(query, to_dict=True)
            result
            {'username': 'John', 'email': '<EMAIL>'}
        """
        result = session.execute(query)
        row = result.first()
        return self.convert_one(row, to_dict)

    async def a_fetchone(self, query: Select, to_dict: bool = False, _session: AsyncSession = None) -> Union[Row, dict]:
        """
        Asynchronously fetch the first result of a SQLAlchemy Select query and convert it to the desired format.

        Args:
            query (Select): SQLAlchemy Select query.
            to_dict (bool, optional): Convert result to dictionary if True. Defaults to False.
            _session (AsyncSession, optional): AsyncSession object to execute the query with. Defaults to None.

        Returns:
            Union[Row, dict]: First row in the desired format.

        Example:
            query = select(User.username, User.email).where(User.id.in_([1,2]))
            result = await a_fetchone(query, to_dict=True)
            result
            {'username': 'John', 'email': '<EMAIL>'}
        """
        result = await self.async_execute(_session, query)
        row = result.first()
        return self.convert_one(row, to_dict)

    def fetch_count(self, query: Select) -> int:
        """
        Fetch the count of results for a given SQLAlchemy Select query.

        Args:
            query (Select): SQLAlchemy Select query.

        Returns:
            int: Count of results.

        Example:
            query = select(User.username, User.email).where(User.id.in_([1,2]))
            result = fetch_count(query)
            result
            10
        """
        subquery = query.subquery()
        q = select(func.count(text('1'))).select_from(subquery)
        return session.execute(q).first()[0]

    async def a_fetch_count(self, query: Select, _session: AsyncSession = None) -> int:
        """
        Asynchronously fetch the count of results for a given SQLAlchemy Select query.

        Args:
            query (Select): SQLAlchemy Select query.
            _session (AsyncSession): AsyncSession object to execute the query with.

        Returns:
            int: Count of results.

        Example:
            query = select(User.username, User.email).where(User.id.in_([1,2]))
            result = await a_fetch_count(query)
            result
            10
        """
        subquery = query.subquery()
        q = select(func.count(text('1'))).select_from(subquery)
        result = await self.async_execute(_session, q)
        return result.first()[0]

    def pagination(self, query: Union[Select, Query], page: int = 1, per_page: int = 10) -> tuple[int, list[dict]]:
        """
        Perform pagination on a SQLAlchemy Select or Query object.

        Args:
            query (Union[Select, Query]): SQLAlchemy Select or Query object.
            page (int, optional): Page number. Defaults to 1.
            per_page (int, optional): Number of results per page. Defaults to 10.

        Returns:
            tuple[int, list[dict]]: Total count of results and list of results for the requested page.

        Example:
            query = select(User.username, User.email).where(User.id.in_([1,2]))
            total, result = pagination(query)
            total, result
            10, [{"username": "John", "email": "<EMAIL>"}, ...]

            query = session.query(User.username, User.email).where(User.id.in_([1, 2]))
            total, result = pagination(query)
            total, result
            10, [{"username": "John", "email": "<EMAIL>"}, ...]
        """
        offset = (page - 1) * per_page
        paginate = query.offset(offset).limit(per_page)
        if isinstance(query, Select):
            total = self.fetch_count(query)
            result = self.fetchall(paginate, to_dict=True)
        else:
            total = query.count()
            result = self.query_to_dict_list(query)
        return total, result

    async def a_pagination(self, query: Select, page: int = 1, per_page: int = 10, _session: AsyncSession = None) -> \
            tuple[int, list[dict]]:
        """
        Perform asynchronous pagination on a SQLAlchemy Select object.

        Args:
            query (Select): SQLAlchemy Select query.
            page (int, optional): Page number. Defaults to 1.
            per_page (int, optional): Number of results per page. Defaults to 10.
            _session (AsyncSession, optional): AsyncSession object to execute the query with. Defaults to None.

        Returns:
            tuple[int, list[dict]]: Total count of results and list of results for the requested page.

        Example:
            query = select(User.username, User.email).where(User.id.in_([1,2]))
            total, result = await a_pagination(query)
            total, result
            10, [{"username": "John", "email": "<EMAIL>"}, ...]

            query = session.query(User.username, User.email).where(User.id.in_([1, 2]))
            total, result = await a_pagination(query)
            total, result
            10, [{"username": "John", "email": "<EMAIL>"}, ...]

        """
        offset = (page - 1) * per_page
        total = await self.a_fetch_count(query, _session)
        paginate = query.offset(offset).limit(per_page)
        result = await self.a_fetchall(paginate, to_dict=True, _session=_session)
        return total, result


database = QueryConverter()
