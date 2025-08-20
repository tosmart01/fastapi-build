from typing import Tuple
from urllib.parse import quote_plus

from config.settings import DATABASE_HOST, DATABASE_CHARSET, DATABASE_NAME, DATABASE_PASSWORD, DATABASE_PORT, \
    DATABASE_USER, DATABASE_SCHEMA, DATABASE_TYPE


def build_db_urls(
        db_type: str = DATABASE_TYPE,
        name: str = DATABASE_NAME,
        user: str = DATABASE_USER,
        password: str = DATABASE_PASSWORD,
        host: str = DATABASE_HOST,
        port: str = DATABASE_PORT,
        charset: str = DATABASE_CHARSET,
        schema: str = DATABASE_SCHEMA,
) -> Tuple[str, str]:
    # 驱动映射 + 默认端口
    drivers = {
        "sqlite": {
            "sync": "sqlite",
            "async": "sqlite+aiosqlite",
            "default_port": None
        },
        "postgres": {
            "sync": "postgresql+psycopg2",
            "async": "postgresql+asyncpg",
            "default_port": 5432
        },
        "mysql": {
            "sync": "mysql+pymysql",
            "async": "mysql+aiomysql",
            "default_port": 3306
        },
        "mariadb": {
            "sync": "mariadb+pymysql",
            "async": "mariadb+aiomysql",
            "default_port": 3306
        }
    }

    db_type_lower = db_type.lower()
    if db_type_lower not in drivers:
        raise ValueError(f"不支持的数据库类型: {db_type}")

    sync_engine = drivers[db_type_lower]["sync"]
    async_engine = drivers[db_type_lower]["async"]
    if not port and drivers[db_type_lower]["default_port"]:
        port = drivers[db_type_lower]["default_port"]

    # SQLite
    if db_type_lower == "sqlite":
        db_url = f"{sync_engine}:///{name}"
        async_db_url = f"{async_engine}:///{name}"
        return db_url, async_db_url

    # MySQL / MariaDB
    if db_type_lower in ("mysql", "mariadb"):
        db_url = (
            f"{sync_engine}://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{name}"
            f"?charset={charset}"
        )
        async_db_url = (
            f"{async_engine}://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{name}"
            f"?charset={charset}"
        )
        return db_url, async_db_url

    # PostgreSQL
    if db_type_lower == "postgres":
        params = []
        if charset:
            params.append(f"client_encoding={charset}")
        if schema:
            # options 参数用于指定 search_path
            params.append(f"options=-csearch_path={schema}")
        param_str = f"?{'&'.join(params)}" if params else ""

        db_url = (
            f"{sync_engine}://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{name}{param_str}"
        )
        async_db_url = (
            f"{async_engine}://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{name}{param_str}"
        )
        return db_url, async_db_url

    # 兜底（不推荐）
    db_url = f"{sync_engine}://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{name}"
    async_db_url = f"{async_engine}://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{name}"
    return db_url, async_db_url
