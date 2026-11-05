from functools import wraps
from flask import abort,redirect,url_for

def login_required(role=None):
    def decorate(view):
        @wraps(view)
        def wrapped(*args,**kwargs):
            from .auth import get_current_user
            user=get_current_user()
            if user is None:
                return redirect(url_for("auth.login"))
            if role and user["role"]!=role:
                abort(403)
            return view(*args,**kwargs)
        return wrapped
    return decorate
