from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.config import get_settings
from apps.api.routes import health  # rotas já criadas abaixo

settings = get_settings()

app = FastAPI(
    title=settings.api_name,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS – apenas internos por enquanto
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # restrinja depois
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar blueprints
app.include_router(health.router, prefix="/v1")
