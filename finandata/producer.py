import importlib
import sys

from loguru import logger

# from finandata.backend.db import db, clients
from finandata.tasks.tasks import crawler


def Update(dataset: str, start_date: str, end_date: str):
    # 要爬蟲的平台使用的檔案 dataset，例如 taiwan_stock_price
    # 拿取每個爬蟲任務的參數列表dict(date,data_source)
    # 爬蟲資料的日期 date，例如 2021-04-10 的台股股價
    # 資料來源 data_source，例如 twse 證交所、tpex 櫃買中心
    parameter_list = getattr(
        importlib.import_module(f"finandata.crawler.{dataset}"),
        "gen_task_paramter_list",  # 匯入函數
    )(
        start_date=start_date, end_date=end_date
    )  # 傳入函數的參數

    # 用 for loop 發送任務
    for parameter in parameter_list:
        logger.info(f"{dataset}, {parameter}")
        task = crawler.s(dataset, parameter)
        # queue 參數，可以指定要發送到特定 queue 列隊中，例如 twse 證交所、tpex 櫃買中心
        task.apply_async(queue=parameter.get("data_source", ""))


if __name__ == "__main__":
    dataset, start_date, end_date = sys.argv[1:]
    Update(dataset, start_date, end_date)
