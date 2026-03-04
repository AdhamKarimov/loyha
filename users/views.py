from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework import permissions

from .models import CustomUser
from .serializers import SignUpSerializer
from rest_framework.permissions import AllowAny
# Create your views here.


class SignUpView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer
    queryset = CustomUser

    def get_serializer(self, *args, **kwargs):
        print("🟢 REQUEST.DATA serializerga kelishdan oldin:", kwargs.get('data'))
        return super().get_serializer(*args, **kwargs)