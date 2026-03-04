
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework import serializers,status

from config import settings
from .models import CodeVerify,CustomUser, VIA_EMAIL, VIA_PHONE
from rest_framework.exceptions import ValidationError
from shared.utilis import check_email_or_phone



class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_status = serializers.CharField(read_only=True)
    auth_type = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_or_phone'] = serializers.CharField(write_only=True,required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'auth_status', 'auth_type' ]

    def create(self,validated_data):
        user = super().create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code=user.generate_cod(VIA_EMAIL)
            try:
                send_mail(
                    'Tasdiqlash kodi',
                    f'Sizning kodingiz: {code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                raise ValidationError({"email": f"Xat yuborishda xatolik yuz berdi: {str(e)}"})
        elif user.auth_type == VIA_PHONE:
            code = user.generate_cod(VIA_PHONE)
            print(code,"|||||||||||||||||||||||||||")
        else:
            raise ValidationError('Email yoki telefon raqam xato')
        return user

    def validate(self, attrs):
        super().validate(attrs)
        data = self.auth_validate(attrs)
        return data

    @staticmethod
    def auth_validate(user_input):
        user_input = user_input.get('email_or_phone')
        user_input_type = check_email_or_phone(user_input)
        if user_input_type == 'phone':
            data = {
                'auth_type':VIA_PHONE,
                'phone_number':user_input
            }
        elif user_input_type == 'email':
            data = {
                'auth_type':VIA_EMAIL,
                'email':user_input
            }
        else:
            response = {
                'status': status.HTTP_400_BAD_REQUEST,
                'massage': "Email yoki telefon raqamingiz xato kiritildi"
            }
            raise ValidationError(response)
        return data

    def validate_email_or_phone(self, email_or_phone):
        if CustomUser.objects.filter(Q(phone_number=email_or_phone) | Q(email=email_or_phone)).exists():
            raise ValidationError("Bu email yoki telefon raqam bilan oldin ro'yxatdan o'tilgan")
        return email_or_phone

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['message'] = 'Kodingiz yuborildi'
        data['refresh'] = instance.token()['refresh']
        data['access'] = instance.token()['access']
        return data