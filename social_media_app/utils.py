import os
from social_media_app.flags import *
from django.core.exceptions import ValidationError


#user gender
user_gender_choices = (
    (Male,"Male"),
    (Female,"Female"),
    (Custom,"Custom"),
)


#user status
user_status_choices = (
    (In_Active,"In_Active"),
    (Active,"Active"),
    (Deleted,"Deleted"),
)


#user friend status
user_friend_choices = (
    (Sent,"Sent"),
    (Accepted,"Accepted"),
    (Rejected,"Rejected"),
)


def validate_profile_image_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if ext.lower() not in valid_extensions:
        raise ValidationError(
            'Unsupported file extension. Only PNG, JPG, JPEG, file allowed')