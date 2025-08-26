from django.urls import path
from .views import submit_request

app_name = "reqs"
urlpatterns = [
    path("submit/", submit_request, name="submit"),
]
