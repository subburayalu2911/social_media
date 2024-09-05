from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import uuid
from social_media_app.utils import *



class UsersManager(BaseUserManager):

    def create_user(self, email_id, password=None, **kwargs):
        if not password:
            raise ValueError('Superusers must have password.')
        
        if email_id is None:
            raise ValueError('Members must have an email address.')
        
        user_obj = self.model(email_id=self.normalize_email(email_id),**kwargs)
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_superuser(self, email_id, password=None, **kwargs):
        kwargs.setdefault('is_admin', True)
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superadmin', True)
        return self.create_user(email_id, password, **kwargs)



class Users(AbstractBaseUser):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    email_id = models.EmailField(db_column='Email',max_length=254, unique=True)
    phone_number = models.CharField(db_column='PhoneNumber',max_length=88, blank=True, null=True) 
    first_name = models.CharField(db_column='FirstName', max_length=256, blank=True, null=True) 
    last_name = models.CharField(db_column='LastName', max_length=256, blank=True, null=True) 
    date_of_birth = models.DateField(db_column='DateOfBirth',null=True, blank=True)
    gender = models.PositiveIntegerField(db_column='Gender', blank=True, null=True)
    status = models.PositiveIntegerField(db_column='Status',default=user_status_choices[1][0], blank=True, null=True)
    profile_image = models.ImageField(db_column='UserImage', blank=True, null=True, validators=[validate_profile_image_extension],upload_to='user/profile_image/')

    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    created_by = models.UUIDField(null=True, blank=True)
    created_by_name = models.CharField(max_length=256, null=True, blank=True)
    updated_by = models.UUIDField(null=True, blank=True)
    updated_by_name = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UsersManager() 

    USERNAME_FIELD = 'email_id'
    REQUIRED_FIELDS = ['first_name','last_name']


    def has_perm(self, prem, obj=None):
        return self.is_superadmin
    
    def has_module_perms(self, app_lable):
        return self.is_superadmin

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name if self.last_name else ""}'.strip()

    @property
    def user_image(self):
        image = self.profile_image.url
        if image:
            image_url = image.replace('/media/media/', '/media/')
        else:
            image_url = None
        return image_url
    
    class Meta:
        db_table = 'SM_App_Users'
        indexes = [
                models.Index(fields=["email_id"]),
                models.Index(fields=["first_name","last_name"]),
                models.Index(fields=["first_name"]),
                models.Index(fields=["last_name"]),
                models.Index(fields=["phone_number"]),
            ]



class UserFriend(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, related_name='userfriend_user')
    friend = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, related_name='friend')
    status = models.PositiveIntegerField(default=user_friend_choices[0][0], blank=True, null=True)
    created_by = models.UUIDField(null=True, blank=True)
    created_by_name = models.CharField(max_length=256, null=True, blank=True)
    updated_by = models.UUIDField(null=True, blank=True)
    updated_by_name = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SM_App_UserFriend'
        indexes = [
                models.Index(fields=["status"]),
            ]




