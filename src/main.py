
from fastapi import FastAPI

from tools.crm_api import router

# ====== API ========
app = FastAPI(tile="Mock CRM API")
app.include_router(router, prefix='/api/v1')