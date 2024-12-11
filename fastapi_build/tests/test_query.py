#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright DataGrand Tech Inc. All Rights Reserved.
Author: Zoe
File: test_query.py
Time: 2024/12/6
"""
import asyncio
import time

from sqlalchemy import func, select

from tests.base import User, BaseTest
from core.context import g


class TestQuery(BaseTest):

    async def test_first(self):
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="test")
        user2 = await User.objects.a_create(username=f"test_{time.time()}", nickname="test2")
        first_user = await User.objects.afirst()
        assert first_user.nickname == user.nickname

    async def test_first_sync(self):
        user = User.objects.create(username=f"test_{time.time()}", nickname="test")
        user2 = User.objects.create(username=f"test_{time.time()}", nickname="test2")
        first_user = User.objects.first()
        assert first_user.nickname == user.nickname

    async def test_last(self):
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="first")
        user2 = await User.objects.a_create(username=f"test_{time.time()}", nickname="last")
        last_user = await User.objects.alast(field=User.id)
        assert last_user.nickname == user2.nickname

    async def test_last_sync(self):
        user = User.objects.create(username=f"test_{time.time()}", nickname="first")
        user2 = User.objects.create(username=f"test_{time.time()}", nickname="last")
        last_user = User.objects.last(field=User.id)
        assert last_user.id == user2.id

    async def test_values(self):
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="values1")
        user2 = await User.objects.a_create(username=f"test_{time.time()}", nickname="values2")
        v = await User.objects.filter(User.nickname.like(f"%values%")).avalues('nickname')
        assert v == [{"nickname": "values1"}, {"nickname": "values2"}]

        v = await User.objects.filter(User.nickname.like(f"%values%")).avalues(User.nickname)
        assert v == [{"nickname": "values1"}, {"nickname": "values2"}]

        v = await User.objects.avalues('nickname')
        assert isinstance(v, list)

    async def test_values_sync(self):
        user = User.objects.create(username=f"test_{time.time()}", nickname="values_sync")
        user2 = User.objects.create(username=f"test_{time.time()}", nickname="values_sync")
        v = User.objects.filter(User.nickname.like(f"%values_sync%")).values('nickname')
        assert v == [{"nickname": "values_sync"}, {"nickname": "values_sync"}]

        v = User.objects.filter(User.nickname.like(f"%values_sync%")).values(User.nickname)
        assert v == [{"nickname": "values_sync"}, {"nickname": "values_sync"}]

        v = User.objects.values('nickname')
        assert isinstance(v, list)

    async def test_values_list(self):
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="values_list")
        user2 = await User.objects.a_create(username=f"test_{time.time()}", nickname="values_list")
        v = await User.objects.avalues_list(User.nickname)
        assert isinstance(v, list)
        assert isinstance(v[0], list)

        v = await User.objects.filter(User.nickname.like(f"%values_list")).avalues_list("nickname")
        assert v == [["values_list"], ["values_list"]]
        v = await User.objects.filter(User.nickname.like(f"%values_list")).avalues_list("nickname", flat=True)
        assert v == ["values_list", "values_list"]

    async def test_values_list_sync(self):
        user = User.objects.create(username=f"test_{time.time()}", nickname="values_list_sync")
        user2 = User.objects.create(username=f"test_{time.time()}", nickname="values_list_sync")
        v = User.objects.values_list(User.nickname)
        assert isinstance(v, list)
        assert isinstance(v[0], list)

        v = User.objects.filter(User.nickname.like(f"%values_list_sync")).values_list("nickname")
        assert v == [["values_list_sync"], ["values_list_sync"]]
        v = User.objects.filter(User.nickname.like(f"%values_list_sync")).values_list("nickname", flat=True)
        assert v == ["values_list_sync", "values_list_sync"]

    async def test_count(self):
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="count")
        user2 = await User.objects.a_create(username=f"test_{time.time()}", nickname="count")
        count = await User.objects.acount()
        db_count = await g.session.execute(select(func.count(User.id)))
        db_count = db_count.scalar()
        assert db_count == count

        count = await User.objects.filter(User.nickname.like(f"%count")).acount()
        assert 2 == count

    async def test_count_sync(self):
        user = User.objects.create(username=f"test_{time.time()}", nickname="count_sync")

        count = User.objects.count()
        db_count = g.session_sync.query(User).count()
        assert count == db_count
        count = User.objects.filter(User.nickname.like(f"%count_sync")).count()
        assert count == 1

    async def test_exists(self):
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="exists")
        exists = await User.objects.filter(User.nickname.like(f"%exists%")).aexists()
        assert exists == True
        exists = await User.objects.filter(User.nickname.like(f"%no_exists%")).aexists()
        assert exists == False
        exists = await User.objects.aexists()
        assert exists == True

    async def test_exists_sync(self):
        user = User.objects.create(username=f"test_{time.time()}", nickname="exists_sync")
        exists = User.objects.filter(User.nickname.like(f"%exists_sync%")).exists()
        assert exists == True
        exists = User.objects.filter(User.nickname.like(f"%no_exists%")).exists()
        assert exists == False
        exists = User.objects.exists()
        assert exists == True

    async def test_exclude(self):
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="exclude")
        count = await User.objects.exclude(User.nickname != "exclude").acount()
        assert count == 1
        count = await User.objects.exclude(User.nickname == "exclude").acount()
        assert count > 1

    async def test_order_by(self):
        user = User.objects.create(username=f"test_{time.time()}", nickname="order_by")
        user = User.objects.create(username=f"test_{time.time()}", nickname="order_by2")
        v = User.objects.filter(User.nickname.like(f"%order_by%")).order_by(User.id.desc()).values_list("nickname",
                                                                                                        flat=True)
        assert v == ["order_by2", "order_by"]

    async def test_limit(self):
        v = User.objects.limit(1).values_list()
        assert len(v) == 1

    async def test_offset(self):
        v = User.objects.order_by(User.id).offset(2).first()
        assert v.id == 3

    async def test_aggregate(self):
        v = User.objects.aggregate(func.count(User.id).label("count"))
        assert v['count'] == User.objects.count()

    async def test_pagination(self):
        total, data = await User.objects.a_pagination(page=1, per_page=3)
        count = await User.objects.acount()
        assert total == count and len(data) == 3, f"pagination error, total={total}, data={data}"

    async def test_pagination_sync(self):
        total, data = User.objects.pagination(page=1, per_page=3)
        count = User.objects.count()
        assert total == count and len(data) == 3, f"pagination error, total={total}, data={data}"

    async def test_update(self):
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="update")
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="update")
        update = await User.objects.filter(User.nickname.like(f"%update%")).aupdate({"nickname": "updated"})
        update_user = await User.objects.aget(User.nickname == "updated")
        assert update_user is not None

    async def test_update_sync(self):
        user = User.objects.create(username=f"test_{time.time()}", nickname="update_sync")
        update = User.objects.filter(User.nickname.like(f"%update_sync%")).update(
            {User.nickname: "update_sync_updated"})
        update_user = User.objects.get(User.nickname == "update_sync_updated")
        assert update_user is not None

    async def test_delete(self):
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="delete")
        delete = await User.objects.filter(User.nickname == "delete").adelete()
        delete_user = await User.objects.aget(User.nickname == "delete")
        assert delete_user is None

    async def test_delete_sync(self):
        user = User.objects.create(username=f"test_{time.time()}", nickname="delete")
        delete = User.objects.filter(User.nickname == "delete").delete()
        delete_user = User.objects.get(User.nickname == "delete")
        assert delete_user is None

    async def test_soft_delete_sync(self):
        user = User.objects.create(username=f"test_{time.time()}", nickname="soft_delete")
        delete = User.objects.filter(User.nickname == "soft_delete").soft_delete()
        delete_user = User.objects.get(User.nickname == "soft_delete")
        assert delete_user is None

    async def test_soft_delete(self):
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="soft_delete2")
        delete = await User.objects.filter(User.nickname == "soft_delete2").asoft_delete()
        delete_user = await User.objects.aget(User.nickname == "soft_delete2")
        assert delete_user is None


if __name__ == '__main__':
    asyncio.run(TestQuery().run())
