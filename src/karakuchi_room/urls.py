from django.urls import path

from django.contrib.auth.views import LogoutView
from .views import survey_delete, vote_delete, soften_comment

from karakuchi_room.views import MyLoginView, SignUpView

from karakuchi_room.views import (
    SurveyListView,
    SurveyDetailView,
    SurveyCreateView,
    SurveyTemporaryUpdateView,
    SurveyUpdateView,
    VoteCreateView,
    VoteDetailView,
    VoteUpdateView,
)


urlpatterns = [
    # 新規作成
    path("signup/", SignUpView.as_view(), name="signup"),
    # ログイン
    path("login/", MyLoginView.as_view(), name="login"),
    # ログアウト
    path("logout/", LogoutView.as_view(), name="logout"),
    # アンケート一覧
    path("", SurveyListView.as_view(), name="survey-list"),
    # アンケート新規作成
    path("surveys/create/", SurveyCreateView.as_view(), name="survey-create"),
    # アンケート詳細
    path("surveys/detail/<int:pk>", SurveyDetailView.as_view(), name="survey-detail"),
    # アンケート削除
    path("surveys/delete/<int:pk>", survey_delete, name="survey-delete"),
    # アンケート編集(一時保存)
    path(
        "surveys/edit/save_temporary/<int:pk>",
        SurveyTemporaryUpdateView.as_view(),
        name="survey-temporary-edit",
    ),
    # アンケート編集(公開済み)
    path(
        "surveys/edit/published/<int:pk>",
        SurveyUpdateView.as_view(),
        name="survey-edit",
    ),
    # 投票作成
    path("votes/create/<int:survey_id>/", VoteCreateView.as_view(), name="vote-create"),
    # 投票詳細
    path("votes/detail/<int:pk>", VoteDetailView.as_view(), name="vote-detail"),
    # 投票削除
    path("votes/delete/<int:pk>", vote_delete, name="vote-delete"),
    # 投票編集
    path(
        "votes/edit/<int:pk>",
        VoteUpdateView.as_view(),
        name="vote-edit",
    ),
    # コメント生成AI機能
    path("api/comment/soften/", soften_comment, name="soften-comment"),
]
