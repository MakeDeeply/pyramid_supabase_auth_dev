'''
pyramid_supabase_auth sample - Color Chooser

Copyright 2023 by Make Deeply - released under MIT License
'''
from pyramid.csrf import new_csrf_token
from pyramid.httpexceptions import HTTPSeeOther, HTTPFound
from pyramid.security import (
    remember,
    forget,
)

from pyramid.view import (
    forbidden_view_config,
    view_config,
)

from gotrue.types import (
    SignInWithEmailAndPasswordCredentials,
    SignInWithOAuthCredentials,
    SignUpWithEmailAndPasswordCredentials,
    Options,
)

# local
from .db import supabase
from .utils import verify_csrf_token


@view_config(
    route_name='login',
    renderer='pyramid_supabase_auth:templates/login.jinja2',
    require_csrf=False,
)
def login(request):
    if request.identity is not None:
        return HTTPSeeOther(request.route_url('home'))

    next_url = request.params.get('next', request.referrer)
    if not next_url:
        next_url = request.route_url('home')

    if request.method == 'POST':
        verified, token = verify_csrf_token(request)
        if not verified:
            return {'error': 'Bad CSRF Token Error', 'token': token}

        try:
            signInCred = SignInWithEmailAndPasswordCredentials(
                email=str(request.POST['email']), password=str(request.POST['password'])
            )

            sess = supabase.auth.sign_in_with_password(signInCred).session
            user_token = sess.access_token
            refresh_token = sess.refresh_token
            user_id = sess.user.id

            if user_token is not None and user_id is not None:
                request.response.set_cookie('access_token', user_token)
                request.response.set_cookie('refresh_token', refresh_token)

                new_csrf_token(request)
                headers = remember(request, user_id)
                request.response.headerlist.extend(headers)
                request.session.flash({'msg': 'Login Successful!', 'type': 'success'})

                headers = request.response.headers
                return HTTPSeeOther(location=next_url, headers=headers)

        except Exception as e:
            print(e)
            request.session.flash(
                {'msg': 'Failed to Login. Please try again.', 'type': 'danger'}
            )
            return {'error': 'Wrong Email Or Password'}

    return {'url': request.route_url('login'), 'next_url': next_url}


@view_config(route_name='logout')
def logout(request):
    next_url = request.route_url('home')

    try:
        request.response.delete_cookie('access_token')
        request.response.delete_cookie('refresh_token')
        headers = forget(request)
        request.response.headerlist.extend(headers)
        supabase.auth.sign_out()
        request.session.flash({'msg': 'You are now logged out.', 'type': 'warning'})

        headers = request.response.headers
        return HTTPSeeOther(location=next_url, headers=headers)

    except Exception as e:
        print(e)
        request.session.flash(
            {'msg': 'Failed to Logout. Please try again.', 'type': 'danger'}
        )
        return HTTPSeeOther(location=next_url)


@view_config(route_name='oauth_login')
def oauth_login(request):
    provider = request.matchdict['provider']
    sign_in_with_oauth = supabase.auth.sign_in_with_oauth({'provider':provider, 'options':{'redirect_to':request.route_url('auth')}})
    url = sign_in_with_oauth.url
    headers = request.response.headers
    return HTTPFound(location=str(url), headers=headers)


@view_config(route_name='auth')
def auth_(request):
    code = request.params.get('code')

    if code is not None:
        new_csrf_token(request)
        try:
            session = supabase.auth.exchange_code_for_session({'auth_code': code})
            user_id = session.user.id
            request.response.set_cookie('access_token', session.session.access_token)
            request.response.set_cookie('refresh_token', session.session.refresh_token)
        except Exception as e:
            print(e)
            request.session.flash(
                {'msg': 'Failed to Login. Please try again.', 'type': 'danger'}
            )
            url = request.route_url('login')
            return HTTPSeeOther(url)

        remember_headers = remember(request, user_id)
        request.response.headerlist.extend(remember_headers)
        headers = request.response.headerlist
        url = request.route_url('home')
        request.session.flash({'msg': 'Login successful!', 'type': 'success'})

        return HTTPFound(location=url, headers=headers)
    else:
        request.session.flash(
            {'msg': 'Failed to Login. Please try again.', 'type': 'danger'}
        )
        url = request.route_url('login')

        print('\n', 'auth_ FAILED: HTTPSeeOther', url)  # TBD: log
        return HTTPSeeOther(url)


@view_config(
    route_name='reset_password',
    renderer='pyramid_supabase_auth:templates/reset_password.jinja2',
    require_csrf=False,
)
def reset_password(request):
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token')

    if request.identity is None:
        return HTTPFound(location=request.route_url('login'))

    if request.method == 'POST':
        if not verify_csrf_token(request):
            return {'error': 'Bad CSRF Token Error'}
        password = request.POST['password']

        try:
            # set session so we can update the user password
            supabase.auth.set_session(access_token, refresh_token)

            supabase.auth.update_user(attributes={'password': password})
            request.session.flash(
                {'msg': 'Password Successfully updated!', 'type': 'success'}
            )
            return HTTPFound(location=request.route_url('home'))

        except Exception as e:
            print(e)
            request.session.flash(
                {'msg': 'Something went Wrong please try again', 'type': 'danger'}
            )
            return {'error':'Your Password Must Be different From Your Previous One And More Than 6 Characters Long'}

    return {}


@view_config(
    route_name='forgot_password',
    renderer='pyramid_supabase_auth:templates/forgot_password.jinja2',
    require_csrf=False,
)
def forgot_password(request):
    if request.method == 'POST':
        verified, token = verify_csrf_token(request)
        if not verified:
            return {'error': 'Bad CSRF Token Error', 'token': token}

        email = request.POST['email']
        url = request.route_url('login')

        try:
            opts = Options(redirect_to=url)
            supabase.auth.reset_password_email(email=email, options=opts)

            request.session.flash(
                {'msg': 'Please check your email and reset your password.', 'type': 'warning'}
            )
            return HTTPFound(location=request.route_url('home'))

        except Exception as e:
            print(e)
            request.session.flash(
                {'msg': 'Failed to send reset link please try again.', 'type': 'danger'}
            )
            return {'error': 'Make sure you provided the correct email'}

    return {}


@view_config(
    route_name='register',
    renderer='pyramid_supabase_auth:templates/register.jinja2',
    require_csrf=False,
)
def register(request):
    if request.identity is not None:
        return HTTPFound(location=request.route_url('home'))

    if request.method != 'POST':
        return {}

    verified, token = verify_csrf_token(request)
    if not verified:
        return {'error': 'Bad CSRF Token Error', 'token': token}
    email = request.POST['email']
    password = request.POST['password']

    try:
        creds = SignUpWithEmailAndPasswordCredentials(email=email, password=password)
        supabase.auth.sign_up(creds)
        request.session.flash({'msg': 'Welcome to Color Chooser', 'type': 'success'})
        return HTTPFound(request.route_url('login'))

    except Exception as e:
        print(e)
        request.session.flash(
            {'msg': 'Failed to register. Please try again.', 'type': 'danger'}
        )
        return {
            'error': 'Failed to register. Make sure this email is not already being used and the password length is 6 or more characters.'
        }


@view_config(route_name='auth_recover')
def auth_recover(request):
    token_hash = request.params.get('token_hash')
    auth_type = request.params.get('type')

    if token_hash and auth_type:
        try:
            auth_response = supabase.auth.verify_otp(params={'token_hash': token_hash, 'type': auth_type})
            user = auth_response.user
            user_id = user.id

            sess = supabase.auth.get_session()
            access_token = sess.access_token
            refresh_token = sess.refresh_token

            request.response.set_cookie('access_token', access_token)
            request.response.set_cookie('refresh_token', refresh_token)

            remember_headers = remember(request, user_id)

            request.response.headerlist.extend(remember_headers)

            headers = request.response.headerlist

            request.session.flash({'msg': 'Please set a new Password.', 'type': 'warning'})
            return HTTPSeeOther(location = request.route_url('reset_password'), headers=headers)

        except Exception as e:
            print(e)
            request.session.flash({'msg': 'Failed to verify token. Please try again.', 'type': 'danger'})
            return HTTPSeeOther(location=request.route_url('forgot_password'))

    request.session.flash({'msg': 'Error, Please try again.', 'type': 'danger'})
    return HTTPSeeOther(location=request.route_url('home'))


@forbidden_view_config(renderer='pyramid_supabase_auth:templates/403.jinja2')
def forbidden_view(exc, request):
    if not request.is_authenticated:
        next_url = request.route_url('login', _query={'next': request.url})

        print('\n', 'forbidden_view: HTTPSeeOther', next_url, '\n')  # TBD: log
        return HTTPSeeOther(location=next_url)

    request.response.status = 403
    return {}
