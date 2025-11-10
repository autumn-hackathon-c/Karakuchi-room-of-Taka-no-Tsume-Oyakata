from django.urls import path

from django.contrib.auth.views import LogoutView
from .views import survey_delete

from karakuchi_room.views import MyLoginView, SignUpView

from karakuchi_room.views import (
    SurveyListView,
    SurveyDetailView,
    SurveyCreateView,
    SurveyTemporaryUpdateView,
    SurveyUpdateView,
    VoteCreateView,
    VoteDetailView
)


urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", MyLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # path("surveys/", SurveyListView.as_view(), name="survey-list"),
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
]
