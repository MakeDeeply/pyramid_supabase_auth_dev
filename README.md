```
pyramid_supabase_auth sample - Color Chooser

Copyright 2023 by Make Deeply - released under MIT License
```

pyramid_supabase_auth
=====================

Purpose
---------------
We're looking for feedback on the best way to integrate Supabase auth (both email and OAUTH providers) into an existing Pyramid web app.

To make the discussion tangible, we created this trivial 'Color Chooser' app. The project was started awhile back and created by people with no prior Supabase experience, so may not be up-to-date or otherwise 'best practice'. Let us know!

MIT License, so have at it! Pull requests welcome.

Questions
---------------

- Any feedback on our approach to auth, either for Supabase or the framework?
- We're not security experts by any stretch. Anything else we missed? Any improvements we should consider?
- For Pyramid in general: any 'best practice' suggestions?

Getting Started
---------------

- Create (or navigate to) a parent folder in the desired location, then change directory into it.

    `mkdir dev`
    `cd dev`

- Create a Python virtual environment (e.g. 'supenv'), if not already created. This should be outside of the folder that's in git.

    `python3 -m venv supenv`

- Activate it

    `source supenv/bin/activate`

- Change directory to the project folder that contains setup.py and README.md

    `cd pyramid_supabase_auth_dev`

- Upgrade packaging tools, if necessary.

    `pip install --upgrade pip setuptools`

- Install the project in editable mode

    `pip install -e .`

- Run the project in dev mode with flag to reload if files are changed

    `pserve development.ini --reload`


Requires
--------------

local_settings.py with:

```
settings = {
	'SUPABASE_URL': '...',
	'SUPABASE_KEY': '...',
	}
```

(or update db.py to use environment variables, and set those in your environment)


Supabase setup
--------------------
In Supabase go to Authentication > Settings > Auth Providers

Enable each of the following:

- Discord: https://supabase.com/docs/guides/auth/auth-discord
- Github: https://supabase.com/docs/guides/auth/auth-github
- Google: https://supabase.com/docs/guides/auth/auth-google
