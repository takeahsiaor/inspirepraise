from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views as auth_views

admin.autodiscover()

from rest_framework import routers

from songs import views
from worship.views import hello, current_datetime, hours_ahead, display_meta


router = routers.DefaultRouter()
router.register(r'songs', views.SongViewSet, base_name='song')
router.register(r'verses', views.VerseViewSet, base_name='verse')

urlpatterns = patterns('',
    (r'^%s' % settings.BASE_URL, include('songs.urls')),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
