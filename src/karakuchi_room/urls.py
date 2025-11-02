from django.urls import path

from karakuchi_room.views import SurveyListView, SurveyDetailView, SurveyCreateView, SurveyUpdateView

from .views import survey_delete

urlpatterns = [
    # アンケート一覧
    path("surveys/", SurveyListView.as_view(), name="survey-list"),
    
    # アンケート新規作成
    path("surveys/create/", SurveyCreateView.as_view(), name="survey-create"),
    
    # アンケート詳細
    path("surveys/detail/<int:pk>", SurveyDetailView.as_view(), name="survey-detail"),
    
    # アンケート削除
    path("surveys/delete/<int:pk>", survey_delete, name="survey-delete")

]
