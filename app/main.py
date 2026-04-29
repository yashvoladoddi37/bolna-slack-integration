"""FastAPI application entry point"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from app.config import settings
from app.routes import webhooks
from app.utils.logger import setup_logger, log_with_context


logger = setup_logger(__name__, settings.log_level)

# Create FastAPI application
app = FastAPI(
    title="Bolna-Slack Integration",
    description="Sends Slack alerts when Bolna calls end with call details and transcript",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all HTTP requests with timing
    
    Args:
        request: HTTP request
        call_next: Next middleware/route handler
    
    Returns:
        HTTP response
    """
    start_time = time.time()
    
    # Log incoming request
    log_with_context(
        logger, "info",
        f"Incoming request: {request.method} {request.url.path}",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Log response
    log_with_context(
        logger, "info",
        f"Request completed: {request.method} {request.url.path}",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2)
    )
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors
    
    Args:
        request: HTTP request
        exc: Exception that was raised
    
    Returns:
        JSON error response
    """
    log_with_context(
        logger, "error",
        f"Unhandled exception: {str(exc)}",
        method=request.method,
        path=request.url.path,
        error=str(exc),
        error_type=type(exc).__name__
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if settings.environment == "development" else "An error occurred"
        }
    )


# Include routers
app.include_router(webhooks.router)


@app.get("/")
async def root():
    """
    Root endpoint with service information
    
    Returns:
        Service information
    """
    return {
        "service": "Bolna-Slack Integration",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "webhook": "/webhook/bolna/call-ended",
            "health": "/webhook/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "bolna-slack-integration",
        "environment": settings.environment
    }


@app.on_event("startup")
async def startup_event():
    """Application startup event handler"""
    logger.info(
        "Application starting up",
        extra={
            "context": {
                "environment": settings.environment,
                "port": settings.port,
                "log_level": settings.log_level
            }
        }
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler"""
    logger.info("Application shutting down")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )

# Made with Bob
