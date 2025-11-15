# ruff: noqa: F401, F403, F405
import os
from pathlib import Path
from .base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ["karakuchi-room.com", "www.karakuchi-room.com"]

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
#  DB (RDS)
# =========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "use_unicode": True,
            "init_command": "SET NAMES utf8mb4",
        },
    },
}

# =========================
#  S3 (IAMロールを使う想定)
# =========================

# ← ここでは AWS_ACCESS_KEY_ID / SECRET は **使わない**
#    コンテナは EC2 の IAM ロール経由で S3 にアクセスさせる

AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "ap-northeast-1")

AWS_S3_CUSTOM_DOMAIN = os.getenv(
    "AWS_S3_CUSTOM_DOMAIN",
    f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com",
)

AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = True
AWS_S3_FILE_OVERWRITE = False

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "public, max-age=86400",
}

# --- static (S3) ---
AWS_LOCATION = "static"  # S3 上のフォルダ名

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"


# --- 逆プロキシ(ALB)配下 ---
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_TRUSTED_ORIGINS = [
    "https://karakuchi-room.com",
    "https://www.karakuchi-room.com",
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
