from django.urls import path
from .views import SignUpView , VerifiyCodeVew,UserChangeInfoView,UserPhotoChangeView,LoginView


urlpatterns = [
    path('signup/',SignUpView.as_view()),
    path('verify/',VerifiyCodeVew.as_view()),
    path('userchangeinfo/',UserChangeInfoView.as_view()),
    path('userchangephoto/',UserPhotoChangeView.as_view()),
    path('login/',LoginView.as_view())
]