from django.contrib import admin

from karakuchi_room.models import User, Survey, Option, Vote, Tag, TagSurvey

# 管理画面でテストデータを入れるために実装
(admin.site.register(User),)
(admin.site.register(Option),)
admin.site.register(Vote)

# 管理画面でSurvey編集画面に表示される「中間テーブルの編集フォーム」の定義
# SurveyにTagSurveyを埋め込んでいる
class TagSurveyInline(admin.TabularInline):
    model = TagSurvey
    extra = 1


# Surveyを管理画面に登録している
@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    inlines = [TagSurveyInline]

