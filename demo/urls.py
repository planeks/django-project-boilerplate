from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.views.generic import TemplateView


admin.site.site_header = 'Admin console'

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('apps.core.urls')),
    # path('select2/', include('django_select2.urls')),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]


# For debug mode only
if settings.DEBUG:
    # Turn on debug toolbar
    import debug_toolbar
    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    # Serve media files via Django
    import django.views.static
    urlpatterns += [
        re_path(r'media/(?P<path>.*)$',
            django.views.static.serve, {
                'document_root': settings.MEDIA_ROOT,
                'show_indexes': True,
            }),
    ]