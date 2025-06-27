from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routes.health import router as health_router
from routes.leads import router as leads_router

# NOVAS ROTAS DO ADMIN
from routes.admin import (
    dashboard as admin_dashboard_router,
    importacoes as admin_importacoes_router,
    leads as admin_leads_router,
    enrich as admin_enrich_router
)

settings = get_settings()

app = FastAPI(
    title=settings.api_name,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- libere domínios específicos em produção
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
