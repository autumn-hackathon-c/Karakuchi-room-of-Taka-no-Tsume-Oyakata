# ruff: noqa: F401, F403, F405
import os
from pathlib import Path
from .base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = [
    "karakuchi-room.com",
    "www.karakuchi-room.com",
    "localhost",
    "127.0.0.1",
]

BASE_DIR = Path(__file__).resolve().parent.parent

# 静的/メディアを S3 配信すると挙動が重くなる不具合が発生したのでローカルに切り替え
STATIC_URL = "/static/"

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
        # 絵文字の文字化け対策
        "OPTIONS": {
            "charset": "utf8mb4",
            "use_unicode": True,
            "init_command": "SET NAMES utf8mb4",
        },
    },
}

# RDS の初回接続高速化（DBコネクションを維持）
DATABASES["default"]["CONN_MAX_AGE"] = 60

# =========================
#  S3 (IAMロールを使う想定)
# =========================

# AWS_ACCESS_KEY_ID / SECRET は **使わない**
# コンテナは EC2 の IAM ロール経由で S3 にアクセスさせる

# パケット名
AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]

# リージョン名
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "ap-northeast-1")

# S3 のカスタムドメイン（静的ファイルの配信用 URL）
AWS_S3_CUSTOM_DOMAIN = os.getenv(
    "AWS_S3_CUSTOM_DOMAIN",
    f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com",
)

# 署名・公開URLの推奨
AWS_S3_SIGNATURE_VERSION = "s3v4"

AWS_DEFAULT_ACL = None

# 署名付きクエリ
AWS_QUERYSTRING_AUTH = False

# 同名アップ時の上書き防止（任意）
AWS_S3_FILE_OVERWRITE = False

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "public, max-age=86400",
}

# --- static (S3) ---
AWS_LOCATION = "static"  # S3 上のフォルダ名

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"

# collectstatic の送り先を S3 に変更
STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"


# --- 逆プロキシ(ALB)配下 ---
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
