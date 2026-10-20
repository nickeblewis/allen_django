from django.urls import path

from site_pages import views

urlpatterns = [
    path("up", views.up, name="up"),
    path("", views.home, name="home"),
]
