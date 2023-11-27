'''
pyramid_supabase_auth sample - Color Chooser

Copyright 2023 by Make Deeply - released under MIT License
'''
def includeme(config):
    # 'includeme' is a magic name (or could specify urls.anything and then def anything)

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')

    config.add_route('login', '/login')
    config.add_route('register', '/register')
    config.add_route('profile', '/profile')
    config.add_route('logout', '/logout')

    config.add_route('auth', '/auth')
    config.add_route('auth_recover', '/auth/recover')
    config.add_route('oauth_login', '/oauth_login/{provider}')

    config.add_route('forgot_password', '/forgot_password')
    config.add_route('reset_password', '/reset_password')
