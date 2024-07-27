import pandas as pd
from requests.models import Response


from finandata.crawler.taiwan_stock_price import (
    clear_data,
    colname_zh2en,
    convert_change,
    convert_date,
    set_column,
    twse_header,
    tpex_header,
    crawler_twse,
    crawler_tpex,
    is_weekend,
    gen_task_paramter_list,
    crawler,
)

from finandata.schema.dataset import check_schema


def test_is_weekend_false():
    """
    測試, 非周末, 輸入周一0, 回傳False
    """
    result = is_weekend(day=0)
    expected = False
    assert result == expected


def test_is_weekend_true():
    """
    測試, 是周末, 輸入周日6, 回傳True
    """
    result = is_weekend(day=6)
    expected = True
    assert result == expected


def test_gen_task_paramter_list():
    """
    測試, 建立task參數列表, 2021-01-01 ~ 2021-01-05
    producer.py發送參數給rabbitmq, 給每個worker單獨執行爬蟲
    """
    result = gen_task_paramter_list(start_date="2021-01-01", end_date="2021-01-05")
    expected = [
        {"date": "2021-01-01", "data_source": "twse"},
        {"date": "2021-01-01", "data_source": "tpex"},
        {"date": "2021-01-04", "data_source": "twse"},
        {"date": "2021-01-04", "data_source": "tpex"},
        {"date": "2021-01-05", "data_source": "twse"},
        {"date": "2021-01-05", "data_source": "tpex"},
    ]
    assert result == expected


def test_convert_date():
    """
    測試, task參數列表2021-01-01 ~ 2021-01-05
    tpex需把輸入的日期格式YYYY-MM-DD轉成民國年/月/日, 以符合Request url
    """
    date = "2021-07-01"
    result = convert_date(date)
    expected = "110/07/01"
    assert result == expected


def test_twse_header():
    result = twse_header()
    expected = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Host": "www.twse.com.tw",
        "Referer": "https://www.twse.com.tw/zh/trading/historical/mi-index.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    assert result == expected


def test_tpex_header():
    result = tpex_header()
    expected = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Host": "www.tpex.org.tw",
        "Referer": "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    assert result == expected


def test_colname_zh2en():
    """
    資料格式https://www.twse.com.tw/zh/trading/historical/mi-index.html
    測試, twse中英轉換
    只取部分欄位：證券代號、成交股數、成交筆數、成交金額、開盤價、最高價、最低價、收盤價、漲跌(+/-)、漲跌價差
    """
    result_df = pd.DataFrame(
        [
            {
                0: "0050",
                1: "元大台灣50",
                2: "4,962,514",
                3: "6,179",
                4: "616,480,760",
                5: "124.20",
                6: "124.65",
                7: "123.75",
                8: "124.60",
                9: "<p style= color:red>+</p>",
                10: "0.25",
                11: "124.55",
                12: "123",
                13: "124.60",
                14: "29",
                15: "0.00",
            },
            {
                0: "0051",
                1: "元大中型100",
                2: "175,269",
                3: "44",
                4: "7,827,387",
                5: "44.60",
                6: "44.74",
                7: "44.39",
                8: "44.64",
                9: "<p style= color:red>+</p>",
                10: "0.04",
                11: "44.64",
                12: "20",
                13: "44.74",
                14: "2",
                15: "0.00",
            },
        ]
    )
    colname = [
        "證券代號",
        "證券名稱",
        "成交股數",
        "成交筆數",
        "成交金額",
        "開盤價",
        "最高價",
        "最低價",
        "收盤價",
        "漲跌(+/-)",
        "漲跌價差",
        "最後揭示買價",
        "最後揭示買量",
        "最後揭示賣價",
        "最後揭示賣量",
        "本益比",
    ]
    result_df = colname_zh2en(result_df.copy(), colname)
    expected_df = pd.DataFrame(
        [
            {
                "StockID": "0050",
                "TradeVolume": "4,962,514",
                "Transaction": "6,179",
                "TradeValue": "616,480,760",
                "Open": "124.20",
                "Max": "124.65",
                "Min": "123.75",
                "Close": "124.60",
                "Dir": "<p style= color:red>+</p>",
                "Change": "0.25",
            },
            {
                "StockID": "0051",
                "TradeVolume": "175,269",
                "Transaction": "44",
                "TradeValue": "7,827,387",
                "Open": "44.60",
                "Max": "44.74",
                "Min": "44.39",
                "Close": "44.64",
                "Dir": "<p style= color:red>+</p>",
                "Change": "0.04",
            },
        ]
    )
    assert pd.testing.assert_frame_equal(result_df, expected_df) is None


def test_set_column():
    """
    資料格式https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw
    測試, tpex爬蟲後只保留需要的欄位0, 2, 3, 4, 5, 6, 7, 8, 9
    根據上述位置設置對應的欄位名稱
    """
    df = pd.DataFrame(
        [
            {
                0: "00679B",
                2: "44.91",
                3: "-0.08",
                4: "45.00",
                5: "45.00",
                6: "44.85",
                7: "270,000",
                8: "12,127,770",
                9: "147",
            },
            {
                0: "00687B",
                2: "47.03",
                3: "-0.09",
                4: "47.13",
                5: "47.13",
                6: "47.00",
                7: "429,000",
                8: "20,181,570",
                9: "39",
            },
            {
                0: "00694B",
                2: "37.77",
                3: "-0.07",
                4: "37.84",
                5: "37.84",
                6: "37.72",
                7: "343,000",
                8: "12,943,630",
                9: "35",
            },
        ]
    )
    result_df = set_column(df)
    expected_df = pd.DataFrame(
        [
            {
                "StockID": "00679B",
                "Close": "44.91",
                "Change": "-0.08",
                "Open": "45.00",
                "Max": "45.00",
                "Min": "44.85",
                "TradeVolume": "270,000",
                "TradeValue": "12,127,770",
                "Transaction": "147",
            },
            {
                "StockID": "00687B",
                "Close": "47.03",
                "Change": "-0.09",
                "Open": "47.13",
                "Max": "47.13",
                "Min": "47.00",
                "TradeVolume": "429,000",
                "TradeValue": "20,181,570",
                "Transaction": "39",
            },
            {
                "StockID": "00694B",
                "Close": "37.77",
                "Change": "-0.07",
                "Open": "37.84",
                "Max": "37.84",
                "Min": "37.72",
                "TradeVolume": "343,000",
                "TradeValue": "12,943,630",
                "Transaction": "35",
            },
        ]
    )

    assert pd.testing.assert_frame_equal(result_df, expected_df) is None


def test_convert_change():
    """
    中英轉換後新增了欄位 Date
    測試, twse轉換欄位change
    將欄位change和dir合併後刪除dir, 欄位change的空格與X+符號轉換為空值，資料型態轉換為浮點數
    """
    df = pd.DataFrame(
        [
            {
                "StockID": "0050",
                "TradeVolume": "4,680,733",
                "Transaction": "5,327",
                "TradeValue": "649,025,587",
                "Open": "139.00",
                "Max": "139.20",
                "Min": "138.05",
                "Close": "138.30",
                "Dir": "<p style= color:green> -</p>",
                "Change": "0.6 5",
                "Date": "2021-07-01",
            },
            {
                "StockID": "0051",
                "TradeVolume": "175,374",
                "Transaction": "120",
                "TradeValue": "10,152,802",
                "Open": "58.20",
                "Max": "59.10",
                "Min": "57.40",
                "Close": "57.90",
                "Dir": "<p style= color:green>X</p>",
                "Change": "0.30",
                "Date": "2021-07-01",
            },
            {
                "StockID": "0052",
                "TradeVolume": "514,042",
                "Transaction": "270",
                "TradeValue": "64,127,738",
                "Open": "125.00",
                "Max": "125.20",
                "Min": "124.35",
                "Close": "124.35",
                "Dir": "<p style= color:green>+</p>",
                "Change": "0.65",
                "Date": "2021-07-01",
            },
        ]
    )
    result_df = convert_change(df)
    expected_df = pd.DataFrame(
        [
            {
                "StockID": "0050",
                "TradeVolume": "4,680,733",
                "Transaction": "5,327",
                "TradeValue": "649,025,587",
                "Open": "139.00",
                "Max": "139.20",
                "Min": "138.05",
                "Close": "138.30",
                "Change": -0.65,
                "Date": "2021-07-01",
            },
            {
                "StockID": "0051",
                "TradeVolume": "175,374",
                "Transaction": "120",
                "TradeValue": "10,152,802",
                "Open": "58.20",
                "Max": "59.10",
                "Min": "57.40",
                "Close": "57.90",
                "Change": 0.3,
                "Date": "2021-07-01",
            },
            {
                "StockID": "0052",
                "TradeVolume": "514,042",
                "Transaction": "270",
                "TradeValue": "64,127,738",
                "Open": "125.00",
                "Max": "125.20",
                "Min": "124.35",
                "Close": "124.35",
                "Change": 0.65,
                "Date": "2021-07-01",
            },
        ]
    )
    assert pd.testing.assert_frame_equal(result_df, expected_df) is None


def test_clear_data():
    """
    測試, 資料清理, 將文字與特殊符號轉成0
    例如, 將原先的會計數字, 如 1,536,598,轉換為一般數字1536598
    """
    df = pd.DataFrame(
        [
            {
                "StockID": "0050",
                "TradeVolume": "4,962,514",
                "Transaction": "6,179",
                "TradeValue": "616,480,760",
                "Open": "+124.20",
                "Max": "124.65",
                "Min": "123.75",
                "Close": "124.60",
                "Change": 0.25,
                "Date": "2021-01-05",
            },
            {
                "StockID": "0051",
                "TradeVolume": "175,269",
                "Transaction": "除息",
                "TradeValue": "7,827,387",
                "Open": "44.60",
                "Max": "X44.74",
                "Min": "44.39",
                "Close": "44.64",
                "Change": 0.04,
                "Date": "2021-01-05",
            },
            {
                "StockID": "0052",
                "TradeVolume": "1,536,598",
                "Transaction": "--",
                "TradeValue": "172,232,526",
                "Open": "112.10",
                "Max": "112.90",
                "Min": "111.15",
                "Close": "111.90",
                "Change": -0.2,
                "Date": "2021-01-05",
            },
        ]
    )
    result_df = clear_data(df.copy())
    expected_df = pd.DataFrame(
        [
            {
                "StockID": "0050",
                "TradeVolume": "4962514",
                "Transaction": "6179",
                "TradeValue": "616480760",
                "Open": "124.20",
                "Max": "124.65",
                "Min": "123.75",
                "Close": "124.60",
                "Change": "0.25",
                "Date": "2021-01-05",
            },
            {
                "StockID": "0051",
                "TradeVolume": "175269",
                "Transaction": "0",
                "TradeValue": "7827387",
                "Open": "44.60",
                "Max": "44.74",
                "Min": "44.39",
                "Close": "44.64",
                "Change": "0.04",
                "Date": "2021-01-05",
            },
            {
                "StockID": "0052",
                "TradeVolume": "1536598",
                "Transaction": "0",
                "TradeValue": "172232526",
                "Open": "112.10",
                "Max": "112.90",
                "Min": "111.15",
                "Close": "111.90",
                "Change": "-0.2",
                "Date": "2021-01-05",
            },
        ]
    )
    assert pd.testing.assert_frame_equal(result_df, expected_df) is None


def test_crawler_twse_success():
    """
    證交所https://www.twse.com.tw/zh/trading/historical/mi-index.html
    測試, twse爬蟲成功時的狀況
    查看檢查response
    colname, 在階層["tables"][8]["fields"]
    df, 在階層["tables"][8]["data"]
    清理步驟：
    爬蟲取得資料, 欄位中英轉換, 新增日期欄位, 漲跌幅處理, 資料清理文字轉數字
    """
    result_df = crawler_twse(date="2021-01-05")
    assert len(result_df) == 20596  # 檢查, 資料量是否正確
    assert list(result_df.columns) == [
        "StockID",
        "TradeVolume",
        "Transaction",
        "TradeValue",
        "Open",
        "Max",
        "Min",
        "Close",
        "Change",
        "Date",
    ]  # 檢查, 資料欄位是否正確


def test_crawler_twse_no_data():
    """
    測試沒 data 的時間點, 爬蟲是否正常
    """
    result_df = crawler_twse(date="2021-01-02")
    assert len(result_df) == 0  # 檢查，沒 data 資料量為0
    assert isinstance(
        result_df, pd.DataFrame
    )  # 檢查，沒 data 一樣要回傳 pd.DataFrame 型態


def test_crawler_twse_error(mocker):
    """
    測試, 在有資料的日期, 但某些時間點因為網站維護而無資料
    在測試階段, 無法保證對方一定會給錯誤的結果
    因此使用 mocker, 對 requests 做"替換", 換成我們設定的結果
    """
    # 模擬一個 HTTP response 對象
    mock_response = mocker.Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value == {}

    # 將特定路徑下的 requests 替換掉
    mock_requests = mocker.patch("finandata.crawler.taiwan_stock_price.requests")

    # 將 requests.get 的回傳值 response 替換掉成空的json
    mock_requests.get.return_value = mock_response

    result_df = crawler_twse(date="2021-01-05")
    assert len(result_df) == 0  # 沒 data, 回傳 0
    # 沒 data, 一樣要回傳 pd.DataFrame 型態
    assert isinstance(result_df, pd.DataFrame)


def test_crawler_tpex_success():
    """
    櫃買中心https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw
    測試, tpex爬蟲成功時的狀況
    查看檢查response
    df, 在階層["aaData"]
    清理步驟：
    爬蟲取得資料, 新增日期欄位, 設定欄位名稱, 資料清理文字轉數字
    """
    result_df = crawler_tpex(date="2021-01-05")
    assert len(result_df) == 6609  # 檢查, 資料量是否正確
    assert list(result_df.columns) == [
        "StockID",
        "Close",
        "Change",
        "Open",
        "Max",
        "Min",
        "TradeVolume",
        "TradeValue",
        "Transaction",
        "Date",
    ]  # 檢查, 資料欄位是否正確


def test_crawler_tpex_no_data():
    """
    測試沒 data 的時間點, 爬蟲是否正常
    """
    result_df = crawler_tpex(date="2021-01-02")
    assert len(result_df) == 0  # 沒 data, 回傳 0
    # 沒 data, 一樣要回傳 pd.DataFrame 型態
    assert isinstance(result_df, pd.DataFrame)


def test_crawler_twse():
    """
    測試證交所爬蟲, end to end test
    """
    result_df = crawler(
        parameter={
            "date": "2021-01-05",
            "data_source": "twse",
        }
    )
    result_df = check_schema(result_df, "TaiwanStockPrice")
    assert len(result_df) > 0


def test_crawler_tpex():
    """
    測試櫃買中心爬蟲, end to end test
    """
    result_df = crawler(
        parameter={
            "date": "2021-01-05",
            "data_source": "tpex",
        }
    )
    result_df = check_schema(result_df, "TaiwanStockPrice")
    assert len(result_df) > 0
