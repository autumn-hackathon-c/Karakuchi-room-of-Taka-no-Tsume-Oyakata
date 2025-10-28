FROM python:3.11.3

ENV PYTHONUNBUFFERED 1

# 作業ディレクトリを /app に変更
WORKDIR /app

# 依存パッケージを先にコピー＆インストール
COPY containers/requirements.txt .

RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install -r requirements.txt \
    && pip install --no-cache-dir "ruff[format]"

# MySQLクライアントツールをインストール（Debian系は default-mysql-client を使う）
RUN apt-get update \
 && apt-get install -y --no-install-recommends default-mysql-client \
 && rm -rf /var/lib/apt/lists/*

