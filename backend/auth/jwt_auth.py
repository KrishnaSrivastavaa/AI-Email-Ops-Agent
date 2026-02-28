from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from fastapi import Cookie, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

SECRET_KEY = "super-secret"
ALGORITHM = "HS256"

security = HTTPBearer()

def create_access_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        print("RAW TOKEN:", access_token)
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        print("DECODED PAYLOAD:", payload)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401)

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    print("User Found:", user)
    if not user:
        raise HTTPException(status_code=401)

    return user
