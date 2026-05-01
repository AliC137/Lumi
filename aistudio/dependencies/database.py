from fastapi import Depends, HTTPException, status
from aistudio.utils.jwt_utils import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from aistudio.core.database import get_db

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Получает текущего пользователя из JWT токена.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return payload
