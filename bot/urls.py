from django.urls import path
from . import views

urlpatterns = [
    path('vaishnav-bot/',views.vaishnav_bot,name="vaishnav-bot")
]
