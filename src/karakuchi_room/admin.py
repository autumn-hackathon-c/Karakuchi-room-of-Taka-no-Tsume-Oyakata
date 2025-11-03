from django.contrib import admin
from karakuchi_room.models import Survey

# 管理画面でSurveysテーブルのテストデータを入れるために実装
admin.site.register(Survey)


