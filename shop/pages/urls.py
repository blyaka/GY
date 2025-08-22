from django.urls import path
from .views import HomePage, ContactsPage, DeliveryPage
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', HomePage, name='home'),
    path('contacts/', ContactsPage, name='contacts'),
    path('delivery/', DeliveryPage, name='delivery')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)