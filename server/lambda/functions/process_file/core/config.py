import os


class Settings:
    VDB_URI: str
    VDB_HEADER: str
    VDB_PORT: int
    VDB_SECRET_KEY: str
    HOOK_URL: str
    HOOK_SECRET: str
    DEBUG: bool

    def __init__(self):
        self.VDB_URI = os.environ["DB_URI"]
        self.VDB_PORT = int(os.environ["VDB_PORT"])
        self.VDB_SECRET_KEY = os.environ["VDB_SECRET_KEY"]
        self.VDB_HEADER = os.environ.get("VDB_HEADER", "Authorization")
        self.HOOK_URL = os.environ["HOOK_URL"]
        self.HOOK_SECRET = os.environ["HOOK_SECRET"]
        self.DEBUG = os.environ.get("DEBUG", "false").lower() == "true"


def get_settings():
    return Settings()
