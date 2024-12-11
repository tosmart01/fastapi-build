#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright DataGrand Tech Inc. All Rights Reserved.
Author: Zoe
File: select.py
Time: 2024/12/2
"""
import asyncio
import time


from sqlalchemy import text

from core.context import g
from db.database import engine_sync
from models.base import Base
from tests.base import User, with_session


class TestCRUD:

    def setup_class(self):
        from db.database import session_maker_sync
        session = session_maker_sync()
        Base.metadata.create_all(bind=engine_sync)
        session.execute(text("truncate table user_test"))

    async def test_create_sync(self):
        user = User.objects.create(username="test", nickname="test", email="dsads@dsa.com")
        user_data = user.to_dict()
        assert user_data["username"] == "test"
        assert user_data["nickname"] == "test"

    async def test_create(self):
        user = await User.objects.a_create(username="test2", nickname="test2", email="dsads@dsa.com")
        user_data = user.to_dict()
        assert user_data["username"] == "test2"
        assert user_data["nickname"] == "test2"

    async def test_update_sync(self):
        user = User.objects.create(username=f"test_{time.time()}", nickname="test", email="dsads@dsa.com")
        User.objects.update_obj(user, properties={"nickname": "test4"})
        assert g.session_sync.query(User).filter(User.id == user.id).first().nickname == "test4"

    async def test_update(self):
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="test", email="dsads@dsa.com")
        await User.objects.a_update_obj(user, properties={"nickname": "test5"})
        new_user = await User.objects.aget_by_id(user.id)
        assert new_user.nickname == "test5"

    async def test_update_by_id_sync(self):
        user = User.objects.create(username=f"test_{time.time()}", nickname="test", email="dsads@dsa.com")
        User.objects.update_by_id(user.id, properties={User.nickname: "test_update_id"})
        assert g.session_sync.query(User).filter(User.id == user.id).first().nickname == "test_update_id"

    async def test_update_by_id(self):
        user = await User.objects.a_create(username=f"test_{time.time()}", nickname="test", email="dsads@dsa.com")
        await User.objects.a_update_by_id(user.id, properties={"nickname": "test_update_id"})
        new_user = await User.objects.aget_by_id(user.id)
        assert new_user.nickname == "test_update_id"

    async def test_update_by_ids_sync(self):
        u1 = User.objects.create(username=f"{time.time()}", nickname="test", email="")
        u2 = User.objects.create(username=f"{time.time()}", nickname="test", email="")
        u3 = User.objects.create(username=f"{time.time()}", nickname="test", email="")
        User.objects.update_by_ids([u1.id, u2.id, u3.id], properties={User.nickname: "bulk_update_test"})
        new_nicknames = User.objects.filter(User.id.in_([u1.id, u2.id, u3])).with_columns(User.nickname).values_list(
            flat=True)
        assert set(new_nicknames) == {"bulk_update_test"}

    async def test_update_by_ids(self):
        u1 = await User.objects.a_create(username=f"{time.time()}", nickname="test", email="")
        u2 = await User.objects.a_create(username=f"{time.time()}", nickname="test", email="")
        u3 = await User.objects.a_create(username=f"{time.time()}", nickname="test", email="")
        ids = [u1.id, u2.id, u3.id]
        await User.objects.a_update_by_ids(ids, properties={"nickname": "bulk_update_test"})
        new_nicknames = await User.objects.filter(User.id.in_([u1.id, u2.id, u3])).with_columns(
            User.nickname).avalues_list(
            flat=True)
        assert set(new_nicknames) == {"bulk_update_test"}

    async def test_delete_obj_sync(self):
        user = User.objects.create(username=f"{time.time()}", nickname="test", email="")
        user_id = user.id
        User.objects.delete_obj(user)
        assert User.objects.get_by_id(user_id) is None

    async def test_delete_obj(self):
        user = await User.objects.a_create(username=f"{time.time()}", nickname="test", email="")
        user_id = user.id
        await User.objects.a_delete_obj(user)
        new_user = await User.objects.aget_by_id(user_id)
        assert new_user is None

    async def test_delete_by_id(self):
        user = await User.objects.a_create(username=f"{time.time()}", nickname="test", email="")
        user_id = user.id
        await User.objects.a_delete_by_id(user_id)
        new_user = await User.objects.aget_by_id(user_id)
        assert new_user is None

    async def test_delete_by_id_sync(self):
        user = User.objects.create(username=f"{time.time()}", nickname="test", email="")
        user_id = user.id
        User.objects.delete_by_id(user_id)
        new_user = User.objects.get_by_id(user_id)
        assert new_user is None

    async def test_delete_by_ids(self):
        user1 = await User.objects.a_create(username=f"{time.time()}", nickname="test", email="")
        user2 = await User.objects.a_create(username=f"{time.time()}", nickname="test", email="")
        user1_id = user1.id
        user2_id = user2.id
        await User.objects.a_delete_by_ids([user1_id, user2_id])
        new_user = await User.objects.filter(User.id.in_([user1_id, user2_id])).avalues_list('nickname', flat=True)
        assert new_user == []

    async def test_delete_by_ids_sync(self):
        user1 = User.objects.create(username=f"{time.time()}", nickname="test", email="")
        user2 = User.objects.create(username=f"{time.time()}", nickname="test", email="")
        user1_id = user1.id
        user2_id = user2.id
        User.objects.delete_by_ids([user1_id, user2_id])
        new_user = User.objects.filter(User.id.in_([user1_id, user2_id])).values_list('nickname', flat=True)
        assert new_user == []

    async def test_soft_delete_obj(self):
        user = await User.objects.a_create(username=f"{time.time()}", nickname="test", email="")
        await User.objects.a_soft_delete_obj(user)
        new_user = await User.objects.filter(User.id == user.id, User.is_delete == 0).afirst()
        assert new_user is None

    async def test_soft_delete_obj_sync(self):
        user = User.objects.create(username=f"{time.time()}", nickname="test", email="")
        User.objects.soft_delete_obj(user)
        new_user = User.objects.filter(User.id == user.id, User.is_delete == 0).first()
        assert new_user is None

    async def test_soft_delete_by_id(self):
        user = await User.objects.a_create(username=f"{time.time()}", nickname="test", email="")
        await User.objects.a_soft_delete_by_id(user.id)
        new_user = await User.objects.aget(User.id == user.id, User.is_delete == 0)
        assert new_user is None

    async def test_soft_delete_by_id_sync(self):
        user = User.objects.create(username=f"{time.time()}", nickname="test", email="")
        User.objects.soft_delete_by_id(user.id)
        new_user = User.objects.get(User.id == user.id, User.is_delete == 0)
        assert new_user is None

    async def test_soft_delete_by_ids(self):
        u1 = await User.objects.a_create(username=f"{time.time()}", nickname="test", email="")
        u2 = await User.objects.a_create(username=f"{time.time()}", nickname="test", email="")
        await User.objects.a_soft_delete_by_ids([u1.id, u2.id])
        new_users = await User.objects.filter(User.id.in_([u1.id, u2.id]), User.is_delete == 0).avalues_list(flat=True)
        assert new_users == []

    async def test_soft_delete_by_ids_sync(self):
        u1 = User.objects.create(username=f"{time.time()}", nickname="test", email="")
        u2 = User.objects.create(username=f"{time.time()}", nickname="test", email="")
        User.objects.soft_delete_by_ids([u1.id, u2.id])
        new_users = User.objects.filter(User.id.in_([u1.id, u2.id]), User.is_delete == 0).values_list(flat=True)
        assert new_users == []

    async def run(self):
        self.setup_class()
        async with with_session():
            await self.test_create()
            await self.test_create_sync()
            await self.test_update()
            await self.test_update_sync()
            await self.test_update_by_id()
            await self.test_update_by_id_sync()
            await self.test_update_by_ids_sync()
            await self.test_update_by_ids()
            await self.test_delete_obj_sync()
            await self.test_delete_obj()
            await self.test_delete_by_id_sync()
            await self.test_delete_by_id()
            await self.test_delete_by_ids()
            await self.test_delete_by_ids_sync()
            await self.test_soft_delete_obj()
            await self.test_soft_delete_obj_sync()
            await self.test_soft_delete_by_id()
            await self.test_soft_delete_by_id_sync()
            await self.test_soft_delete_by_ids()
            await self.test_soft_delete_by_ids_sync()


if __name__ == '__main__':
    asyncio.run(TestCRUD().run())
