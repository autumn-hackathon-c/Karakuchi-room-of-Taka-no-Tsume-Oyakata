# ruff: noqa: F401, F403, F405
import os
from .base import *  # noqa


DEBUG = False
ALLOWED_HOSTS = ["karakuchi-room.com", "www.karakuchi-room.com"]

# RDS: writer/reader
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.getenv("DB_PORT", "3306"),
        # 絵文字の文字化け対策
        "OPTIONS": {
            "charset": "utf8mb4",
            "use_unicode": True,
            "init_command": "SET NAMES utf8mb4",
        },
    },
}

# --- S3 ---
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
AWS_S3_CUSTOM_DOMAIN = os.getenv(
    "AWS_S3_CUSTOM_DOMAIN",
    f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com",
)

# 署名・公開URLの推奨
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = True  # 署名付きクエリ
AWS_S3_FILE_OVERWRITE = False  # 同名アップ時の上書き防止（任意）

# Cache-Control（静的は長期 / メディアは短め）
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "public, max-age=86400"  # デフォルト: 1日（主に media）
}

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"

# collectstatic の送り先を S3 に変更
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
# DEFAULT_FILE_STORAGE = "closet_search.storage_backends.MediaStorage"

# 逆プロキシ(ALB)配下
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF信頼オリジン
CSRF_TRUSTED_ORIGINS = [
    "https://karakuchi-room.com",
    "https://www.karakuchi-room.com",
]

# セキュアCookie
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
