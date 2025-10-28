# 鷹の爪親方の辛口部屋

## 環境構築手順

※適宜修正する可能性あり。その際は都度共有予定🙇‍♂️

### 1. リポジトリをクローン
```
git clone git@github.com:autumn-hackathon-c/Karakuchi-room-of-Taka-no-Tsume-Oyakata.git
cd Karakuchi-room-of-Taka-no-Tsume-Oyakata
```

### 2. envファイル作成
```
touch .env
```
(具体的なソースコードの中身は違う方法で共有予定)


### 3.Django プロジェクトを起動

#### 3.1 ビルド
```
docker-compose build
```

#### 3.2 起動
```
docker-compose up -d
```

#### 3.3 削除
```
docker-compose　down
```

### 3.4 アクセス確認方法
Webアプリ： http://localhost:8000

### 4.マイグレーション関連コマンド一覧

#### 4.1. マイグレーションファイルを作成
```
docker-compose exec django python manage.py makemigrations
```

#### 4.2 マイグレーションを実行（テーブル作成など）
```
docker-compose exec django python manage.py migrate
```

## コマンド集 （汎用的に使うコマンドがあれば、都度記載予定)

### 1 MySQLコンテナに接続
```
docker exec -it mysql mysql -u root -p
```
パスワードを聞かれたら.env に書いた rootpass を入力

DB選択
```
use app_db
```

他は以下の記事やSQL文を各自で確認するようにしてください🙇‍♂️
https://qiita.com/yuzooho/items/5d608f3b84a2037cada0


### 2.Ruffコマンド
Lint(コードチェックのみ)

```bash
make lint-check
```

Format（コード整形）

```bash
make format
```
上記がOKでないとマージできないので
プルリク投げる際は都度上記を実行するようにしてください。
ただし、フロントエンド(HTML,CSS,JavaScript)の内容は修正不可


練習でプルリク投げます。




