import re
from rest_framework import status
from rest_framework.exceptions import ValidationError


phone_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
email_regex = re.compile(r'^998([378]{2}|(9[013-57-9]))\d{7}$')

def check_email_or_phone(user_input):
    if re.fullmatch(phone_regex,user_input):
        data = 'phone'
    elif re.fullmatch(email_regex,user_input):
        data = 'email'

    else:
        response = {
            'status':status.HTTP_400_BAD_REQUEST,
            'massage':"Email yoki telefon raqamingiz xato kiritildi"
        }
        raise ValidationError(response)
    return data