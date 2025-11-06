from django.contrib import admin
from karakuchi_room.models import User, Survey, Option

# 管理画面でテストデータを入れるために実装
(admin.site.register(User),)
(admin.site.register(Survey),)
admin.site.register(Option)
