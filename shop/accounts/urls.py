from django.urls import path
from .views import SignupPageView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('signup/', SignupPageView.as_view(), name='signup'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)