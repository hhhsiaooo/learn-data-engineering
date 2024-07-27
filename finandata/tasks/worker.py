from celery import Celery
from finandata.config import (
    WORKER_ACCOUNT,
    WORKER_PASSWORD,
    MESSAGE_QUEUE_HOST,
    MESSAGE_QUEUE_PORT,
)

broker = (
    f"pyamqp://{WORKER_ACCOUNT}:{WORKER_PASSWORD}@"
    f"{MESSAGE_QUEUE_HOST}:{MESSAGE_QUEUE_PORT}/"
)

app = Celery(
    "tasks",
    # 只包含 tasks.py 裡面的程式, 才會成功執行
    include=["finandata.tasks.tasks"],
    # 連線到 rabbitmq,
    broker=broker,
)
