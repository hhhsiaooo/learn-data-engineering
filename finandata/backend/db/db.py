import psycopg2
import typing
import pandas as pd
from loguru import logger
from sqlalchemy import create_engine, engine
from sqlalchemy import text


def update2postgresql_by_pandas(
    df: pd.DataFrame,
    table: str,
    postgresql_conn: engine.base.Connection,
):
    if len(df) > 0:
        try:
            df.to_sql(
                name=table,
                con=postgresql_conn,
                if_exists="append",
                index=False,
                chunksize=1000,
            )
        except Exception as e:
            logger.info(e)
            return False
    return True


def build_update_sql(
    colname: typing.List[str],
    value: typing.List[str],
):
    update_sql = ",".join(
        [
            " {} = EXCLUDED.{} ".format(
                colname[i],
                colname[i],
            )
            for i in range(len(colname))
            if str(value[i])
        ]
    )
    return update_sql


def build_df_update_sql(table: str, df: pd.DataFrame) -> typing.List[str]:
    logger.info("build_df_update_sql")
    df_columns = list(df.columns)
    sql_list = []
    for i in range(len(df)):
        temp = list(df.iloc[i])
        value = [
            psycopg2.extensions.QuotedString(str(v)).getquoted().decode() for v in temp
        ]
        sub_df_columns = [df_columns[j] for j in range(len(temp))]
        update_sql = build_update_sql(sub_df_columns, value)
        sql_query = "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT (date) DO UPDATE SET {}".format(
            table,
            ",".join(sub_df_columns),
            ",".join(value),
            update_sql,
        )
        sql_list.append(sql_query)
    return sql_list


def update2postgresql_by_sql(
    df: pd.DataFrame,
    table: str,
    postgresql_conn: engine.base.Connection,
):
    sql_query = build_df_update_sql(table, df)
    commit(sql=sql_query, postgresql_conn=postgresql_conn)


def commit(
    sql: typing.Union[str, typing.List[str]],
    postgresql_conn: engine.base.Connection = None,
):
    logger.info("commit")
    try:
        if isinstance(sql, list):
            for s in sql:
                try:
                    postgresql_conn.execute(text(s))

                except Exception as e:
                    logger.info(e)
                    logger.info(s)
                    break

        elif isinstance(sql, str):
            postgresql_conn.execute(text(sql))

        postgresql_conn.commit()
    except Exception as e:
        logger.info(e)


def upload_data(
    df: pd.DataFrame,
    table: str,
    postgresql_conn: engine.base.Connection,
):
    if len(df) > 0:
        # 直接上傳
        if update2postgresql_by_pandas(
            df=df,
            table=table,
            postgresql_conn=postgresql_conn,
        ):
            pass
        else:
            # 如果有重複的資料
            # 使用 SQL 語法上傳資料
            update2postgresql_by_sql(
                df=df,
                table=table,
                postgresql_conn=postgresql_conn,
            )


# if __name__ == "__main__":
#     conn = get_postgresql_conn()

#     data = {
#         "name": ["Alice", "Bob", "Charlie"],
#         "gender": ["f", "m", "f"],
#         "age": [10000, 20000, 30000],
#     }
#     df = pd.DataFrame(data)
#     upload_data(df, "person", conn)
