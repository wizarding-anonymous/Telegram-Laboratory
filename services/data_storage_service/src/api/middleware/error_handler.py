# services\data_storage_service\src\api\middleware\error_handler.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

class MigrationException(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)

class DatabaseException(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            logger.error(f"HTTP Exception: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "status_code": exc.status_code},
            )
        except MigrationException as exc:
            logger.error(f"Migration Error: {exc.detail}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Migration error: {exc.detail}", "status_code": 500},
            )
        except DatabaseException as exc:
            logger.error(f"Database Error: {exc.detail}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Database error: {exc.detail}", "status_code": 500},
            )
        except Exception as exc:
            logger.exception("Unhandled Exception")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An internal server error occurred. Please try again later.",
                    "status_code": 500,
                },
            )
