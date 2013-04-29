from flask import g, request, redirect, url_for

from functools import wraps
from random import choice
from string import digits, letters


def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if g.user is not None:
            return f(*args, **kwargs)
        return redirect(url_for('frontend.login', next_url=request.url))
    return decorator


def random_alphanum(size):
    return ''.join(choice(digits + letters) for i in range(size))
