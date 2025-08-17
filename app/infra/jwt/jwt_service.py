from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TypedDict

import jwt
from fastapi import HTTPException

from app.__core__.application.gateways.jwt_service import IJWTService
from app.__core__.application.settings import get_settings

settings = get_settings()

TokenPayload = TypedDict("TokenPayload", {"sub": str})


class JWTService(IJWTService):
    ALGORITHM = "HS256"

    def create_token(self, customer_id: str) -> str:
        expire_at = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_EXPIRE_DAYS
        )
        return jwt.encode(
            {
                "sub": customer_id,
                "exp": expire_at,
            },
            settings.JWT_SECRET_KEY,
            algorithm=self.ALGORITHM,
        )

    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[self.ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="token_expired")
        except Exception:
            raise HTTPException(status_code=401, detail="invalid_token")
