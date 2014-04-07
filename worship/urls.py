from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views as auth_views
admin.autodiscover()

from worship.views import hello, current_datetime, hours_ahead, display_meta
from songs import views

urlpatterns = patterns('',
    (r'^%s' % settings.BASE_URL, include('songs.urls')),
)
