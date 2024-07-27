# 建立 psql volume
create-psql-volume:
	docker volume create postgres-data

# 啟動 psql 容器
create-psql:
	docker-compose -f psql.yml up -d

# 啟動 rabbitmq 容器
create-rabbitmq:
	docker-compose -f rabbitmq.yml up -d

# 啟動環境
install-python-env:
	poetry shell

# 啟動 celery, 專門執行 twse queue 列隊的任務
# --concurrency=1：這裡預設為CPU核心數，由於證交所會banIP，須設定一次只能執行一個任務
run-celery-twse:
	poetry run celery -A finandata.tasks.worker worker --loglevel=info --concurrency=1  --hostname=%h -Q twse

# 啟動 celery, 專門執行 tpex queue 列隊的任務
run-celery-tpex:
	poetry run celery -A finandata.tasks.worker worker --loglevel=info --concurrency=1  --hostname=%h -Q tpex

# sent task
sent-taiwan-stock-price-task:
	poetry run python3.10 -m finandata.tasks.producer taiwan_stock_price 2024-04-24 2024-04-24

# 建立 dev 環境變數
gen-dev-env-variable:
	poetry run python3.10 -m genenv DEFAULT

# 建立 staging 環境變數
gen-staging-env-variable:
	poetry run python3.10 -m genenv STAGING

# 建立 release 環境變數
gen-release-env-variable:
	poetry run python3.10 -m genenv RELEASE

# 建立 image
build-image:
	docker build -f Dockerfile -t crawler:7.2.1 .

# 啟動 crawler 容器
up-crawler:
	docker-compose -f crawler.yml up

# 啟動 multi-crawler 容器
up-multi-crawler:
	docker-compose -f crawler_multi_celery.yml up

# 啟動自動化排程
run-scheduler:
	poetry run python3.10 -m finandata.tasks.scheduler

# 啟動 scheduler 容器
up-scheduler:
	docker-compose -f scheduler.yml up

tag-image:
	docker tag crawler:7.2.1 haileyhhh/crawler:7.2.1

push-image:
	docker push haileyhhh/crawler:7.2.1

