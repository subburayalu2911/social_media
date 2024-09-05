from datetime import timedelta, datetime
from django.utils import timezone
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import *
from rest_framework import status
from django.db.models import Q, Value
from rest_framework.pagination import PageNumberPagination
from django.db.models.functions import Concat
from django.db import transaction

# Create your views here.


class StandardResultSetPagination(PageNumberPagination):
    """
    Here we can get the datas in pagination format.
    """
    page_size = 10
    page_size_query_param = 'pageSize'

    # max_page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'per_page': self.page_size,
            'page': self.page.number,
            'total': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'data': data
        })


class UserManagement(APIView):
    """
    Here we can manage the user details based on the methods
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        if user_id:
            """
            Here we can get the single user details
            """
            user_data = Users.objects.filter(id=user_id, status=Active).first()
            if not user_data:
                return Response({'msg': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
            response = UserSerializer(user_data).data
            return Response(response, status=status.HTTP_200_OK)
        else:
            """
            Here we can get the all users list who are not as a friend to login user.
            """
            user_id = request.auth.get('user_id')
            search = request.GET.get('search')

            get_friends_id = UserFriend.objects.filter(Q(user_id=user_id) | Q(friend_id=user_id)).filter(status=Accepted)
            
            friends_id = []

            with transaction.atomic():
                for friend in get_friends_id.all():
                    if str(user_id) == str(friend.friend_id):
                        friends_id.append(str(friend.user_id))
                    else:
                        friends_id.append(str(friend.friend_id))

            users = Users.objects.filter(status=Active).exclude(id=user_id).exclude(id__in=friends_id).order_by('created_at').annotate(
                fullnamespace=Concat('first_name', Value(' '), 'last_name')).annotate(
                fullname=Concat('first_name', 'last_name'))

            if search:
                users = users.filter(Q(email_id=search) | Q(
                    fullnamespace__icontains=search) | Q(fullname__icontains=search))

            paginator = StandardResultSetPagination()
            paginated_user = paginator.paginate_queryset(users, request)
            user_serializer_data = UserSerializer(
                paginated_user, many=True).data
            return paginator.get_paginated_response(user_serializer_data)

    def patch(self, request, user_id):
        """
        In this function we can partially update the single user detail
        """
        user_data = Users.objects.filter(id=user_id, status=Active).first()

        if not user_data:
            return Response({'msg': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

        password = request.data.get('password')
        if password:
            return Response({'msg': "User can't update password here"}, status=status.HTTP_400_BAD_REQUEST)

        user_serializer = UserSerializer(
            user_data, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'msg': 'User details Updated Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        """
        In this function, user can delete their own account.
        """
        user_data = Users.objects.filter(id=user_id, status=Active).first()
        if not user_data:
            return Response({'msg': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        if user_data.status == Active:
            user_data.status = Deleted
            user_data.save()
            return Response({'msg': 'User Deleted Successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def login(request):
    """
    User can login and generate a token against the user
    """
    if request.method == 'POST':
        data = request.data
        email_id = data.get('email_id')
        password = data.get('password')
        error = {}

        if not email_id:
            error['email_id'] = 'Please enter a valid email'

        if not password:
            error['password'] = 'Please enter a valid password'

        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        user_authenticate = authenticate(
            email_id=email_id.lower(), password=password)
        if user_authenticate:
            if user_authenticate.status == Active:
                token_response = generate_token(user_authenticate)
                return Response(token_response, status=status.HTTP_200_OK)
            elif user_authenticate.status == In_Active:
                return Response({'msg': 'In Active User, Please contact Admin Team'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'msg': 'Deleted User, Please contact Admin Team'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': 'Invalid Username or Password'}, status=status.HTTP_401_UNAUTHORIZED)


def generate_token(user):
    """
    In this function generate a token against the given user
    """
    token = RefreshToken.for_user(user)
    token.access_token.set_exp(from_time=None, lifetime=timedelta(days=365))
    token.set_exp(from_time=None, lifetime=timedelta(days=367))
    token_items = {}
    data = UserSerializer(user).data
    token_items.update(data)
    for item in token_items:
        RefreshToken.__setitem__(token, item, token_items[item])

    responce_token = {}
    responce_token['access_token'] = str(token.access_token)
    responce_token['refresh_token'] = str(token)
    responce_token['token_items'] = token_items
    return responce_token


@api_view(['POST'])
def register_user(request):
    """
    Here we create a new user
    """
    if request.method == 'POST':
        data = request.data
        email_id = data.get('email_id')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        error = {}
        if not email_id:
            error['email_id'] = 'Email Id is required'

        if not password:
            error['password'] = 'password is required'

        if not confirm_password:
            error['confirm password'] = 'confirm password is required'

        if password != confirm_password:
            error['password'] = 'Password Mismatched.'

        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        first_name = email_id.split('@')[0]
        user_data = UserSerializer(data={
            'first_name': first_name,
            'email_id': email_id.lower(),
            'password': password,
            'status': Active,
        })
        if user_data.is_valid():
            user_data.save()
            return Response({'msg': 'User Registered Successfully'}, status=status.HTTP_200_OK)

        else:
            return Response({'msg': user_data.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_friend_request(request):
    user_id = request.auth['user_id']

    if request.method == 'POST':
        """
        Here we can send a request to particular friend
        """
        data = request.data
        friend_id = data.get('friend_id')
        error = {}

        user = Users.objects.get(id=user_id, status=Active)

        if not user:
            error['friend_id'] = "Your Account does not Active, You Can't send a request."

        if not friend_id:
            error['friend_id'] = 'Please enter a friend ID'

        if str(user_id) == str(friend_id):
            error['friend_id'] = "You can't send a request to yourself."

        friend_data = Users.objects.filter(id=friend_id, status=Active).first()

        if not friend_data:
            error['friend_id'] = 'Please enter a valid friend ID'
        
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_requests_count = UserFriend.objects.filter(
                                    user=user, created_at__gte=one_minute_ago
                                ).count()

        if recent_requests_count >= 3:
            error['msg'] = 'You can only send 3 friend requests per minute.'

        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        friend_request_check = UserFriend.objects.filter(Q(user=user, friend=friend_data) |
                                                         Q(friend=user, user=friend_data)).first()

        if not friend_request_check:
            create_friend_request = UserFriend.objects.create(created_at=timezone.now(),
                user=user, friend=friend_data, status=Sent)
            return Response({'msg': 'Request Send Successfully'}, status=status.HTTP_200_OK)
        else:
            if friend_request_check.status == Sent:
                error['msg'] = 'Request Already Sent'

            if friend_request_check.status == Accepted:
                error['msg'] = 'Already Accepted, Cannot Send request again.'

            if error:
                return Response(error, status=status.HTTP_400_BAD_REQUEST)

            if friend_request_check.status == Rejected:
                friend_request_check.status = Sent
                friend_request_check.save()
                return Response({'msg': 'Friend Request Send Successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def friends_list_screen_based(request):
    """
    Here we get the friends list for the authenticated user based on the screen.
    """
    user_id = request.auth['user_id']

    if request.method == 'GET':
        for_screen = request.GET.get('for_screen')
        search = request.GET.get('search')

        friends_data = UserFriend.objects.filter(Q(user_id=user_id) | Q(friend_id=user_id)).order_by('created_at').annotate(
            fullnamespace=Concat('friend__first_name', Value(' '), 'friend__last_name')).annotate(
            fullname=Concat('friend__first_name', 'friend__last_name'))

        if search:
            friends_data = friends_data.filter(
                Q(fullnamespace__icontains=search) | Q(fullname__icontains=search))

        if for_screen == 'sent':
            friends_data = friends_data.filter(status=Sent)
            paginator = StandardResultSetPagination()
            paginated_user = paginator.paginate_queryset(friends_data, request)
            user_serializer_data = UserFriendSerializer(
                paginated_user, many=True).data
            response = paginator.get_paginated_response(user_serializer_data)
            return response
        else:
            friends_data = friends_data.filter(status=Accepted)
            
            accepted_friend_list = []

            for friend in friends_data:
                if str(user_id) == str(friend.friend.id):
                    friend_dict = {
                        'id': str(friend.id),
                        'friend_name': friend.user.get_full_name,
                        'friend_id': str(friend.user.id),
                        'status': friend.status,
                        'status_text': user_friend_choices[friend.status][1],
                    }
                    accepted_friend_list.append(friend_dict)
                else:
                    friend_dict = {
                        'id': str(friend.id),
                        'friend_name': friend.friend.get_full_name,
                        'friend_id': str(friend.friend.id),
                        'status': friend.status,
                        'status_text': user_friend_choices[friend.status][1],
                    }
                    accepted_friend_list.append(friend_dict)


            paginator = StandardResultSetPagination()
            paginated_user = paginator.paginate_queryset(friends_data, request)
            response = paginator.get_paginated_response(accepted_friend_list)
            return response

            


        


class requested_friends_management(APIView):
    """
    Here we can get the requested friends list against the user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.auth['user_id']

        requested_user_list = UserFriend.objects.filter(
            friend_id=user_id, status=Sent)

        paginator = StandardResultSetPagination()
        paginated_user_list = paginator.paginate_queryset(
            requested_user_list, request)

        requested_user_data = []

        for requested_user in paginated_user_list:
            friend_dict = {
                'id': requested_user.id,
                'friend_id': str(requested_user.user.id),
                'friend_name': requested_user.user.get_full_name,
                'friend_image': f"{settings.MY_DOMAIN}{requested_user.user.profile_image.url}".replace('//media', '/media') if requested_user.user.profile_image else None
            }
            requested_user_data.append(friend_dict)

        response = paginator.get_paginated_response(requested_user_data)

        return response

    def post(self, request):
        user_id = request.auth['user_id']
        friend_id = request.data.get('friend_id')
        type_of_manage = request.data.get('type_of_manage')

        error = {}

        if not friend_id or friend_id == '':
            error['friend_id']= 'Please provide friend ID'

        if not type_of_manage:
            error['type_of_manage']= 'This Field may not be null'

        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        friend_data = Users.objects.filter(id=friend_id, status=Active).first()

        if not friend_data:
            error['msg']= 'Please provide valid friend ID'
            
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request_data = UserFriend.objects.filter(user=friend_data, friend_id=user_id).first()

        if not friend_request_data:
            error['msg']= 'There was no request from this friend'
        
        if type_of_manage not in ['accept', 'reject']:
            error['msg']= 'Please provide valid type of manage'
        
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
        status_type = Accepted if type_of_manage == 'accept' else Rejected
        status_type_text = user_friend_choices[status_type][1]
        
        if friend_request_data.status == Sent:
            friend_request_data.status = status_type
            friend_request_data.save()
            return Response({'msg': f'{status_type_text} Successfully'}, status=status.HTTP_200_OK)
        else:
            status_text = user_friend_choices[friend_request_data.status][1]
            return Response({'msg': f'Already request {status_text}'}, status=status.HTTP_400_BAD_REQUEST)
