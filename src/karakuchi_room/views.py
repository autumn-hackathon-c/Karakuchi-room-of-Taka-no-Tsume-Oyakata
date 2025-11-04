
from django.views.generic import CreateView
# 会員登録する」ためにCreateViewが必要
# CREATEVIEWは汎用的なビューだからdjango.views.genericの中のCreateViewになる
# ここはトイトイさんとコンフリクト起こすかも

from django.contrib.auth.views import LoginView
# LoginViewをインポートする事でテンプレート名や
# リダイレクト先を指定するだけでログイン画面を作成できる
# django.contrib.auth.viewは認証用ビュー群


from django.contrib.auth.mixins import LoginRequiredMixin
# 裏側のロジック(view)でコントロールする
# ログインしているユーザーだけにアクセスを許可する


from django.contrib.auth.forms import UserCreationForm
# ユーザー周りのフォームをインポート

from django.urls import reverse_lazy
# reverse_lazyをインポートすることでリダイレクト先を指定できる

from .forms import CustomUserCreationForm, LoginForm
# 同じアプリケーション内のforms.pyからCustomUserFormとLoginFormをインポート




# 新規登録
class SignUpView(CreateView):
    template_name = "karakuchi_room/signup.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")



# ログイン
class MyLoginView(LoginView):
    template_name = "karakuchi_room/login.html"
    redirect_authenticated_user = True
    form_class = LoginForm






# from django.shortcuts import render
# from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
# from django.urls import reverse_lazy

# from karakuchi_room.models import Survey

# アンケート画面(surveys)

# アンケート一覧画面
# class TaskListView(ListView):
# model = Survey
# template_name = "karakuchi_room/surveys.html"

# アンケート詳細画面
# class TaskDetailView(DetailView):
# model = Survey
# template_name = "karakuchi_room/surveys_detail.html"

# アンケート作成画面
# class TaskCreateView(CreateView):
# model = Survey
# フォームに title, description, due_date の 3 つすべてが自動で生成される
# fields = "__all__"
# template_name = "karakuchi_room/surveys_create.html"
# 成功後、詳細画面にリダイレクト
# success_url = reverse_lazy("surveys-detail")

# アンケート削除
# class TaskDeleteView(DeleteView):
# model = Survey
# 成功後、一覧画面リダイレクト
# success_url = reverse_lazy("surveys")
# モーダルなのでtemplate_nameは不要

# アンケート編集画面(一時保存)
# class TaskUpdateView(UpdateView):
# model = Survey
# fields ="__all__"
# template_name = "karakuchi_room/surveys_edit_save_temporary.html"
# success_url = reverse_lazy("surveys-detail")

# アンケート編集画面(公開済)
# class TaskUpdateView(UpdateView):
# model = Survey
# fields ="__all__"
# template_name = "karakuchi_room/surveys_edit_published.html"
# success_url = reverse_lazy("surveys-detail")


