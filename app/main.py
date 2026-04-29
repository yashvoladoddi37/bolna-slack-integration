"""FastAPI application entry point"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes import webhooks
from app.utils.logger import setup_logger, log_with_context


logger = setup_logger(__name__, settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up", extra={
        "context": {"environment": settings.environment, "port": settings.port}
    })
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Bolna-Slack Integration",
    description="Sends Slack alerts when Bolna calls end with call ID, agent ID, duration, and transcript",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    log_with_context(
        logger, "info",
        f"Incoming request: {request.method} {request.url.path}",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown",
    )
    response = await call_next(request)
    log_with_context(
        logger, "info",
        f"Request completed: {request.method} {request.url.path}",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round((time.time() - start) * 1000, 2),
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_with_context(
        logger, "error",
        f"Unhandled exception: {exc}",
        method=request.method,
        path=request.url.path,
        error_type=type(exc).__name__,
    )
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal server error"},
    )


app.include_router(webhooks.router)


@app.get("/")
async def root():
    return {
        "service": "Bolna-Slack Integration",
        "version": "1.0.0",
        "status": "running",
        "webhook_endpoint": "/webhook/bolna/call-ended",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bolna-slack-integration"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
