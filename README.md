### 資料工程

#### 一、開發環境-wsl
* OS：Windows 11 / WSL(Windows Subsystem for Linux) / Ubuntu 22.04
  * linux目錄/usr："Unix System Resources"，包含 Unix/Linux 系統的資源，主要是用來存放不常更改的系統軟體和資源
  * linux目錄/mnt："mount"，用來暫時掛載其他文件系統或裝置的地方，方便使用者臨時存取這些文件系統或裝置
* IDE：VS Code，可切換 terminal (Windows/Ubuntu)
  
#### 容器管理工具-Docker
* Docker 簡介
  * 開源軟體平台，用於建立、測試和部署應用程式
  * 開發環境與生產環境不同：不同開發人員的本地端可能使用不同作業系統，雲端常用的Linux也有不同版本，Docker獨立環境可確保開發與生產的穩定性
  * 開發版本更動：爬蟲跟API會不斷更動版本，Docker+CI/CD可一鍵換版
  * 拓展性高：爬蟲、API、資料庫可能採用分散式架構，使用Loading Balance做分流，需要高拓展性的基底架構
  * 多服務的大型架構：高可用性的Web採用前後端分離，需要整合許多服務，如爬蟲、DB、API、Airflow、Backend、Log、視覺化分析
  * Docker服務容器化、微服務化，可走向K8s現代架構
  * Image：暫
  * Container：暫
  * Volume：暫
  
* Docker 操作
  * 安裝
    ```
    sudo apt-get update
    sudo apt-get install -y docker.io
    ```
  * 加入使用者
    ```
    sudo usermod -aG docker hailey
    ```
  * 查看容器
    ```
    docker ps
    ```
  * 安裝 Docker-Compose
    ```
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ```
  * 啟用 Docker 以開機自動啟動 
    ```
    sudo systemctl enable docker
    ```
  * Docker 網路設定
    * 列出所有網路
    ```
    docker network ls
    ```
    * Docker安裝時會自動創建網路
    ```
    # NETWORK ID          NAME                DRIVER              SCOPE
    # 啟動容器但沒指定網路時，默認bridge
    # d9b9b8d46a49        bridge              bridge              local
    # 與本機共享網路
    # 9f3b97f86be1        host                 host               local
    # 容器沒有網路連接
    # b650d3fbb5a2        none                 null               local
    ```
    * 不同容器要共享（同一個專案的容器）或分離（前端/後端）網路，可以自定義網路
      手動創建網路
    ```
    docker network create my_custom_network
    ```
    將容器連接到自定義網路
    ```
    docker run -d --name my_container --network my_custom_network nginx
    ```
    * 使用 YAML 檔創建容器時，可先定義網路
    ```
    version: "3.0"
    services:

      postgresql:
        image: postgres:13
        ports:
          - "5432:5432"
        environment:
          POSTGRES_DB: test
          POSTGRES_USER: hailey
          POSTGRES_PASSWORD: user841022 
        volumes:
          - postgres-data:/var/lib/postgresql/data
        restart: always
        networks:
          - crawlerproject_dev
    networks:
      crawlerproject_dev:
      external: true
    ```


#### 二、Python環境設置-Poetry
* Python 3 venv
  * 更新 Python3 的venv，創建虛擬環境並啟用
    ```
    cd dsp/kedro
    sudo apt install python3.10-venv
    python3 -m venv venv
    source venv/bin/activate
    ```
  * 安裝套件
    ```
    pip install kedro
    ```
  * 一次安裝所有套件
    ```
    pip install -r requirements.txt
    ```
  * 退出虛擬環境
    ```
    deactivate
    ```
* Virtualenv
  * 國網專案為例，專案檔案依 Linux 檔案系統階層標準 FHS 部署
    * `/srv/www` ：網站檔案。
    * `/etc` ：設定檔。
    * `/var/log` ：記錄檔。
    * `/var/lib/venv` ： Python 虛擬環境。
    ```
    sudo rm -rf /var/lib/venv/swr-api-2023
    sudo mkdir -p /var/lib/venv/swr-api-2023
    sudo chown $USER /var/lib/venv/swr-api-2023
    virtualenv -p python3.11 /var/lib/venv/swr-api-2023
    . /var/lib/venv/swr-api-2023/bin/activate
    wget https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
    pip install "fastapi>=0.95.0" "uvicorn[standard]" "pydantic>=2" "pydantic-settings>=2" python-dotenv dalex joblib "scikit-learn<1.3"
    ```

* 套件管理工具：Poetry
  * 可直接產生 pyproject.toml 說明專案所需套件
  * 使用`pipx`可將 Poetry 安裝到獨立環境
    ```
    sudo apt update
    sudo apt install pipx
    pipx install poetry
    which poetry
    # /home/hailey/.local/pipx/venvs/poetry/bin/poetry
    pipx uninstall poetry
    pipx list
    # nothing has been installed with pipx
    ```
  * 安裝 Poetry，安裝到家目錄，避免安裝到專案虛擬環境
    ```
    pip install poetry==1.1.15
    which poetry
    # /home/hailey/.local/bin/poetry
    ```
    初始化
    ```
    poetry init
    # creating pyproject.toml config
    # [Package name] 套件名稱，以便後續import使用
    # [Version] 版本號
    # [Description] 套件說明
    # [Author] 作者 <email>
    # [License] 許可證
    # [Compatible Python versions] Python版本
    ```
    虛擬環境狀態
    ```
    poetry config --list
    # cache-dir = "/home/hailey/.cache/pypoetry"
    # experimental.new-installer = true
    # installer.parallel = true
    # virtualenvs.create = true 
    # 在偵測不到虛擬環境時會自行建立
    # virtualenvs.in-project = null
    # virtualenvs.path = "{cache-dir}/virtualenvs"  
    # /home/hailey/.cache/pypoetry/virtualenvs
    ```
    調整設定，可以在專案資料夾中建立.venv
    ```
    poetry config virtualenvs.in-project true
    ```
    刪除原本的虛擬環境
    ```
    poetry env remove python3.10
    ```
    重新建立虛擬環境於專案目錄中，一對一關係
    ```
    poetry env use python3.10
    # Creating virtualenv wsl in /mnt/c/Users/dwarf/Desktop/wsl/.venv
    # 並非原本的/home/hailey/.cache/pypoetry/virtualenvs
    # 因為統一將虛擬環境建立在特定目錄裡，意味著單一專案允許建立複數個虛擬環境，且命名模式冗長
    ```
    啟動虛擬環境，需切換至專案資料夾內執行，會偵測當前目錄是否存在pyproject.toml
    ```
    poetry shell
    # . /mnt/c/Users/dwarf/Desktop/CrawlerProject/.venv/bin/activate
    ```
    退出虛擬環境
    ```
    exit
    ```
    安裝套件
    ```
    poetry add flask
    poetry add apscheduler # 排程工具
    ```
    安裝僅用於開發環境的套件
    ```
    poetry add --dev flask
    ```
    開啟 Python
    ```
    poetry run python
    ```
* `pyproject.toml`工具設定檔與套件打包
  * 官方說明：https://packaging.python.org/en/latest/tutorials/packaging-projects/
  * `Poetry`會自動建立`pyproject.toml`，使用`virtualenv`或`venv`建立虛擬環境需自行撰寫`pyproject.toml`
  * 用`Poetry`+`virtualenv`+`pyproject.toml`取代`Pipenv`+`Pipfile`+`setup.py` 
  * 
  ```
  # 國網範例
  # The Social Worker Risk project API, 2023.
  # Copyright 2023 DSP, inc.  All rights reserved.
  # Authors:
  #   imacat.yang@dsp.im (imacat), 2023/10/24

  [project]
  name = "swr-api-2023"
  dynamic = ["version"]
  description = "The Social Worker Risk project API, 2023."
  readme = "README.rst"
  requires-python = ">=3.10"
  authors = [
      {name = "Hailey Hsiao", email = "hailey.hsiao@dsp.im"},
      {name = "imacat", email = "imacat.yang@dsp.im"},
  ]
  keywords = ["risk-score", "nchc"]
  classifiers = [
      "Programming Language :: Python :: 3",
      "License :: Other/Proprietary License",
      "Operating System :: OS Independent",
      "Framework :: FastAPI",
      "Topic :: Scientific/Engineering :: Information Analysis",
  ]
  dependencies = [
      "fastapi >= 0.95.0",
      "uvicorn[standard]",
      "pydantic >= 2",
      "pydantic-settings >= 2",
      "python-dotenv",
      "dalex",
      "joblib",
      "scikit-learn == 1.3.2",
  ]

  [project.optional-dependencies]
  test = [
      "unittest",
      "httpx",
  ]

  [build-system]
  requires = ["setuptools>=42"]
  build-backend = "setuptools.build_meta"

  [tool.setuptools.dynamic]
  version = {attr = "swr_api_2023.VERSION"}
  ```
#### 三、資料庫建置-PostgreSQL
* 資料庫架設：PostgreSQL
  * 下載 PostgreSQL Docker Image
    ```
    sudo docker pull postgres:13
    ```
  * 創建 PostgreSQL Volumns 確保Container關閉時資料不會遺失
    ```
    sudo docker volume create postgres-data
    ```
  * 創建 Container 並掛接 Volumns 
    ```
    sudo docker run -d \
    --name postgres-container \
    -e POSTGRES_PASSWORD=<password> \
    -e POSTGRES_DB=test \
    -p 5432:5432 \
    -v postgres-data:/var/lib/postgresql/data \
    postgres:13
    ```
  * 確認是否掛接成功
    ```
    sudo docker inspect postgres-container
    ```
  * 重啟 Container
    ```
    sudo docker start postgres-container
    ```
  * 停止/刪除 Container
    ```
    sudo docker stop postgres-container
    sudo docker rm postgres-container
    ```
  * 輸出容器的IP位址
    ```
    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres-container
    # 172.17.0.2
    ```
    * 後續用`psql.yml`建立的 Docker Container名稱為`crawlerproject_postgresql_1`，輸出容器的IP位址
    ```
    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' crawlerproject_postgresql_1
    # 172.19.0.2
    ```
  * 確認主機和 Docker 容器之間是否有網路連通性，使用 ping 命令來測試是否可以從主機 ping 到 PostgreSQL 容器的 IP
    ```
    ping 172.17.0.2
    # PING <PostgreSQL_IP> (<PostgreSQL_IP>): 56 data bytes
    # 64 bytes from <PostgreSQL_IP>: icmp_seq=0 ttl=64 time=0.345 ms
    # 64 bytes from <PostgreSQL_IP>: icmp_seq=1 ttl=64 time=0.312 ms
    ```
  * 進入 PostgreSQL Container
    ```
    docker exec -it postgres-container psql -U hailey -d test
    # docker exec -it postgres-container psql -U your_username -d your_database
    ```
  * 後續用`psql.yml`建立的 Docker Container名稱為`crawlerproject_postgresql_1`
    ```
    docker exec -it crawlerproject_postgresql_1 psql -U hailey -d test
    ```


#### 四、資料庫操作-PostgreSQL
* 建立使用者
  ```
  CREATE USER myuser WITH ENCRYPTED PASSWORD 'mypassword';
  ```
  創建使用者 hailey，並給予創建資料庫的權限
  ```
  CREATE USER hailey WITH PASSWORD 'password' CREATEDB;
  ```
* 授權使用者
  ```
  GRANT ALL PRIVILEGES ON DATABASE mydatabase TO myuser;
  ```
  給予 hailey 測試資料庫的所有權限
  ```
  GRANT ALL PRIVILEGES ON DATABASE test TO hailey;
  ```
* 修改密碼
  ```
  psql -U myuser -d mydatabase
  # 方法一
  ALTER USER myuser WITH ENCRYPTED PASSWORD 'newpassword';
  # 方法二
  mydatabase=> \password
  Enter new password:
  Enter it again:
  ```
* 建立資料庫
  ```
  CREATE DATABASE mydatabase;
  ```
* 建立資料庫並指定擁有者
  ```
  CREATE DATABASE mydatabase OWNER myuser;
  ```
* 創建資料表
  ```
  # 台股資料表
  CREATE TABLE taiwanstockprice(
  "StockID" VARCHAR(10) NOT NULL,
  "TradeVolume" BIGINT NOT NULL,
  "Transaction" INT NOT NULL,
  "TradeValue" BIGINT NOT NULL,
  "Open" FLOAT NOT NULL,
  "Max" FLOAT NOT NULL,
  "Min" FLOAT NOT NULL,
  "Close" FLOAT NOT NULL,
  "Change" FLOAT NOT NULL,
  "Date" DATE NOT NULL,
  PRIMARY KEY("StockID", "Date")
  );
  # 台指期資料表
  CREATE TABLE taiwanfuturesdaily(
  "Date" DATE NOT NULL,
  "FuturesID" VARCHAR(10) NOT NULL,
  "ContractDate" VARCHAR(30) NOT NULL,
  "Open" FLOAT NOT NULL,
  "Max" FLOAT NOT NULL,
  "Min" FLOAT NOT NULL,
  "Close" FLOAT NOT NULL,
  "Change" FLOAT NOT NULL,
  "ChangePer" FLOAT NOT NULL,
  "Volume" FLOAT NOT NULL,
  "SettlementPrice" FLOAT NOT NULL,
  "OpenInterest" INT NOT NULL,
  "TradingSession" VARCHAR(11) NOT NULL,
  PRIMARY KEY("Date","FuturesID", "ContractDate","TradingSession")
  );
  ```
* 列出欄位
  ```
  SELECT column_name
  FROM information_schema.columns
  WHERE table_name = 'taiwanstockprice';
  ```
* 查看類型
  ```
  SELECT column_name, data_type
  FROM information_schema.columns
  WHERE table_name = 'taiwanstockprice';
  ```
* 修改資料表，新增欄位/修改欄位資料類型
  ```
  ALTER TABLE person
  ALTER COLUMN age TYPE int;
  # age從text轉換為int，需使用轉換式
  ALTER TABLE person
  ALTER COLUMN age TYPE integer
  USING age::integer;
  ```
* 刪除資料表
  ```
  DROP TABLE table_name;
  ```
* 僅刪除資料表內容
  ```
  DELETE FROM table_name;
  ```
* 建立主鍵值
  ```
  ALTER TABLE person ADD PRIMARY KEY (name);
  ```
#### 五、分散式任務-RabbitMQ
* 分散式任務轉發 RabbitMQ
  * Producer -> 發送任務 -> Broker <- 拿取任務<- Worker
  * Broker 是訊息傳遞中心：RabbitMQ
  * Worker 的監控工具：Flower
  * RabbitMQ 與 Flower 安裝
    * Docker 安裝 `rabbitmq.yml`
      ```
      docker-compose -f rabbitmq.yml up -d
      ```
    * 瀏覽器輸入`http://localhost:15672/`啟動 `RabbitMQ` 畫面，帳號密碼預設為worker/worker
    * 瀏覽器輸入`http://localhost:5555/`啟動 `Flower` 畫面
  * 輸出容器的IP位址
    ```
    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' crawlerproject_rabbitmq_1
    # 172.19.0.3
    ```
* 分散式套件 Celery
  * 安裝 Celery
    ```
    poetry add celery
    ```
  * `worker.py`：使用 Celery 建立 Worker 並連線至RabbitMQ
  * `tasks.py`：匯入剛剛建立的 Worker，註冊任務，把要執行的程式碼放在這裡
  * `producer.py`：匯入剛剛建立的執行程式碼，呼叫他以發送任務
  * 啟動 Celery Worker，專門執行 twse/tpex queue 的任務，查看 Flower 有沒有出現對應的 Worker 並顯示online狀態
    ```
    poetry run celery -A finandata.tasks.worker worker --loglevel=info --concurrency=1  --hostname=%h -Q twse
    poetry run celery -A finandata.tasks.worker worker --loglevel=info --concurrency=1  --hostname=%h -Q tpex
    ```
  * 使用 terminal 啟動 Celery Worker 時，注意 `.env` 要指定 RabbitMQ Container 的 IP 位址 `MESSAGE_QUEUE_HOST=172.19.0.3`
    ```
    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' crawlerproject_rabbitmq_1
    # 172.19.0.3
    ```
  * 後續部署成 Docker Container YAML檔案`crawler_multi.yml`以啟動 Celery Worker 後，`.env` 的 IP 位址就要命名成容器的名稱`PSQL_DATA_HOST=postgresql` `MESSAGE_QUEUE_HOST=rabbitmq`
  * 使用`producer.py`，發送任務
    ```  
    poetry run python3.10 -m finandata.tasks.producer taiwan_stock_price '2024-04-24' '2024-04-25'
    ```
  * 如果關閉`Celery Worker`，然後發送任務，在`RabbitMQ`瀏覽器介面的Queues-GetMessage(s)會出現剛剛發送的任務
* `Linode`：要實現真正的分散式架構，需要花錢申請多台機器，先跳過
* `APScheduler`：定時爬蟲
  * 安裝`APScheduler`
    ```
    poetry add apscheduler
    ```
  * `scheduler.py`編輯檔案設定排程
  * 執行排程
    ```
    poetry run python3.10 -m finandata.tasks.scheduler
    ```

#### 六、管理環境變數-local.ini
* `local.ini`：管理開發、測試、正式環境變數。包含PostgreSQL 與 RabbitMQ 的環境變數
  * 在正式環境變數[RELEASE]，可以用 Docker 容器的 service name 代替 IP 來連線，例如：`PSQL_DATA_HOST=postgresql` `MESSAGE_QUEUE_HOST=rabbitmq`，部署在開發與產品環境時不受 IP 限制，也不會洩漏 host 資訊
* `genenv.py`：建立`.env`環境檔
* 選擇建立預設的環境檔（傳入環境參數）
  ```
  poetry run python3.10 -m genenv DEFAULT
  ```

#### 七、程式設定檔-config
* 使用`config.py`取用`.env`的環境變數
  * 安裝`python-dotenv`來載入`.env`環境變數
  ```
  poetry add python-dotenv
  ```

#### 八、資料庫連線-clients
* `clients.py`：管理所有對資料庫的連線
  * SQLAlchemy 支援 ORM (Object-relational Mapping)，可用物件方式操作資料庫
  * 安裝 SQLAlchemy 的 PostgreSQL 驅動程式：psycopg2-binary
    ```
    poetry add sqlalchemy
    poetry add psycopg2-binary
    ```
* **(這邊不會先省略)** `router.py`：管理資料庫連線 connect、上傳 upload、確認連線是否存活 alive
  * 安裝 loguru 紀錄日誌
    ```
    poetry add loguru
    ```

#### 九、資料收集
* 證交所資料
  * 資料來源：https://www.twse.com.tw/zh/trading/historical/mi-index.html
  * 取得方式：GET
  * 編輯`twse_crawler.py`
* 櫃買中心資料
  * 資料來源：https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw
  * 取得方式：GET
  * 編輯`tpex_crawler.py`
* 期交所資料
  * 資料來源：https://www.taifex.com.tw/cht/3/futDailyMarketView
  * 取得方式：POST
  * 編輯`taifex_crawler.py`

#### 七、存入資料庫
* 執行`twse_crawler.py`
  ```
  poetry run python3.10 -m finandata.twse_crawler 2024-02-19 2024-02-20
  ```
* 執行`tpex_crawler.py`
  ```
  poetry run python3.10 -m finandata.tpex_crawler.py 2024-02-19 2024-02-20
  ```
* 執行`taifex_crawler.py`
  ```
  poetry run python3.10 -m finandata.taifex_crawler.py 2024-02-19 2024-02-20
  ```

#### 九、資料提供-datareleas
* RESTful API：一種界接介面，用於不同程式與軟體間的呼叫與傳遞，定義了GET、POST、PUT、DELETE等操作，進行資料拿取、推送、更新、刪除。
* 初始化
  ```
  poetry init
  ```
  虛擬環境狀態
  ```
  poetry config --list
  ```
  調整設定，可以在專案資料夾中建立.venv
  ```
  poetry config virtualenvs.in-project true
  ```
  建立虛擬環境於專案目錄中，一對一關係
  ```
  poetry env use python3.10
  # Creating virtualenv wsl in /mnt/c/Users/dwarf/Desktop/datarelease/.venv
  ```
  啟動虛擬環境，需切換至專案資料夾內執行，會偵測當前目錄是否存在pyproject.toml
  ```
  poetry shell
  ```
  退出虛擬環境
  ```
  exit
  ```
  安裝套件
  ```
  poetry add fastapi pandas sqlalchemy uvicorn psycopg2-binary requests
  ```
  開啟 Python
  ```
  poetry run python
  ```
* 編輯`main.py`，從PostgreSQL撈資料出來，透過API回傳給使用者
* 執行`main.py`，啟動API
  ```
  poetry run uvicorn main:app --reload --port 8080
  ```
* 撰寫測試文件`test.py`，模擬使用者呼叫API
  ```
  poetry run python test.py
  ```
* 用URL呼叫：http://127.0.0.1:8080/taiwan_stock_price?stock_id=2330&start_date=2024-04-24&end_date=2024-04-24


#### 九、壓力測試
* ApacheBench：對伺服器進行基準測試的工具，可以模擬多個使用者同時對伺服器發送多個request，統計每次request需要多少時間，中途是否有failed。
* 安裝套件
  ```
  sudo apt-get install apache2-utils -y
  ```
* 進行壓力測試
  ```
  ab -c 10 -n 1000 'http://127.0.0.1:8080/'
  ```
#### 十、API介面-Swagger
* Swagger：自動生成的OpenAPI文件，可以直接在Web上對API發送request
* 啟動API
  ```
  poetry run uvicorn main:app --reload --port 8080
  ```
* 瀏覽器輸入`http://127.0.0.1:8080/docs`，點選不同的路徑參數，使用`Try it out`呼叫API
* 修改設定，將localhost、127.0.0.1改成實體IP，便能在雲端Linode上架設API，讓別人使用該服務

