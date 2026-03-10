from django.urls import path
from .views import SignUpView , VerifiyCodeVew,UserChangeInfoView


urlpatterns = [
    path('signup/',SignUpView.as_view()),
    path('verify/',VerifiyCodeVew.as_view()),
    path('userchangeinfo/',UserChangeInfoView.as_view())
]