from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy

from karakuchi_room.models import Survey

# アンケート画面(surveys)

#アンケート一覧画面
class SurveyListView(ListView):
    model = Survey
    template_name = "karakuchi_room/surveys.html"

#アンケート詳細画面
class SurveyDetailView(DetailView):
    model = Survey
    template_name = "karakuchi_room/surveys_detail.html"

#アンケート作成画面
class SurveyCreateView(CreateView):
    model = Survey
    fields = "__all__"
    template_name = "karakuchi_room/surveys_create.html"
    #成功後、詳細画面にリダイレクト
    success_url = reverse_lazy("surveys-detail")

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
