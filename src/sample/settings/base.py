# src/sample/settings/base.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECRET_KEY = os.environ.get("SECRET_KEY")
SECRET_KEY = "django-insecure-d%p-lt!l95$%*=1@yiu2wn4c-c@bkjgu^=l)7df$64saa7uj9l"

DEBUG = False  # ここでは固定せず、各環境で上書き

ALLOWED_HOSTS: list[str] = []  # 各環境で上書き

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "karakuchi_room.apps.KarakuchiRoomConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "sample.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sample.wsgi.application"

# 認証ユーザーのモデルを指定
AUTH_USER_MODEL = "karakuchi_room.User"


LOGIN_URL = "/login"
LOGOUT_REDIRECT_URL = "login"

# パスワードバリデータ
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 未ログイン状態でログインが必要なページにアクセスしたときに
# ログインページにリダイレクトされる
LOGIN_URL = "login"
# ログインしたらアンケート一覧画面にリダイレクト
LOGIN_REDIRECT_URL = "survey-list"
# ログアウトしたらログインページにリダイレクト
LOGOUT_REDIRECT_URL = "login"

# テンプレ/静的の共通
STATICFILES_DIRS = [BASE_DIR / "static"]

# ここではDBやS3、CSRF信頼オリジン、セキュリティヘッダなど
# “環境で変わるもの”は書かず、dev/prodで上書きする
