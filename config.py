import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
    DATABASE_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "instance" / "privshare.db"))
    STORAGE_DIR = Path(os.getenv("STORAGE_DIR", BASE_DIR / "storage" / "encrypted_files"))
    TMP_DIR = Path(os.getenv("TMP_DIR", BASE_DIR / "storage" / "tmp"))
    MAX_CONTENT_LENGTH_MB = int(os.getenv("MAX_CONTENT_LENGTH_MB", "32"))
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH_MB * 1024 * 1024
    DEFAULT_EXPIRY_HOURS = int(os.getenv("DEFAULT_EXPIRY_HOURS", "24"))
    PBKDF2_ITERATIONS = int(os.getenv("PBKDF2_ITERATIONS", "390000"))
    TRUST_PROXY_HEADERS = os.getenv("TRUST_PROXY_HEADERS", "0") == "1"

    # All file types allowed. Metadata cleaning applies to supported types only.

    @classmethod
    def ensure_dirs(cls):
        cls.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        cls.TMP_DIR.mkdir(parents=True, exist_ok=True)
