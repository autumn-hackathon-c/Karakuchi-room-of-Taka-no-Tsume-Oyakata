from django.shortcuts import render, redirect
from .forms import SurveyForm
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy

from karakuchi_room.models import Survey
from django.contrib.auth import get_user_model
from django.contrib import messages
import logging

#ログ出力するために記載
logger = logging.getLogger(__name__)

# アンケート画面(surveys)

#アンケート一覧画面
class SurveyListView(ListView):
    model = Survey
    template_name = "karakuchi_room/surveys.html"

#アンケート詳細画面
class SurveyDetailView(DetailView):
    model = Survey
    template_name = "karakuchi_room/surveys_detail.html" 

#ゲストユーザー（ログイン機能ができるまで暫定的に記載）
def get_guest_user():
    User = get_user_model()
    guest, _ = User.objects.get_or_create(
        username="guest",
        defaults={"email": "guest@example.com", "is_active": True},
    )
    return guest

#アンケート新規作成
class SurveyCreateView(CreateView):
    model = Survey
    form_class = SurveyForm                          # ← ModelForm を使う
    template_name = "karakuchi_room/surveys_create.html" 
    success_url = None                               

    def form_valid(self, form):
        survey = form.save(commit=False)
        user = self.request.user if self.request.user.is_authenticated else get_guest_user()
        survey.user = user
        survey.save()
        messages.success(self.request, "アンケートを作成しました。")
        return redirect("survey-list")  # ← 成功時は必ず 302

    def form_invalid(self, form):
        logger.warning("SurveyCreate errors: %s", form.errors)  # ← サーバーログに出す
        return super().form_invalid(form) 
    
#アンケート削除
class SurveyDeleteView(DeleteView):
    model = Survey
    #成功後、一覧画面リダイレクト
    success_url = reverse_lazy("surveys")
    #モーダルなのでtemplate_nameは不要

#アンケート編集画面(一時保存)
class SurveyUpdateView(UpdateView):
    model = Survey
    fields ="__all__"
    template_name = "karakuchi_room/surveys_edit_save_temporary.html"
    success_url = reverse_lazy("surveys-detail")

#アンケート編集画面(公開済)
class SurveyTemporaryUpdateView(UpdateView):
    model = Survey
    fields ="__all__"
    template_name = "karakuchi_room/surveys_edit_published.html"
    success_url = reverse_lazy("surveys-detail")
