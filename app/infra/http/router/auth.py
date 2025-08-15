from fastapi import APIRouter, Depends, HTTPException, Response

from app.__core__.application.logger import logger
from app.__core__.application.settings import get_settings
from app.__core__.application.use_case.sign_in_use_case import (ISignInUseCase,
                                                                SignInInput,
                                                                SignInOutput)
from app.__core__.application.use_case.sign_up_use_case import (ISignUpUseCase,
                                                                SignUpInput,
                                                                SignUpOutput)
from app.__core__.domain.exception.exception import (AuthenticationError,
                                                     ValidationError)
from app.infra.dependency import get_sign_in_use_case, get_sign_up_use_case
from app.infra.security import validate_api_key

router = APIRouter(
    dependencies=[Depends(validate_api_key)],
)
settings = get_settings()


@router.post("/sign-in", response_model=SignInOutput, status_code=200)
async def sign_in(
    request: SignInInput,
    response: Response,
    sign_in_use_case: ISignInUseCase = Depends(get_sign_in_use_case),
):
    try:
        sign_in_output = await sign_in_use_case.execute(request)

        cookie_max_age = settings.JWT_EXPIRE_DAYS * 24 * 60 * 60
        response.set_cookie(
            key="access_token",
            value=sign_in_output.access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=cookie_max_age,
        )

        return sign_in_output

    except (AuthenticationError, ValidationError) as exc:
        match str(exc):
            case "invalid_credentials":
                raise HTTPException(status_code=401, detail=str(exc))
            case _:
                raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        logger.error("sign_in_failed", exc_info=str(exc))
        raise HTTPException(status_code=500)


@router.post("/sign-up", response_model=SignUpOutput, status_code=201)
async def sign_up(
    request: SignUpInput,
    sign_up_use_case: ISignUpUseCase = Depends(get_sign_up_use_case),
):
    try:
        return await sign_up_use_case.execute(request)

    except (AuthenticationError, ValidationError) as exc:
        match str(exc):
            case "username_already_exists":
                raise HTTPException(status_code=409, detail=str(exc))
            case _:
                raise HTTPException(status_code=422, detail=str(exc))

    except Exception as exc:
        logger.error("sign_up_failed", exc_info=str(exc))
        raise HTTPException(status_code=500)


@router.post("/sign-out", status_code=204)
def sign_out(response: Response):
    try:
        response.delete_cookie(key="access_token")

    except Exception as exc:
        logger.error("sign_out_failed", exc_info=str(exc))
        raise HTTPException(status_code=500)
