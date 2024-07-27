import os
from dotenv import load_dotenv

# 構建 .env 檔案的路徑
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")

# 載入 .env 檔案
load_dotenv(dotenv_path)

# 使用 os.environ.get 來取得環境變數
PSQL_DATA_HOST = os.environ.get("PSQL_DATA_HOST")
PSQL_DATA_USER = os.environ.get("PSQL_DATA_USER")
PSQL_DATA_PASSWORD = os.environ.get("PSQL_DATA_PASSWORD")
PSQL_DATA_PORT = int(os.environ.get("PSQL_DATA_PORT"))
PSQL_DATA_DATABASE = os.environ.get("PSQL_DATA_DATABASE")

WORKER_ACCOUNT = os.environ.get("WORKER_ACCOUNT")
WORKER_PASSWORD = os.environ.get("WORKER_PASSWORD")

MESSAGE_QUEUE_HOST = os.environ.get("MESSAGE_QUEUE_HOST")
MESSAGE_QUEUE_PORT = int(os.environ.get("MESSAGE_QUEUE_PORT"))

# 印出環境變數的值
if __name__ == "__main__":
    print("Variable value:", PSQL_DATA_PASSWORD)
