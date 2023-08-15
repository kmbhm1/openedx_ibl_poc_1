import datetime
import json
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

from profiles.oauth import oauth

from .models import Greeting


class SingletonClass(object):
    TOKEN_INFO = {}
    EXIRATION = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonClass, cls).__new__(cls)
        return cls.instance


def login(request):
    # build a full authorize callback uri
    redirect_uri = request.build_absolute_uri('/authorize/')
    return oauth.lms.authorize_redirect(request, redirect_uri)


def authorize(request):
    # This will create a http request client that points to the LMS.
    lms = oauth.create_client('lms')

    # Here, we authenticate the client with the token we got from the LMS. In a real-world
    # application, we'd save this token somehow for subsequent requests.
    token = lms.authorize_access_token(request)
    if not bool(SingletonClass().TOKEN_INFO) or \
        (SingletonClass().TOKEN_INFO['access_token'] != token['access_token'] and
         datetime.datetime.now() < SingletonClass().EXIRATION):
        SingletonClass().TOKEN_INFO = token
        SingletonClass().EXIRATION = datetime.datetime.now() + datetime.timedelta(seconds=token['expires_in'])

    # And then, we use this token to fetch the user's info.
    resp = lms.get('/api/user/v1/me', token=token)
    resp.raise_for_status()
    profile = resp.json()

    # Now that we have the user's info, we can render a page with the relevant info.
    return render(request, 'authorize.html', {
        'token': SingletonClass().TOKEN_INFO,
        'profile': profile,
    })


def greeting(request):

    # Authenticate
    try:
        auth_code = request.headers['Authorization'].replace("Bearer ", "").strip()
    except KeyError:
        return HttpResponse(json.dumps({'message': 'Authorization header is missing'}), content_type='application/json')
    except Exception:
        return HttpResponse(json.dumps({'message': 'Something went wrong'}), content_type='application/json')

    if not bool(SingletonClass().TOKEN_INFO) or (
            SingletonClass().TOKEN_INFO['access_token'] != auth_code and
            datetime.datetime.now() < SingletonClass().EXIRATION):
        return HttpResponse(json.dumps({'message': 'Token is invalid'}), content_type='application/json')
    elif datetime.datetime.now() > SingletonClass().EXIRATION and \
            SingletonClass().TOKEN_INFO['access_token'] == auth_code:
        return HttpResponse(json.dumps({'message': 'Token is expired. Login again.'}), content_type='application/json')
    
    # Register greeting
    if not request.GET.get('text'):
        return HttpResponse(json.dumps({'message': 'Text is missing in parameter.'}), content_type='application/json')
    
    if request.GET.get("text").lower().replace('"', '') == 'hello':
        new_req = request.GET.copy()
        new_req["text"] = "goodbye"
        request.GET = new_req
        return greeting(request)
    else:

        g = Greeting.objects.create(
            text=request.GET.get('text'),
        )

        return HttpResponse(json.dumps({'message': str(g)}), content_type='application/json')
