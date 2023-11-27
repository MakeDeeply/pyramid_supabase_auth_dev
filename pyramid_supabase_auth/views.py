'''
pyramid_supabase_auth sample - Color Chooser

Copyright 2023 by Make Deeply - released under MIT License
'''
import os
import sys

from pyramid.csrf import get_csrf_token, new_csrf_token
from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.response import Response
from pyramid.view import view_config, notfound_view_config, exception_view_config

from .utils import verify_csrf_token

script_folder = os.path.dirname(os.path.abspath(__file__))
if script_folder not in sys.path:
    sys.path.append(script_folder)
import db
import utils


@view_config(route_name='home', renderer='pyramid_supabase_auth:templates/index.jinja2')
def home(request):
    user = request.identity
    fav_color = ''

    if user is not None:
        try:
            fav_color = db.get_user_color(user.id)
        except Exception as e:
            print('home ERROR:', e)

    return {
        'colors': db.colors,
        'colorsTable': db.get_all_users_colors(),
        'fav_color': fav_color,
        'user': user,
        'users': db.get_users(),
    }


@view_config(route_name='profile', renderer='pyramid_supabase_auth:templates/profile.jinja2', require_csrf=False)
def profile(request):
    user = request.identity

    if user is None:
        return HTTPFound(location=request.route_url('login'))

    try:
        fav_color = db.get_user_color(user.id)
    except Exception as e:
        fav_color = None
        print(e)

    if request.method == 'POST':
        verified, token = verify_csrf_token(request)
        if not verified:
            return {
                'error': 'CSRF Token Error',
                'colors': db.colors,
                'your_color': fav_color,
                'token':token
            }
        else:
            color = request.POST['color']
            if color in db.colors:
                try:
                    data = db.set_user_color(user.id, color)
                    fav_color = data[0]['favourite_color']
                    request.session.flash(
                        {
                            'msg': 'Your new Color is %s!' % data[0]['favourite_color'],
                            'type': 'success',
                        }
                    )
                    return HTTPFound(location=request.route_url('profile'))

                except Exception as e:
                    print('profile_view ERROR', e)
                    request.session.flash(
                        {
                            'msg': 'Failed to change your color. Please try again.',
                            'type': 'danger',
                        }
                    )

            else:
                request.session.flash(
                    {'msg': 'Please provide a valid color.', 'type': 'warning'}
                )

    return {'colors': db.colors, 'your_color': fav_color}


@notfound_view_config(renderer='pyramid_supabase_auth:templates/404.jinja2')
def notfound_view(request):
    request.response.status = 404
    return {}


@exception_view_config(HTTPUnauthorized)
def unauthorized_exception_view(exc, request):
    return Response('Unauthorized', status=401)
