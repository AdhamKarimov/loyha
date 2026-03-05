from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework import generics, status
from rest_framework.response import Response

from .models import CustomUser
from .serializers import SignUpSerializer , VerifySerializer
from rest_framework.permissions import AllowAny
# Create your views here.


class SignUpView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer
    queryset = CustomUser



class VerifiyCodeVew(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VerifySerializer
    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
