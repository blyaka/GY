from django.urls import path
from .views import submit_request, submit_contact

app_name = "reqs"
urlpatterns = [
    path("submit/", submit_request, name="submit"),
    path("contact/submit/", submit_contact, name="contact_submit"),
]
