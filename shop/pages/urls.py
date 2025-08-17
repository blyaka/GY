from django.urls import path
from .views import HomePage
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', HomePage, name='home'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)