from django.urls import path
from django.contrib.auth.views import LogoutView

from karakuchi_room.views import MyLoginView

# from karakuchi_room.views import TaskListView, TaskDetailView, TaskCreateView, TaskDeleteView, TaskUpdateView

urlpatterns = [
    path("login/", MyLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout")
    # path("", TaskListView.as_view(), name="surveys")

]
