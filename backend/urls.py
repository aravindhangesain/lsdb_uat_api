"""tutorial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from backend.schema import schema, flags_schema, module_intake_schema, module_intake_grid_schema, customer_schema, crate_schema, active_projects_schema, assign_units_schema,work_order_schema


urlpatterns = [
    path('api/1.0/', include('lsdb.urls')),
    path("graphql/",csrf_exempt(GraphQLView.as_view(graphiql=settings.DEBUG, schema=schema)),),
    path("graphql/flags/",csrf_exempt(GraphQLView.as_view(graphiql=True, schema=flags_schema)),),
    path("graphql/moduleintake/details/",csrf_exempt(GraphQLView.as_view(graphiql=True, schema=module_intake_grid_schema)),),
    path("graphql/module-intake/",csrf_exempt(GraphQLView.as_view(graphiql=True,schema=module_intake_schema)),),
    path("graphql/customers/",csrf_exempt(GraphQLView.as_view(graphiql=True, schema=customer_schema)),),
    path("graphql/crate_intakes/",csrf_exempt(GraphQLView.as_view(graphiql=True, schema=crate_schema)),),
    path("graphql/active-projects/",csrf_exempt(GraphQLView.as_view(graphiql=True, schema=active_projects_schema)),),
    path("graphql/assign_units",csrf_exempt(GraphQLView.as_view(graphiql=True, schema=assign_units_schema)),),
    path("graphql/work_order/",csrf_exempt(GraphQLView.as_view(graphiql=True, schema=work_order_schema)),),
    # For later versions:
    # path('api/2.0/', include('lsdb.urls2')),
]

if settings.DEBUG:
    urlpatterns.append(path('admin/', admin.site.urls))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
