from django.contrib import admin
from django.urls import include, path

from campaigns.views import IndexView

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("campaigns/", include("campaigns.urls", namespace="campaigns")),
    path("users/", include("users.urls", namespace="users")),
]
