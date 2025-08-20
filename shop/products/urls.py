from django.urls import path
from .views import ShopView, quick_view, ProductDetailView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', ShopView.as_view(), name='shop'),
    path('qv/<int:pk>/', quick_view, name='product_quick_view'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)