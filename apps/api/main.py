from fastapi import FastAPI
from apps.api.routes import router

app = FastAPI(title="Youon Intelligence API")

app.include_router(router)