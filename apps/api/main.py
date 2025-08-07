from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.services.config import get_settings
from apps.api.routes.health import router as health_router
from apps.api.routes.leads_routes import router as leads_router
from apps.api.routes.detetive_routes import router as detetive_router  # ✅ adicionado

from apps.api.routes import admin_routes

settings = get_settings()

app = FastAPI(
    title=settings.api_name,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👇 aqui estão suas rotas registradas
app.include_router(health_router, prefix="/v1")
app.include_router(leads_router, prefix="/v1")
app.include_router(detetive_router)  # ✅ isso habilita a rota do modo detetive
app.include_router(admin_routes.router)
