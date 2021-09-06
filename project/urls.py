""" Project URL Configuration """
from django.contrib import admin
from django.urls import include, path
from common.views import custom400, custom404


admin.site.site_header = 'PBX'
admin.site.site_title = 'PBX'

handler400 = custom400
handler404 = custom404

urlpatterns = [
    path('', include('django_prometheus.urls')),
    path('fsapi', include('fsapi.urls')),
    path('admin/', admin.site.urls),
]
