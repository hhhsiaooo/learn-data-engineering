import datetime
import time
import typing
import sys

import pandas as pd
import requests
from loguru import logger

from finandata.schema.dataset import check_schema


def clear_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """資料清理，將文字轉成數字"""
    for col in [
        "TradeVolume",
        "Transaction",
        "TradeValue",
        "Open",
        "Max",
        "Min",
        "Close",
        "Change",
    ]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "")
            .str.replace("X", "")
            .str.replace("+", "")
            .str.replace("----", "0")
            .str.replace("---", "0")
            .str.replace("--", "0")
            .str.replace("除權息", "0")
            .str.replace("除息", "0")
            .str.replace("除權", "0")
        )
    return df


def colname_zh2en(df: pd.DataFrame, colname: typing.List[str]) -> pd.DataFrame:
    """twse中文欄位轉成英文欄位"""
    taiwan_stock_price = {
        "證券代號": "StockID",
        "證券名稱": "",
        "成交股數": "TradeVolume",
        "成交筆數": "Transaction",
        "成交金額": "TradeValue",
        "開盤價": "Open",
        "最高價": "Max",
        "最低價": "Min",
        "收盤價": "Close",
        "漲跌(+/-)": "Dir",
        "漲跌價差": "Change",
        "最後揭示買價": "",
        "最後揭示買量": "",
        "最後揭示賣價": "",
        "最後揭示賣量": "",
        "本益比": "",
    }
    df.columns = [taiwan_stock_price[col] for col in colname]
    df = df.drop([""], axis=1)
    return df


def convert_change(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    twse合併漲跌欄位為Change
    將Change的空格和符號X替換為空值並轉換為浮點數
    刪除欄位Dir
    """
    logger.info("convert_change")
    df["Dir"] = df["Dir"].str.split(">").str[1].str.split("<").str[0]
    df["Change"] = df["Dir"] + df["Change"]
    df["Change"] = (
        df["Change"]
        .str.replace(" ", "")
        .str.replace("+", "")
        .str.replace("X", "")
        .astype(float)
    )
    df = df.fillna("")
    df = df.drop(["Dir"], axis=1)
    return df


def convert_date(date: str) -> str:
    """tpex把輸入的日期格式YYYY-MM-DD轉成民國年/月/日，以符合Request url"""
    logger.info("convert_date")
    year, month, day = date.split("-")
    year = int(year) - 1911
    return f"{year}/{month}/{day}"


def set_column(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """tpex設定資料欄位名稱"""
    df.columns = [
        "StockID",
        "Close",
        "Change",
        "Open",
        "Max",
        "Min",
        "TradeVolume",
        "TradeValue",
        "Transaction",
    ]
    return df


def twse_header():
    """網頁瀏覽時, 所帶的 request header 參數, 模仿瀏覽器發送 request"""
    return {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Host": "www.twse.com.tw",
        "Referer": "https://www.twse.com.tw/zh/trading/historical/mi-index.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }


def tpex_header():
    """網頁瀏覽時, 所帶的 request header 參數, 模仿瀏覽器發送 request"""
    return {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Host": "www.tpex.org.tw",
        "Referer": "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }


def crawler_twse(
    date: str,
) -> pd.DataFrame:
    """
    證交所網址https://www.twse.com.tw/zh/trading/historical/mi-index.html
    """
    logger.info("crawler_twse")
    url = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={date}&type=ALL&response=json"
    url = url.format(date=date.replace("-", ""))
    time.sleep(5)
    res = requests.get(url, headers=twse_header())
    if (res.json().get("stat") == "很抱歉，沒有符合條件的資料!") or (res.json() == {}):
        return pd.DataFrame()
    try:
        if "tables" in res.json():
            colname = res.json()["tables"][8]["fields"]
            df = pd.DataFrame(res.json()["tables"][8]["data"])
            # 欄位中英轉換
            df = colname_zh2en(df.copy(), colname)
            df["Date"] = date
            # 漲跌幅處理
            df = convert_change(df.copy())
            # 資料清理，將文字轉成數字
            df = clear_data(df.copy())
            return df
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()


def crawler_tpex(
    date: str,
) -> pd.DataFrame:
    """
    櫃買中心網址https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw
    """
    logger.info("crawler_tpex")
    url = "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&d={date}&se=AL"
    url = url.format(date=convert_date(date))
    time.sleep(5)
    res = requests.get(url, headers=tpex_header())
    data = res.json().get("aaData", "")
    df = pd.DataFrame(data)
    if not data or len(df) == 0:
        return pd.DataFrame()
    df = df[[0, 2, 3, 4, 5, 6, 7, 8, 9]]
    # 欄位中英轉換
    df = set_column(df.copy())
    df["Date"] = date
    # 資料清理，將文字轉成數字
    df = clear_data(df.copy())
    return df


def is_weekend(day: int) -> bool:
    return day in [5, 6]


def gen_task_paramter_list(start_date: str, end_date: str) -> typing.List[str]:
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    days = (end_date - start_date).days + 1
    date_list = [start_date + datetime.timedelta(days=day) for day in range(days)]
    date_list = [
        dict(
            date=str(d),
            data_source=data_source,
        )
        for d in date_list
        for data_source in [
            "twse",
            "tpex",
        ]
        if not is_weekend(d.weekday())
    ]
    return date_list


def crawler(
    parameter: typing.Dict[
        str,
        typing.List[typing.Union[str, int, float]],
    ]
) -> pd.DataFrame:
    logger.info(parameter)
    date = parameter.get("date", "")
    data_source = parameter.get("data_source", "")
    if data_source == "twse":
        df = crawler_twse(date)
    elif data_source == "tpex":
        df = crawler_tpex(date)
    df = check_schema(
        df.copy(),
        dataset="TaiwanStockPrice",
    )
    return df


# if __name__ == "__main__":
#     # start_date, end_date = sys.argv[1:]
#     # result = crawler_twse(start_date, end_date)
#     date = sys.argv[1]
#     result = crawler_tpex(date)
#     result = check_schema(
#         result.copy(),
#         dataset="TaiwanStockPrice",
#     )
#     print(result)
