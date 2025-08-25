from django.urls import path
from .views import PersonalAccountPage, ProfileEditView, FavoriteListView, favorite_toggle_api
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', PersonalAccountPage, name='lk'),
    path("edit/", ProfileEditView.as_view(), name="lk_edit"),
    path('favorites/', FavoriteListView.as_view(), name='favorites'),
    path('favorites/toggle/', favorite_toggle_api, name='toggle_fv'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)