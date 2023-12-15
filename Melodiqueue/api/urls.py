from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index),
    path('main', views.main),
    path('logout', views.logout_view),
]
