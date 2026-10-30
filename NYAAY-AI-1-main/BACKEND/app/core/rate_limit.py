from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

def get_user_id(request: Request) -> str:
    # If using Firebase Auth middleware, user is in request.state.user
    if hasattr(request.state, "user") and request.state.user:
        return request.state.user.get("uid", get_remote_address(request))
    return get_remote_address(request)

limiter = Limiter(key_func=get_user_id)
