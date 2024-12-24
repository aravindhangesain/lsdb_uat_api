from rest_framework import permissions
from lsdb.models import Permission
from lsdb.models import PermittedView

class ConfiguredPermission(permissions.BasePermission):
    """
    Global permission check for "allowed" by configuration.
    """

    def has_permission(self, request, view):
        # django superusers get all access:
        if request.user.is_superuser : return True
        if request.user.is_staff : return True
        if request.user.is_authenticated:
            try:
                # is this a permitted view?
                this = PermittedView.objects.get(name=view.basename)
            except:
                return False
            return request.user.group_set.filter(permission__permission_types__name=request.method,
                permission__permitted_views__name=this)
        return False

class GroupPermission(permissions.BasePermission):
    """
    User object permission based on the object group FK being one of the groups the
    user is a member of.
    """
    def has_object_permission(self, request, view, object):
        return (object.group in request.user.group_set.all())

class IsAdmin(permissions.BasePermission):
    """
    User permission, is the current user a superuser?
    """
    def has_permission(self, request, view):
        return request.user.is_superuser

class IsAdminOrSelf(permissions.BasePermission):
    """
    User permission, is the current user a superuser or editing their own record?
    """
    def has_object_permission(self, request, view, object):
        return request.user.is_superuser or object == request.user

    # def has_object_permission(self, request, view, obj):
    #     # this gets to the object level
    #     if request.user.is_superuser : return True
    #     # print((obj.__class__.__name__).lower())
    #     print(obj)
    #     return self.permtest((obj.__class__.__name__).lower(),request)
    #
    #     # return True
    #
    # def permtest(self, checkit, request):
    #     try:
    #         # is this a permitted view?
    #         this = PermittedView.objects.get(name=checkit)
    #         print(this)
    #     except:
    #         return False
    #         # filter(string_field__in=arrayOfStrings)
    #     user_groups = request.user.group_set.all()
    #     for permission in this.permission_set.all():
    #         if permission.group in user_groups:
    #             print(permission.permission_types.filter(name=request.method))
    #             return permission.permission_types.filter(name=request.method)
    #     print('this siatement is false')
    #     return False
