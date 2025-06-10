import time
from fastapi import Request
import structlog

logger = structlog.get_logger()

class LoggingMiddleware:
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            "request_started",
            method=request.method,
            url=str(request.url),
            client_host=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            logger.info(
                "request_completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration=time.time() - start_time
            )
            
            return response
            
        except Exception as e:
            # Log error
            logger.error(
                "request_failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                duration=time.time() - start_time
            )
            raise 