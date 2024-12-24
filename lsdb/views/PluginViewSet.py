from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.decorators import action, permission_classes

from lsdb.models import Plugin
from lsdb.serializers import PluginSerializer
from lsdb.permissions import ConfiguredPermission, IsAdmin, GroupPermission
from RestrictedPython import compile_restricted


def _compile(obj):
    # Returns the byte_code object of a plugin
    if obj.restricted == False:  # Let's be very clear here...
        try:
            byte_code = compile(
                obj.source_code,
                filename='<inline code>',
                mode='exec'
            )
        except SyntaxError as e:
            # Return errors here
            return e, None
    else:
        try:
            byte_code = compile_restricted(
                obj.source_code,
                filename='<inline code>',
                mode='exec'
            )
        except SyntaxError as e:
            # Return errors here
            return e, None
    return None, byte_code


class PluginViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Permission to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Plugin.objects.all()
    serializer_class = PluginSerializer
    permission_classes = [ConfiguredPermission]

    # Overriding some of the built-in view methods for permission control:
    # @permission_classes(IsAdmin)
    def create(self, request):
        if request.user.is_superuser:
            return super().create(request)
        else:
            return Response({"Error":"Not Authorized"}, status=status.HTTP_403_FORBIDDEN)
    #
    # @permission_classes([IsAdmin,])
    # def update(self, request, pk=None):
    #     self.super.update()
    #
    # @permission_classes([IsAdmin,])
    # def partial_update(self, request, pk=None):
    #     self.super.partial_update()
    #
    # @permission_classes([IsAdmin,])
    # def destroy(self, request, pk=None):
    #     self.super.destroy()

    @action(detail=True, methods=['get', 'post'],
            serializer_class=PluginSerializer,
            permission_classes=[GroupPermission, ConfiguredPermission, ]
            )
    def compile_plugin(self, request, pk=None):
        # This will compile the code in either restricetd or unrestricted
        # model and then place the byte_code into the database
        self.context = {'request': request}
        obj = Plugin.objects.get(id=pk)
        if request.method == 'POST':
            errors, obj.byte_code = _compile(obj)
            if errors:
                return Response({'Compile': 'failed', "errors": errors})
            else:
                obj.save()
                return Response({'Compile': 'succeeded', "errors": None})
        return Response(self.serializer_class(obj, many=False, context=self.context).data)

    @action(detail=True, methods=['get', 'post'],
            serializer_class=PluginSerializer,
            )
    def test_plugin(self, request, pk=None):
        # Every plugin should be a class with a test() method
        # Unit test, that returns the results of the test as an HTTP response
        self.context = {'request': request}
        to_serialize = request.query_params.get('serialize')
        obj = Plugin.objects.get(id=pk)
        if request.method == 'POST':
            # Commented out for source-only KLUGE below
            # byte_code = obj.byte_code
            # try:
            #     exec(byte_code)
            # except Exception as e:
            #     print(e)
            #     return Response({'Errors':e})
            # KLUGE:
            errors, byte_code = _compile(obj)
            # Your class should be ready now:
            if errors:
                return Response({'test_result': 'failed', "errors": errors})
            else:
                exec(byte_code)
                plugin_class = locals().get(obj.name)
                plugin_instance = plugin_class()
                if 'true' in to_serialize:
                    return Response({'test_result': 'passed', 'output': plugin_instance._test()})
                else:
                    return plugin_instance._test()
        return Response(self.serializer_class(obj, many=False, context=self.context).data)

    @action(detail=True, methods=['get', 'post'],
            serializer_class=PluginSerializer,
            permission_classes=[IsAdmin, ]
            )
    def review_plugin(self, request, pk=None):
        # We don't want to deploy code into production that has not been reviewed
        # This needs to be called by an admin to mark a plugin as approved.
        # Generally other code will load the plugin object and then execute the run()
        if request.method == 'POST':
            pass

    @action(detail=True, methods=['get', 'post'],
            serializer_class=PluginSerializer,
            permission_classes=[GroupPermission, ConfiguredPermission, ]
            )
    def run_plugin(self, request, pk=None):
        """
        This action feeds the data provided to the _run() method of the plugin.
        {
        "key":"value"
        ...
        }
        """
        # This may not be needed or appropriate in all cases.
        # I think what wwe wnt to be able to do is POST a struct
        # and the plugin should chew on the data and return local results.
        # Generally other code will load the plugin object and then execute the run()
        self.context = {'request': request}
        obj = Plugin.objects.get(id=pk)
        to_serialize = request.query_params.get('serialize')
        if request.method == 'POST':
            params = request.data
            # Commented out for source-only KLUGE below
            # byte_code = obj.byte_code
            # try:
            #     exec(byte_code)
            # except Exception as e:
            #     print(e)
            #     return Response({'Errors':e})
            # KLUGE:
            errors, byte_code = _compile(obj)
            # Your class should be ready now:
            if errors:
                return Response({'test_result': 'failed', "errors": errors})
            else:
                exec(byte_code)
                plugin_class = locals().get(obj.name)
                plugin_instance = plugin_class()
                if 'true' in to_serialize:
                    return Response({'test_result': 'passed', 'output': plugin_instance._run(**params)})
                else:
                    return plugin_instance._run(**params)
        return Response(self.serializer_class(obj, many=False, context=self.context).data)

        pass


'''
class PluginTest():
    def __init__(self):
        self.a = 1
        self.b = 2

    def _test(self):
        return(self.a + self.b)

    def _run(self, a=None, b=None):
        return( a + b)

class FieldNull():
    def __init__(self):
        self.a = None

    def _test(self):
        return(self.a == None)

    def _run(self, field=None):
        return( field == None )

class FieldNull():
    def __init__(self):
        self.a = None

    def _test(self):
        return(self.a == None)

    def _run(self, field=None):
        return( field == None )

'''
