from django.urls import path
from .views import HomePage, ContactsPage, DeliveryPage, RefundPage, PrivacyPage, OfferPage, AboutPage, BuyerPage, PrivaLabPage
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', HomePage, name='home'),
    path('contacts/', ContactsPage, name='contacts'),
    path('delivery/', DeliveryPage, name='delivery'),
    path('refund-exchange/', RefundPage, name='refund'),
    path('privacy-policy/', PrivacyPage, name='privacy'),
    path('public-offer/', OfferPage, name='offer'),
    path('about/', AboutPage, name='about'),
    path('for-buyer/', BuyerPage, name='buyer'),

    path('prive-labaratory/', PrivaLabPage, name='prive-lab')
]

handler404 = 'pages.views.custom_404'

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)