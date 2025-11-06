# from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from .forms import SurveyCreateForm, OptionFormSet, SurveyFormDraft, SurveyFormPublished
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db import transaction
from django.urls import reverse_lazy
from karakuchi_room.models import Survey
from django.contrib.auth import get_user_model
from django.contrib import messages
import logging

# ログ出力するために記載
logger = logging.getLogger(__name__)

# アンケート画面(Surveys)


# アンケート一覧画面
class SurveyListView(ListView):
    model = Survey
    template_name = "karakuchi_room/surveys.html"


# アンケート詳細画面
class SurveyDetailView(DetailView):
    model = Survey
    template_name = "karakuchi_room/surveys_detail.html"

    # 以下、選択項目を表示させるための設定
    ## テンプレート変数名を指定
    context_object_name = "survey"

    ## アンケートに紐づく選択肢（Option）を取得する。
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["vote_list"] = self.object.options.filter(is_deleted=False)
        return ctx


# ゲストユーザー（ログイン機能ができるまで暫定的に記載）
def get_guest_user():
    User = get_user_model()
    guest, _ = User.objects.get_or_create(
        username="guest",
        defaults={"email": "guest@example.com", "is_active": True},
    )
    return guest


# アンケート新規作成
class SurveyCreateView(CreateView):
    model = Survey
    # ModelForm を使う
    form_class = SurveyCreateForm
    template_name = "karakuchi_room/surveys_create.html"
    success_url = None

    # SurveyフォームとOptionフォームセットをテンプレートに渡す
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["formset"] = OptionFormSet(self.request.POST)
        else:
            ctx["formset"] = OptionFormSet()
        return ctx

    # SurveyとOptionをまとめて保存
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():  # どちらか失敗すればロールバック
                survey = form.save(commit=False)
                user = (
                    self.request.user
                    if self.request.user.is_authenticated
                    else get_guest_user()
                )
                survey.user = user
                survey.save()
                formset.instance = survey  # Option の親を設定
                formset.save()

            messages.success(self.request, "アンケートを作成しました。")
            return redirect("survey-list")

        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容にエラーがあります。")
        return super().form_invalid(form)


# アンケート編集画面(一時保存)
class SurveyTemporaryUpdateView(UpdateView):
    model = Survey
    form_class = SurveyFormDraft
    template_name = "karakuchi_room/surveys_edit_save_temporary.html"

    # 下書きだけを対象にする（公開済みは404）
    def get_queryset(self):
        return Survey.objects.filter(is_public=False)

    def get_success_url(self):
        return reverse_lazy("survey-detail", kwargs={"pk": self.object.pk})

    # ラジオで公開に切り替え可能にするならここで反映
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.is_public = bool(form.cleaned_data.get("is_public", False))
        obj.save()
        return super().form_valid(form)


# アンケート編集画面(公開済)
class SurveyUpdateView(UpdateView):
    model = Survey
    form_class = SurveyFormPublished
    template_name = "karakuchi_room/surveys_edit_published.html"

    # 公開済みだけを対象にする（下書きは404）
    def get_queryset(self):
        return Survey.objects.filter(is_public=True)

    def get_success_url(self):
        return reverse_lazy("survey-detail", kwargs={"pk": self.object.pk})

    # 公開済みは常に公開のままに固定するなら明示しておく
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.is_public = True  # 常に公開維持（解除を許さない）
        obj.save()
        return super().form_valid(form)


# アンケート削除(DeleteViewは別途削除用のページが必要なので、今回は別の方法で実装)
def survey_delete(request, pk):
    obj = get_object_or_404(Survey, pk=pk)
    obj.delete()
    messages.success(request, "削除しました。")
    return redirect("survey-list")
