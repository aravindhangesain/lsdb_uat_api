from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
)
from rest_framework_tracking.mixins import LoggingMixin

from lsdb.authentication import expires_in, token_refresh
from lsdb.models import Group, Template
from lsdb.models import Note
from lsdb.permissions import ConfiguredPermission, IsAdminOrSelf, IsAdmin
from lsdb.serializers import InviteUserSerializer
from lsdb.serializers import LostPasswordSerializer
from lsdb.serializers import NoteSerializer
from lsdb.serializers import PasswordSerializer
from lsdb.serializers import UserSerializer, TemplateSerializer
from lsdb.serializers.UserSerializer import EditUserSerializer
from lsdb.utils import Notification
from lsdb.utils.Crypto import encrypt


class UserFilter(filters.FilterSet):
    # projects =
    groups = filters.NumberFilter(method='filter_by_custom_group')

    def filter_by_custom_group(self, queryset, name, value):
        """
        Custom filter to get all users linked to the given group ID.
        """
        try:
            group = Group.objects.get(id=value)
            user_ids = group.users.values_list('id', flat=True)
            return queryset.filter(id__in=user_ids)
        except Group.DoesNotExist:
            return queryset.none()
        
    class Meta:
        model = User
        fields = {
            'email': ['exact', 'icontains'],
            'username': ['exact', 'icontains'],
            'is_active': ['exact'],
            'groups': ['exact']
        }


class UserViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows User to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [ConfiguredPermission]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAdminOrSelf])
    @transaction.atomic
    def edit(self, request, pk=None):
        """
        This action allows a user to edit its own properties, restricting editing to only the allowed fields:

        POST:
        {
            first_name: "",
            last_name: "",
            password: "",
            subscriptions: [IDs],
        }
        """

        self.context = {'request': request}

        user = User.objects.get(pk=pk)

        if request.method == 'POST':
            updated_user_data = request.data
            input_serializer = EditUserSerializer(data=updated_user_data)
            

            if input_serializer.is_valid():
                user.first_name = updated_user_data.get('first_name', user.first_name)
                user.last_name = updated_user_data.get('last_name', user.last_name)

                user.save()
            else:
                return Response({"error": input_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EditUserSerializer(instance=user, context=self.context)

        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAdminOrSelf])
    @transaction.atomic
    def set_allowed_templates(self, request, pk=None):
        """
        This action will set a user's allowed templates list to the list sent
        POST:
        {
            "templates": [IDs]
        }
        """

        self.context = {'request': request}

        user = User.objects.get(pk=pk)

        current_set = []
        for template_id in user.userprofile.allowed_templates.all().values('id'):
            current_set.append(template_id.get('id'))

        if request.method == 'POST':
            params = request.data
            incoming_templates = params.get('templates')

            for template in current_set:
                if template not in incoming_templates:
                    user.userprofile.allowed_templates.remove(Template.objects.get(pk=template))

            for template in incoming_templates:
                if template not in current_set:
                    user.userprofile.allowed_templates.add(Template.objects.get(pk=template))

            return Response(UserSerializer(user, many=False, context=self.context).data)
        else:
            return Response({'available_templates': TemplateSerializer(Template.objects.all(), many=True,
                                                                       context=self.context).data})

    @action(detail=True, methods=['get', 'post'],
            permission_classes=[IsAdmin])
    @transaction.atomic
    def set_groups(self, request, pk=None):
        """
        This action will set a user's group membership to the list sent.
        POST:
        {
            "groups":[ID,ID,ID]
        }
        """
        self.context = {'request': request}
        user = User.objects.get(id=pk)
        current_set = []
        for id in user.group_set.all().values('id'):
            current_set.append(id.get('id'))
        if request.method == 'POST':
            params = request.data
            incoming_list = params.get('groups')
            # If there's an id in current_set that's not in the list:
            #    nuke it
            # If there's an id in the list that is not in current set:
            #    add it
            for group in current_set:
                if group not in incoming_list:
                    user.group_set.remove(Group.objects.get(id=group))
            for group in incoming_list:
                if group not in current_set:
                    user.group_set.add(Group.objects.get(id=group))
            return Response(UserSerializer(user, many=False, context=self.context).data)
        else:
            # GET:
            return Response([])

    @action(detail=True, methods=['post'],
            permission_classes=(IsAdminOrSelf,),
            serializer_class=PasswordSerializer)
    def set_password(self, request, pk=None):
        self.context = {'request': request}
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.data.get('old_password')):
                return Response({'old_password': ['Wrong password.']},
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            request.user.set_password(serializer.data.get('new_password'))
            request.user.save()
            token, _ = Token.objects.get_or_create(user=request.user)
            token = token_refresh(token)
            return Response({
                'status': 'Password set.',
                'token': token.key
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'],
            permission_classes=(IsAdminOrSelf,),
            serializer_class=PasswordSerializer)
    def token_refresh(self, request, pk=None):
        """
        This action requires any POST, the content will be ignored.
        GET will return the current token and expiration. POST will refresh the token.
        """
        self.context = {'request': request}
        token, _ = Token.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            token = token_refresh(token)
        return Response({
            'user': request.user.username,
            'id': request.user.id,
            'expires_in': expires_in(token),
            'token': token.key,
            'build': settings.LSDB_BUILD,
        }, status=HTTP_200_OK)

    @action(detail=True, methods=['post'],
            permission_classes=(AllowAny,),
            serializer_class=LostPasswordSerializer)
    def lost_password(self, request, pk=None):
        self.context = {'request': request}
        serializer = LostPasswordSerializer(data=request.data)
        if serializer.is_valid():
            # if not request.user.check_password(serializer.data.get('old_password')):
            #     return Response({'old_password': ['Wrong password.']},
            #                     status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            request.user.set_password(serializer.data.get('new_password'))
            request.user.save()
            token, _ = Token.objects.get_or_create(user=request.user)
            token = token_refresh(token)
            return Response({
                'status': 'Password set.',
                'token': token.key
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=(IsAdmin,),
            serializer_class=InviteUserSerializer)
    def invite_user(self, request, pk=None):
        user = User.objects.get(pk=pk)
        self.context = {'request': request}
        serializer = InviteUserSerializer(data=request.data)
        # Probably should use a permission class here
        if serializer.is_valid():
            if request.user.is_superuser:
                invite = username = serializer.data.get('username')
                if invite != user.username:
                    return Response({
                        'status': 'invitation failed. User {0} must match {1}.'.format(
                            invite, user.username
                        )
                    }, status=status.HTTP_400_BAD_REQUEST)

                token, _ = Token.objects.get_or_create(user=user)
                note = Notification()
                note.throttled_email(template='account_create',
                                     user=user,
                                     user_name=user.username,
                                     magic_link=settings.CLIENT_HOST + '/forgot_password/' + encrypt(token))
                return Response({
                    'status': 'Invitation link sent to {0}.'.format(user.email, ),
                }, status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['get'],
            permission_classes=(ConfiguredPermission,),
            serializer_class=NoteSerializer
            )
    def my_notes(self, request, pk=None):
        """
        This action returns all notes owned or tagged by the currently logged in user.
        """
        self.context = {"request": request}
        notes = Note.objects.filter(Q(owner=request.user) | Q(tagged_users=request.user) | Q(user=request.user.id))
        notes = notes.exclude(parent_note__isnull=False)
        closed = request.query_params.get('closed', 'FALSE')
        if closed.upper() == 'TRUE':
            notes = notes.filter(disposition__complete=True).distinct()
        else:
            notes = notes.filter(Q(disposition__complete=False) | Q(disposition__isnull=True)).distinct()
        serializer = self.serializer_class(notes, many=True, context=self.context)
        return Response(serializer.data)
