from datetime import datetime, timedelta, UTC
import jwt  # ensure this is the PyJWT library, not your file
from jwt  import PyJWTError
from aistudio.config.config import JWTConfig

# Загружаем конфигурацию JWT из .env
jwt_config = JWTConfig()

SECRET_KEY = jwt_config.JWT_SECRET_KEY
ALGORITHM = jwt_config.JWT_ALGORITHM

# Время жизни токенов из .env
ACCESS_TOKEN_EXPIRE_MINUTES = jwt_config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = jwt_config.REFRESH_TOKEN_EXPIRE_DAYS


def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    """
    Создает access токен с указанным временем жизни.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: int = REFRESH_TOKEN_EXPIRE_DAYS):
    """
    Создает refresh токен с указанным временем жизни.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    """
    Декодирует access токен.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except PyJWTError:
        return None


def decode_refresh_token(token: str):
    """
    Декодирует refresh токен.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except PyJWTError:
        return None


def is_token_expired(token: str, is_refresh: bool = False):
    """
    Проверяет, истек ли токен.
    """
    try:
        if is_refresh:
            payload = decode_refresh_token(token)
        else:
            payload = decode_access_token(token)
        
        if not payload:
            return True
            
        exp = payload.get("exp")
        if not exp:
            return True
            
        # Конвертируем timestamp в datetime
        exp_datetime = datetime.fromtimestamp(exp, UTC)
        return datetime.now(UTC) > exp_datetime
        
    except Exception:
        return True
