from django.urls import path

from karakuchi_room.views import SurveyListView, SurveyDetailView, SurveyCreateView, SurveyDeleteView, SurveyUpdateView

urlpatterns = [
    # アンケート一覧
    path("surveys/", SurveyListView.as_view(), name="survey-list"),
    
    # アンケート新規作成
    path("surveys/create/", SurveyCreateView.as_view(), name="survey-create"),
    
    # アンケート詳細
    path("surveys/detail/<int:pk>", SurveyDetailView.as_view(), name="survey-detail"),

]
