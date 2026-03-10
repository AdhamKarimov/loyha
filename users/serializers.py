
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework import serializers,status

from config import settings
from .models import CodeVerify,CustomUser, VIA_EMAIL, VIA_PHONE , CODE_VERIFY,DONE
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
        data['message'] = 'Kodingiz yuborildi Iltimos kodni tasdiqlang'
        return data


class VerifySerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)
    code = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        code = attrs.get('code')
        try:
            user = CustomUser.objects.get(Q(phone_number=email_or_phone) | Q(email=email_or_phone))
        except CustomUser.DoesNotExist:
            raise ValidationError("Foydalanuvchi topilmadi.")

        verify_code = CodeVerify.objects.filter(
            user=user,
            code=code,
        ).order_by('-created_at').first()

        if not verify_code:
            raise ValidationError("Tasdiqlash kodi xato yoki yaroqsiz.")

        user.auth_status = CODE_VERIFY
        user.save()
        attrs['user'] = user
        return attrs

    def to_representation(self, instance):
        user = instance['user']
        return {
            'message': 'Muvaffaqiyatli tasdiqlandi',
            'auth_status': user.auth_status,
            'access': user.token()['access'],
            'refresh': user.token()['refresh'],
        }


class UserChangeInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)

        if password is None or confirm_password is None or password != confirm_password:
            response = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Parollar mos emas yoki xato kiritildi'
            }
            raise ValidationError(response)
        if len([i for i in password if i == ' ']) > 0:
            response = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Parollar xato kiritildi'
            }
            raise ValidationError(response)

        return data

    def validate_username(self, username):
        if len(username) < 6:
            raise ValidationError({'message': 'Username kamida 7 ta bolishi kerak'})
        elif not username.isalnum():
            raise ValidationError({'message': 'Username da ortiqcha belgilar bolmasligi kerak'})
        elif username[0].isdigit():
            raise ValidationError({'message': 'Username raqam bilan boshlanmasin'})
        return username

    def validate_first_name(self,first_name):
        first_name = first_name.strip()
        if not first_name:
            raise serializers.ValidationError("Ism bo'sh bo'lishi mumkin emas.")
        if len(first_name) < 3:
            raise serializers.ValidationError("Ism kamida 3 ta belgidan iborat bo'lishi kerak.")
        if len(first_name) > 50:
            raise serializers.ValidationError("Ism 50 ta belgidan oshmasligi kerak.")
        if not first_name.isalpha():
            raise serializers.ValidationError("Ism faqat harflardan iborat bo'lishi kerak.")
        return first_name.capitalize()

    def validate_last_name(self, last_name):
        last_name = last_name.strip()
        if not last_name:
            raise serializers.ValidationError("Familiya bo'sh bo'lishi mumkin emas.")
        if len(last_name) < 2:
            raise serializers.ValidationError("Familiya kamida 2 ta belgidan iborat bo'lishi kerak.")
        if len(last_name) > 50:
            raise serializers.ValidationError("Familiya 50 ta belgidan oshmasligi kerak.")
        if not last_name.isalpha():
            raise serializers.ValidationError("Familiya faqat harflardan iborat bo'lishi kerak.")
        return last_name.capitalize()

    def update(self, instance, validated_data):
        if instance.auth_status != CODE_VERIFY:
            raise ValidationError({"message": "siz hali tasdiqlanmagansiz ",'status':status.HTTP_400_BAD_REQUEST})
        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.username = validated_data.get('username')
        instance.set_password(validated_data.get('password'))
        instance.auth_status = DONE
        instance.save()
        return instance
