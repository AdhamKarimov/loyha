from django.db.models import Q
from rest_framework import serializers,status
from .models import CodeVerify,CustomUser, VIA_EMAIL, VIA_PHONE
from rest_framework.exceptions import ValidationError
from shared.utilis import check_email_or_phone



class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_status = serializers.CharField(read_only=True)
    verify_type = serializers.CharField(read_only=True)

    def __init__(self,instance=None,data=...,**kwargs):
        super().__init__(instance,data,**kwargs)
        self.fields['email_or_phone']= serializers.CharField(write_only=True,required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'auth_status', 'verify_type',]

    def validate(self, attrs):
        print(attrs,"///////////////////")
        super().validate(attrs)
        print(attrs,"+++++++++++++++++++++++")
        data = self.auth_validate(attrs)
        return data

    @staticmethod
    def auth_validate(user_input):
        print(user_input,"______________________")
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

    def validate_email_or_phone(self,email_or_phone):
        user = CustomUser.objects.filter(Q(phone_number=email_or_phone)|Q(email=email_or_phone))
        if user:
            raise ValidationError(detail="Bu email yoki telefon raqam bilan oldin ro'yxatdan o'tgan")
