from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('admin/', admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]

urlpatterns += i18n_patterns(
    path('accounts/', include('allauth.urls')),
    path('profile/', include('accounts.urls')),
    path('shop/', include('products.urls')),
    path('blog/', include('blog.urls')),
    path("reqs/", include("reqs.urls", namespace="reqs")),
    path('', include('pages.urls')),

    prefix_default_language=True,
)



from django.contrib.sitemaps.views import sitemap
from .sitemaps import SITEMAPS

urlpatterns += [
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
]



from django.views.generic import TemplateView

urlpatterns += [
    path("robots.txt", TemplateView.as_view(
        template_name="robots.txt", content_type="text/plain"
    )),
]



from django.http import HttpResponse
urlpatterns += [ path("healthz", lambda r: HttpResponse("ok")) ]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)