from django.urls import path
from . import views

urlpatterns = [
    path('vaishnav-bot/',views.vaishnav_bot,name="vaishnav-bot"),
    path('submit-feedback/',views.submit_feedback,name="submit-feedback"),
    path('send-otp/', views.send_otp, name="send_otp"),
    path('verify-otp/', views.verify_otp, name="verify_otp"),
    path('logout/', views.logout_user, name="logout"),
    path('get-history/', views.get_history, name="get_history"),
]
