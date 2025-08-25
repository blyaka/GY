from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path('accounts/', include('allauth.urls')),
    path('profile/', include('accounts.urls')),
    path('shop/', include('products.urls')),
    path('blog/', include('blog.urls')),
    path('', include('pages.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



from django.http import HttpResponse
urlpatterns += [ path("healthz", lambda r: HttpResponse("ok")) ]