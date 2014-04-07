from django.contrib.auth.models import User, check_password
from registration.backends import default
from registration import signals
from registration.forms import RegistrationForm
from registration.models import RegistrationProfile
from django.conf import settings
from django.contrib.sites.models import RequestSite, Site

class Backend(default.DefaultBackend):
    def register(self, request, **kwargs):
        email, password = kwargs['email'], kwargs['password1']
        username = email
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(username, email, password, site)
        signals.user_registered.send(sender=self.__class__,user=new_user, request=request)
        return new_user

# class EmailAuthBackend(object):
    # """
    # for email authentication instead of username
    # """
    
    # def authenticate(self, username=None, password=None):
        # try:
            # user = User.objects.get(email=username)
            # if user.check_password(password):
                # return user
        # except User.DoesNotExist:
            # return None
            
    # def get_user(self, user_id):
        # try:
            # return User.objects.get(pk=user_id)
        # except User.DoesNotExist:
            # return None
