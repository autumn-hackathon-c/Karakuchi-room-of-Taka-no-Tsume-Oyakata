# ruff: noqa: F401, F403, F405
import os
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]  # ローカル/コンテナからのアクセス許可

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DATABASE"),
        "USER": os.getenv("MYSQL_USER"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD"),
        "HOST": "db",
        "PORT": "3306",
        # 絵文字の文字化け対策
        "OPTIONS": {
            "charset": "utf8mb4",
            "use_unicode": True,
            "init_command": "SET NAMES utf8mb4",
        },
    }
}

# 静的/メディアはローカル配信
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

USE_X_FORWARDED_HOST = False
SECURE_PROXY_SSL_HEADER = None
# CSRF_TRUSTED_ORIGINS = ["http://localhost:8000"]