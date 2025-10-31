from django.urls import path

from karakuchi_room.views import SurveyListView, SurveyDetailView, SurveyCreateView, SurveyDeleteView, SurveyUpdateView

urlpatterns = [
    path("surveys/", SurveyListView.as_view(), name="survey-list"),
    path("surveys/create/", SurveyCreateView.as_view(), name="survey-create")

]
