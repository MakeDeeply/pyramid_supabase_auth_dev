'''
pyramid_supabase_auth sample - Color Chooser

Copyright 2023 by Make Deeply - released under MIT License
'''
from pyramid.authentication import AuthTktCookieHelper
from pyramid.csrf import CookieCSRFStoragePolicy
from pyramid.request import RequestLocalCache

# local
from .db import supabase


class MySecurityPolicy:
    def __init__(self, secret):
        self.authtkt = AuthTktCookieHelper(secret)
        self.identity_cache = RequestLocalCache(self.load_identity)

    def load_identity(self, request):
        identity = self.authtkt.identify(request)
        if identity is None:
            return None

        userid = identity['userid']

        try:
            user = supabase.auth.admin.get_user_by_id(userid).user
        except Exception as e:
            user = None

        return user

    def identity(self, request):
        return self.identity_cache.get_or_create(request)

    def authenticated_userid(self, request):
        try:
            user = supabase.auth.admin.get_user_by_id(self.identity(request))
        except Exception as e:
            user = None
        if user is not None:
            return user

    def remember(self, request, userid, **kw):
        return self.authtkt.remember(request, userid, **kw)

    def forget(self, request, **kw):
        return self.authtkt.forget(request, **kw)


def includeme(config):
    # 'includeme' is a magic name (or could specify urls.anything and then def anything)
    settings = config.get_settings()

    config.set_csrf_storage_policy(CookieCSRFStoragePolicy())
    config.set_default_csrf_options(require_csrf=True)

    config.set_security_policy(MySecurityPolicy(settings['auth.secret']))
