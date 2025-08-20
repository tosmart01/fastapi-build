#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright DataGrand Tech Inc. All Rights Reserved.
Author: Zoe
File: __init__.py.py
Time: 2024/12/6
"""
import asyncio

from db.database import load_session
from core.context import g

load_session()
from models.user import User

async def main():
    await User.objects.a_update_by_id(1, properties={"nickname": "xxx"})


if __name__ == '__main__':
    asyncio.run(main())