from django.urls import path
from . import views

urlpatterns = [
    path('vaishnav-bot/',views.vaishnav_bot,name="vaishnav-bot"),
    path('submit-feedback/',views.submit_feedback,name="submit-feedback"),
]
