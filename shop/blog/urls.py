from django.urls import path
from .views import BlogPage, PostPage
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', BlogPage, name='blog'),
    path('<slug:slug>/', PostPage, name='post'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)