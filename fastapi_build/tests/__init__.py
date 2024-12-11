#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright DataGrand Tech Inc. All Rights Reserved.
Author: Zoe
File: __init__.py.py
Time: 2024/12/6
"""
import asyncio

from db.database import session_maker_sync, session_maker
from core.context import g

session = session_maker_sync()
g.session_sync = session
g.session = session_maker()
from models.user import User

async def main():
    await User.objects.a_update_by_id(1, properties={"nickname": "xxx"})


if __name__ == '__main__':
    asyncio.run(main())