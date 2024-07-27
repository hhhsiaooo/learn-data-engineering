from finandata.config import (
    PSQL_DATA_USER,
    PSQL_DATA_PASSWORD,
    PSQL_DATA_HOST,
    PSQL_DATA_PORT,
    PSQL_DATA_DATABASE,
)

from sqlalchemy import create_engine, engine


def get_postgresql_conn() -> engine.base.Connection:
    address = (
        f"postgresql://{PSQL_DATA_USER}:{PSQL_DATA_PASSWORD}"
        f"@{PSQL_DATA_HOST}:{PSQL_DATA_PORT}/{PSQL_DATA_DATABASE}"
    )
    engine = create_engine(address)
    connect = engine.connect()
    return connect


if __name__ == "__main__":
    conn = get_postgresql_conn()
    if isinstance(conn, engine.base.Connection):
        print("get_postgresql_conn 返回了 SQLAlchemy 的 Connection 物件")
    else:
        print("get_postgresql_conn 返回不是 SQLAlchemy 的 Connection 物件")
