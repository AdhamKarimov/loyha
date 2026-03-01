import random
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from shared.models import BaseModels
from datetime import datetime,timedelta
from config.settings import EMAIL_EXPIRATION_TIME,PHONE_EXPIRATION_TIME
from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.


ORDINARY_USER,ADMIN,MANAGER = ('ordinary_user','admin','manager')
NEW,CODE_VERIFY,DONE,PHOTO_DONE = ('new','code_verify','done','photo_done')
VIA_EMAIL,VIA_PHONE, = ('via_email','via_phone',)


class CustomUser(BaseModels,AbstractUser):
    USER_ROLE = (
        (ORDINARY_USER,ORDINARY_USER),
        (ADMIN,ADMIN),
        (MANAGER,MANAGER)
    )
    USER_STATUS = (
        (NEW,NEW),
        (CODE_VERIFY,CODE_VERIFY),
        (DONE,DONE),
        (PHOTO_DONE,PHOTO_DONE)
    )
    USER_AUTH_STATUS = (
        (VIA_EMAIL,VIA_EMAIL),
        (VIA_PHONE,VIA_PHONE)
    )
    user_role = models.CharField(max_length=20,choices=USER_ROLE, default=ORDINARY_USER)
    auth_status = models.CharField(max_length=20,choices=USER_AUTH_STATUS, default=NEW)
    auth_type = models.CharField(max_length=20,choices=USER_AUTH_STATUS)
    email = models.EmailField(max_length=100,blank=True,null=True,unique=True)
    phone = models.CharField(max_length=13,blank=True,null=True,unique=True)
    user = models.ImageField(upload_to='/user_photo',validators=[FileExtensionValidator(allowed_extensions=['png','jpg','heic'])])

    def __str__(self):
        return self.username

    def check_username(self):
        if not self.username:
            temp_username = f" username{ uuid.uuid4().__str__().split('-')[-1]}"
            while CustomUser.objects.filter(username=temp_username).filter().exists():
                temp_username += str(random.randint(0,9))
            self.username = temp_username

    def check_pass(self):
        if not self.password:
            temp_password = f"pass{(uuid.uuid4().__str__().split('-')[-1])}"
            self.username = temp_password

    def hashing_pass(self):
        if self.password.startswith('pbkdf2_sha256'):
            self.password = self.set_password(self.password)

    def check_email(self):
        if self.email:
            email_normaliz = self.email.lower()
            self.email = email_normaliz

    def token(self):
        refresh_token = RefreshToken.for_user(self)

        data = {
            'refresh':str(refresh_token),
            'access':str(refresh_token.access_token)
        }
        return data

    def generate_cod(self,verify_type):
        code = ''.join([random.randint(1000,9999)%10 for _ in range(4)])
        CodeVerify.objects.create(
            code=code,
            user=self,
            verify_type=verify_type
        )
        return code



    def clean(self):
        self.check_email()
        self.check_username()
        self.check_pass()
        self.hashing_pass()

    def save(self, force_insert = ...,force_update = ..., using = ..., update_fields = ...):
        self.clean()
        super().save(force_insert,force_update, using, update_fields)


class CodeVerify(BaseModels):
    VERIFY_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )

    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    verify_type = models.CharField(max_length=30,choices=VERIFY_TYPE)
    expiration_time = models.DateTimeField()

    def save(self,*args,**kwargs):
        if self.verify_type == VIA_EMAIL:
            self.expiration_time = datetime.now()+timedelta(minutes=EMAIL_EXPIRATION_TIME)
        else:
            self.expiration_time = datetime.now()+timedelta(minutes=PHONE_EXPIRATION_TIME)

        return super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.user.username} | {self.code}"