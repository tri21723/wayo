from fastapi import HTTPException


def api_error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status,
        detail={"code": code, "message": message, "details": []},
        headers={"WWW-Authenticate": "Bearer"} if status == 401 else None,
    )
