from django.contrib import admin

from karakuchi_room.models import User, Survey, Option, Vote, Tag, TagSurvey

from django.forms import ValidationError
from django.forms.models import BaseInlineFormSet

# 管理画面でテストデータを入れるために実装
(admin.site.register(User),)
(admin.site.register(Option),)
(admin.site.register(Vote),)
(admin.site.register(Tag),)


# 管理画面でSurvey編集画面に表示される「中間テーブルの編集フォーム」の定義
# SurveyにTagSurveyを埋め込んでいる
class TagSurveyInline(admin.TabularInline):
    model = TagSurvey
    extra = 1


# 管理者画面で選択肢（２つ以上必須、最大４つまで）の制約をかけるために定義
class OptionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0

        for form in self.forms:
            # 削除されていない + label があるフォームをカウント
            if not form.cleaned_data.get("DELETE", False) and form.cleaned_data.get(
                "label"
            ):
                count += 1

        if count < 2:
            raise ValidationError("選択肢は2つ以上必要です。")

        if count > 4:
            raise ValidationError("選択肢は最大4つまでです。")


class OptionInline(admin.TabularInline):
    model = Option
    formset = OptionInlineFormSet
    extra = 1


# Surveyを管理画面に登録している
@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    inlines = [TagSurveyInline, OptionInline]
