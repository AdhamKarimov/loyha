from django.urls import path
from .views import SignUpView , VerifiyCodeVew


urlpatterns = [
    path('signup/',SignUpView.as_view()),
    path('verify/',VerifiyCodeVew.as_view())
]