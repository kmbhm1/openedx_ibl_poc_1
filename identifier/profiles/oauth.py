from authlib.integrations.django_client import OAuth
from django.conf import settings

oauth = OAuth()

for key, value in settings.AUTHLIB_OAUTH_CLIENTS.items():
    # This will register the LMS as a client for Authlib.
    # If you added any other providers to the AUTHLIB_OAUTH_CLIENTS
    # settings dictionary, they'll be added, too.
    oauth.register(key, **value)
