"""dashboard_convoys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('devices', views.devices, name='devices'),
    path('map', views.map, name='map'),
    path('speed-up/(?P<device_id>)\d+/$', views.speed_up, name='speed-up'),
    path('brake/(?P<device_id>)\d+/$', views.brake, name='brake'),
    path('start/(?P<device_id>)\d+/$', views.start, name='start'),
    path('delete-device/(?P<device_id>)\d+/$', views.delete_device, name='delete-device'),
]
