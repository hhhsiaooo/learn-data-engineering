## 1.基於此作業系統 image 建構應用程式
FROM ubuntu:22.04

## 2.安裝運行環境

# 系統升級、安裝 python
RUN apt-get update && apt-get install python3.10 -y && apt-get install python3-pip -y

## 3.複製應用程式、安裝套件、環境配置

# 建立資料夾存放爬蟲程式碼
RUN mkdir /CrawlerProject

# 將當前路徑下所有檔案複製進去
COPY . /CrawlerProject/

# 設定工作目錄
WORKDIR /CrawlerProject/

# 設定環境變數
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# 安裝Poetry
RUN pip install poetry
RUN poetry config virtualenvs.in-project true
# RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
# RUN pip install --no-cache-dir --upgrade -r /CrawlerProject/requirements.txt
# 不安裝套件，直接在正式機設置poetry並安裝pyproject.toml裡的套件
# poetry shell
# poetry env use python3.10
# poetry install


# 不建立.env，另外給正式機.env和local.ini檔案，而不是包在docker裡面
# RUN poetry run python3.10 -m genenv RELEASE