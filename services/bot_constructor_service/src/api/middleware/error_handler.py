# services\bot_constructor_service\src\api\middleware\error_handler.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

class ErrorHandlerMiddleware:
    """
    Middleware for handling exceptions and returning structured error responses.
    """

    async def __call__(self, request: Request, call_next):
        """
        Middleware entry point to catch and handle exceptions.

        Args:
            request (Request): The incoming HTTP request.
            call_next (function): The next middleware or endpoint handler.

        Returns:
            JSONResponse: Structured error response in case of an exception.
        """
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            logger.error(f"HTTP Exception: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "status_code": exc.status_code},
            )
        except Exception as exc:
            logger.exception("Unhandled Exception")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An internal server error occurred.",
                    "status_code": 500,
                },
            )
