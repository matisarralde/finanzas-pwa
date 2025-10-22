# apps/backend/src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import logging

from src.core.config import settings
from src.core.errors import AppException
from src.core.rate_limit import RateLimitMiddleware
from src.api import transactions, budgets, categories, accounts, rules, reports, exports, gmail, health

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Finance API")
    yield
    logger.info("Shutting down Finance API")

app = FastAPI(
    title="Personal Finance API",
    description="API para gestión de finanzas personales con ingesta automática desde Gmail",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)

# Exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code}
    )

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(rules.router, prefix="/rules", tags=["Rules"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
app.include_router(exports.router, prefix="/exports", tags=["Exports"])
app.include_router(gmail.router, prefix="/gmail", tags=["Gmail"])

# Metrics endpoint
@app.get("/metrics", include_in_schema=False)
async def metrics():
    from fastapi.responses import Response
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
