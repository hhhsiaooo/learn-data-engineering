import importlib
import typing

# from sqlalchemy import create_engine, engine
from finandata.backend.db import db, clients
from finandata.tasks.worker import app


# 註冊 task, 有註冊的 task 才可以變成任務發送給 rabbitmq
@app.task()
def crawler(dataset: str, parameter: typing.Dict[str, str]):
    # 根據不同 dataset(taiwan_stock_price或taiwan_futures_daily), 使用相對應的 crawler 收集資料
    # 使用 getattr, importlib, 動態導入finandata.crawler 下對應的模組
    # 調用其中的 crawler 函數，獲取爬取的數據後，賦值給 df 變數
    df = getattr(
        importlib.import_module(f"finandata.crawler.{dataset}"),
        "crawler",
    )(parameter=parameter)
    # 根據不同 dataset，上傳到對應的資料表
    db_dataset = dict(
        taiwan_stock_price="taiwanstockprice",
        taiwan_futures_daily="taiwanfuturesdaily",
    )
    # upload_data(df, table, conn)
    conn = clients.get_postgresql_conn()
    db.upload_data(df, db_dataset.get(dataset), conn)
