from functools import wraps
from flask_login import current_user
from flask import abort

def role_required(*roles):
    """
    A custom decorator to restrict routes to specific user roles.
    Example usage: @role_required('admin', 'librarian')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # If they aren't logged in, or their role isn't in the allowed list, reject them
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403) # Returns a 403 Forbidden HTTP error
            return f(*args, **kwargs)
        return decorated_function
    return decorator