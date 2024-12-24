from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
)
from rest_framework_tracking.mixins import LoggingMixin

from lsdb.authentication import token_expire_handler, expires_in, token_refresh
from lsdb.permissions import ConfiguredPermission
from lsdb.serializers import ForgotPasswordSerializer
from lsdb.serializers import TokenSigninSerializer
from lsdb.serializers import UserSigninSerializer
from lsdb.utils import Notification
from lsdb.utils.Crypto import encrypt, decrypt


class NoopViewSet(LoggingMixin, viewsets.ViewSet):
    logging_methods = ['GET']
    queryset = User.objects.all()
    permission_classes = [ConfiguredPermission]

    def list(self, request):
        user = request.user
        if not user:
            return Response({'detail': 'Invalid credentials or activate account.'}, status=HTTP_404_NOT_FOUND)

        # TOKEN STUFF
        token, _ = Token.objects.get_or_create(user=user)

        # token_expire_handler will check, if the token is expired it will generate new one
        is_expired, token = token_expire_handler(token)
        # user_serialized = UserSerializer(data=user)
        # print(request.data)
        # if user_serialized.is_valid():
        return Response({
            'user': user.username,
            'id': user.id,
            'expires_in': expires_in(token),
            'token': token.key,
            'build': settings.LSDB_BUILD,
        }, status=HTTP_200_OK)


class SignInViewSet(LoggingMixin, viewsets.ViewSet):
    logging_methods = ['POST']
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def create(self, request):
        signin_serializer = UserSigninSerializer(data=request.data)
        if not signin_serializer.is_valid():
            # bad request or just a token?
            signin_serializer = TokenSigninSerializer(data=request.data)
            if not signin_serializer.is_valid():
                # I have no idea what you're asking
                return Response(signin_serializer.errors, status=HTTP_400_BAD_REQUEST)
            else:
                # we have a token
                original_token = decrypt(signin_serializer.data['token'])
                try:
                    token = Token.objects.get(key=original_token)
                except Token.DoesNotExist:
                    raise AuthenticationFailed("Invalid token.")
                token = token_refresh(token)
                user = User.objects.get(username=token.user)
                # print(user)
        else:
            user = authenticate(
                username=signin_serializer.data['username'],
                password=signin_serializer.data['password']
            )
            # user = User.objects.get(username = user)

        if not user:
            return Response({'detail': 'Invalid credentials or activate account.'}, status=HTTP_404_NOT_FOUND)

        # TOKEN STUFF
        token, _ = Token.objects.get_or_create(user=user)

        # token_expire_handler will check, if the token is expired it will generate new one
        is_expired, token = token_expire_handler(token)
        # user_serialized = UserSerializer(data=user)
        # print(request.data)
        # if user_serialized.is_valid():
        return Response({
            'user': user.username,
            'id': user.id,
            'expires_in': expires_in(token),
            'token': token.key,
            'build': settings.LSDB_BUILD,
        }, status=HTTP_200_OK)


class ForgotPasswordViewSet(LoggingMixin, viewsets.ViewSet):
    logging_methods = ['POST']
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def create(self, request):
        forgot_serializer = ForgotPasswordSerializer(data=request.data)
        if forgot_serializer.is_valid():
            try:
                user = User.objects.get(username=forgot_serializer.data['username'])
            except ObjectDoesNotExist:
                return Response({
                    'status': 'User {0} not found.'.format(forgot_serializer.data['username'])
                }, status=status.HTTP_400_BAD_REQUEST)

            token, _ = Token.objects.get_or_create(user=user)
            note = Notification()

            note.throttled_email(template='reset_password',
                                 user=user,
                                 magic_link=settings.CLIENT_HOST + '/forgot_password/' + encrypt(token))
            return Response({
                'status': 'Password reset link sent to {0}.'.format(user.email),
            }, status=status.HTTP_200_OK)
