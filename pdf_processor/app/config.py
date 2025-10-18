import os
from dotenv import load_dotenv


class Settings:
    VDB_URI: str
    VDB_HEADER: str
    VDB_PORT: int
    COLLECTION_NAME: str
    VDB_SECRET_KEY: str
    DEBUG: bool
    CELERY_SQS_QUEUE: str
    CELERY_SQS_QUEUE_NAME: str
    SQS_QUEUE: str
    SQS_QUEUE_NAME: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_ACCESS_KEY_ID: str
    BUCKET_NAME: str
    AWS_REGION: str

    def __init__(self):
        load_dotenv()

        self.VDB_URI = os.environ["VDB_URI"]
        self.VDB_PORT = int(os.environ["VDB_PORT"])
        self.COLLECTION_NAME = os.environ["COLLECTION_NAME"]
        self.VDB_SECRET_KEY = os.environ["VDB_SECRET_KEY"]
        self.VDB_HEADER = os.environ.get("VDB_HEADER", "Authorization")
        self.DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
        self.CELERY_SQS_QUEUE = os.environ["CELERY_SQS_QUEUE"]
        self.CELERY_SQS_QUEUE_NAME = os.environ["CELERY_SQS_QUEUE_NAME"]
        self.SQS_QUEUE = os.environ["SQS_QUEUE"]
        self.SQS_QUEUE_NAME = os.environ["SQS_QUEUE_NAME"]
        self.AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
        self.AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
        self.BUCKET_NAME = os.environ["BUCKET_NAME"]
        self.AWS_REGION = os.environ["AWS_REGION"]


def get_settings():
    return Settings()
