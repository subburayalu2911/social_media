from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from social_media import settings
from .models import *
from .utils import *

class UserSerializer(serializers.ModelSerializer):
    status_text = serializers.SerializerMethodField(read_only=True)
    gender_text = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Users
        fields= ['id', 'first_name','last_name','email_id','phone_number', 'date_of_birth','status','status_text','profile_image', 'password', 'gender', 'gender_text']


    def get_status_text(self, instance):
        status = instance.status
        status_text = user_status_choices[status][1]
        return status_text

    
    def get_gender_text(self, instance):
        gender_value = instance.gender if instance.gender else 0
        gender_text = user_gender_choices[gender_value][1]
        return gender_text


    def to_representation(self, instance):
        response = super(UserSerializer, self).to_representation(instance)
        response.pop('password')
        if instance.profile_image:
            image_url = f"{settings.MY_DOMAIN}{instance.profile_image.url}".replace('//media', '/media')
            response['profile_image'] = image_url
        return response


    def validate_email_id(self, value):
        if not value:
            raise ValidationError("This field may not be blank.")

        instance = self.instance
        email_id = value.lower()
        if instance:
            user_instance = Users.objects.filter(email_id=email_id).exclude(id=instance.id).first()
        else:
            user_instance = Users.objects.filter(email_id=email_id).first()
        
        if user_instance:
            raise ValidationError("This email id already exist.")
        
        return email_id
    
    def validate_gender(self, value):
        if value:
            if value not in [Male,Female,Custom]:
                raise ValidationError("Please select valid gender.")
        return value 


    def validated_date_of_birth(self, value):
        if value is None:
            raise ValidationError("This field may not be blank.")
        return value


    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not validated_data.get('gender'):
            validated_data['gender'] = 0
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserFriendSerializer(serializers.ModelSerializer):
    friend_name = serializers.SerializerMethodField(read_only=True)
    status_text = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserFriend
        fields= ['id','friend', 'friend_name','status','status_text']
    

    def get_status_text(self, instance):
        status = instance.status
        status_text = user_friend_choices[status][1]
        return status_text

    def get_friend_name(self, instance):
        name = instance.friend.get_full_name
        return name
    
    def to_representation(self, instance):
        response = super(UserFriendSerializer, self).to_representation(instance)
        friend_id = response.pop('friend')
        response['friend_id'] = str(friend_id)
        return response

