from django.urls import path
from SuperAdmin.views import Feedback_view

urlpatterns = [
    path("",Feedback_view, name="home"),
]
