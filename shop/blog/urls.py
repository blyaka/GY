from django.urls import path
from .views import BlogView, PostPage
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', BlogView.as_view(), name='blog'),
    path('<slug:slug>/', PostPage, name='post'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)