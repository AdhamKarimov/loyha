from rest_framework.generics import CreateAPIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import SignUpSerializer , VerifySerializer,UserChangeInfoSerializer,UserPhontoStatisSerializer,LoginSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView


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



class UserChangeInfoView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = UserChangeInfoSerializer(instance=request.user,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': status.HTTP_200_OK,
                'message': "Siz muvofaqqiyatli ro'yxatdan o'tdingiz",
            })
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'Xato',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserPhotoChangeView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self,request):
        user=request.user
        serializer = UserPhontoStatisSerializer(data = request.data, partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=user,validated_data= serializer.validated_data)
        return Response({
            'message':"rasm qo'shildi",
            'status': status.HTTP_200_OK,
            'access': user.token()['access'],
            'refresh': user.token()['refresh'],
        })



class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
