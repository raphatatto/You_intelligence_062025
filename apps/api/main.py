from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.services.config import get_settings
from apps.api.routes.health import router as health_router
from apps.api.routes.leads import router as leads_router

# NOVAS ROTAS DO ADMIN
from apps.api.routes.admin_routes import (
    dashboard as admin_dashboard_router,
    importacoes as admin_importacoes_router,
    leads as admin_leads_router,
    enrich as admin_enrich_router,
)

# Configurações globais
settings = get_settings()

# Inicializa o app com nome e versão vindos do .env
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

# Rotas do painel Admin
app.include_router(admin_dashboard_router.router)
app.include_router(admin_importacoes_router.router)
app.include_router(admin_leads_router.router)
app.include_router(admin_enrich_router.router)
