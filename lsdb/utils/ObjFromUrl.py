import urllib.parse
from django.urls import resolve

def obj_from_url(url):
    path = urllib.parse.urlparse(url).path
    resolved_func, unused_args, resolved_kwargs = resolve(path)
    return resolved_func.cls().get_queryset().get(id=resolved_kwargs['pk'])
