from pyramid.config import Configurator

from pyramid.session import SignedCookieSessionFactory

import pyramid_supabase_auth.routes
import pyramid_supabase_auth.security

my_session_factory = SignedCookieSessionFactory('HhiUHOIUbuo8wg2y7u()')

def main(global_config, **settings):
    '''This function returns a Pyramid WSGI application.'''
    with Configurator(settings=settings) as config:
        config.set_session_factory(my_session_factory)
        config.include('pyramid_jinja2')
        config.include(routes)
        config.include(security)
        config.scan()

    return config.make_wsgi_app()
