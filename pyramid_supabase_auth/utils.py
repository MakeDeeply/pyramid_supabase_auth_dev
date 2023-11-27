import types

from pyramid.exceptions import BadCSRFToken
from pyramid.csrf import check_csrf_token, get_csrf_token, new_csrf_token


def verify_csrf_token(request):
    try:
        check_csrf_token(request)
        return (True, get_csrf_token(request))
    except BadCSRFToken:
        token = new_csrf_token(request)
        request.session.flash(
            {'msg': 'Bad CSRF TOKEN ERROR. Try again.', 'type': 'danger'}
        )
        return (False, token)


def request_to_dict(request, verbose=False):
    request_dict = {}

    for attr_name in dir(request):
        if attr_name.startswith('_'):
            continue

        try:
            attr_value = getattr(request, attr_name)
            if isinstance(attr_value, types.MethodType):
                continue

            if verbose:
                print()
                print(f'• {attr_name} {type(attr_value)} = {attr_value}')
            request_dict[attr_name] = attr_value
        except Exception as e:
            # print this independent of 'verbose'
            print(f'ERROR in {attr_name}', e)

    if verbose:
        print()
    return request_dict


def compare(dict1, dict2, verbose=True):
    diff_dict = {}
    mismatched_fields = []

    keys = sorted(set(list(dict1.keys()) + list(dict2.keys())))

    for key in keys:
        # distinguish 'exists with no value' from 'not in the dict'
        if key in dict1:
            value1 = dict1.get(key)
        else:
            value1 = (
                'NO SUCH FIELD'  # this is arbitrary and could be an actual value...
            )

        if key in dict2:
            value2 = dict2.get(key)
        else:
            value2 = (
                'NO SUCH FIELD'  # this is arbitrary and could be an actual value...
            )

        # I rarely care about this distinction
        if value1 is None:
            value1 = ''
        if value2 is None:
            value2 = ''

        # actual comparison
        if value1 != value2:
            mismatched_fields.append(key)

            if type(value1) == type(value2):
                typestring = type(
                    value1
                ).__name__  # .__name__ to turn type into a string without angle brackets, <type 'unicode'> etc.
            else:
                typestring = 'types: %s vs. %s' % (
                    type(value1).__name__,
                    type(value2).__name__,
                )

            diff_dict[key] = (value1, value2, typestring)

            if verbose:
                print('%s: "%s" vs. "%s"; %s' % (key, value1, value2, typestring))

            # else: the caller might use pretty_print or custom formatting

    if mismatched_fields and (set(keys) == set(mismatched_fields)):
        print()
        print('NONE of these fields matched:', ', '.join(keys))
        print()
    elif mismatched_fields:
        print()
        print('fields that did NOT match:', ', '.join(mismatched_fields))
        print()
    else:
        print()
        print('all checked fields match')
        print()

    return diff_dict
