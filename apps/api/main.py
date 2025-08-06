from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.services.config import get_settings
from apps.api.routes.health import router as health_router
from apps.api.routes.leads_routes import router as leads_router
from apps.api.routes.analise_routes import router as analise_router

# ✅ ROTAS ADMIN TODAS EM UM ÚNICO ARQUIVO
from apps.api.routes import admin_routes

# Configurações globais
settings = get_settings()

app = FastAPI(
    title=settings.api_name,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS liberado (ajuste para produção!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas públicas
app.include_router(health_router, prefix="/v1")
app.include_router(leads_router, prefix="/v1")
app.include_router(analise_router, prefix="/v1")

# Rotas do painel Admin
app.include_router(admin_routes.router)
