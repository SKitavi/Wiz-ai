# app/main.py
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
import time
import sys

from backend.app.config import settings, get_cors_origins
from backend.app.database import check_db_connection, init_db
from backend.app.services.scheduler import start_scheduler, stop_scheduler

# Import routers
from backend.app.routers import auth
from backend.app.routers import automation
from backend.app.routers import document
from backend.app.routers import tasks
from backend.app.routers import plans


# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
# Ensure logs directory exists before file logging
import os
os.makedirs("logs", exist_ok=True)
logger.add(
    "logs/wizai.log",
    rotation="500 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    level="DEBUG"
)

# Create FastAPI app
app = FastAPI(
    title="WizAI API",
    description="AI-Powered Student Life Organizer - Intelligent Backend System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"➡️  {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        f"⬅️  {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.2f}s"
    )
    
    # Add custom header with processing time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.ENVIRONMENT == "development" else "An error occurred"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 Starting WizAI API...")
    
    # Check database connection
    logger.info("Checking database connection...")
    if check_db_connection():
        logger.info("✅ Database connection successful")
        
        # Initialize database tables
        try:
            init_db()
            logger.info("✅ Database initialized")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
    else:
        logger.error("❌ Database connection failed!")

        # Start background scheduler
        try:
            start_scheduler()
            logger.info("✅ Background scheduler started")
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")

    
    logger.info("✅ WizAI API started successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 Shutting down WizAI API...")
    stop_scheduler()
    logger.info("✅ Background scheduler stopped")


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "healthy",
        "service": "WizAI API",
        "version": "1.0.0",
        "message": "Welcome to WizAI - Your AI-Powered Student Life Organizer"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    db_status = check_db_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "environment": settings.ENVIRONMENT
    }


# Include routers
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

# Additional routers
app.include_router(
    automation.router,
    prefix="/api/automation",
    tags=["Automation"]
)

app.include_router(
    document.router,
    prefix="/api/documents",
    tags=["Documents"]
)

app.include_router(
    tasks.router,
    prefix="/api/tasks",
    tags=["Tasks"]
)

app.include_router(
    plans.router,
    prefix="/api/plans",
    tags=["Plans"]
)

# app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
# app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )
    