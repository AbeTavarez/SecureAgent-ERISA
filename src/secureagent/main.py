
from fastapi import FastAPI

from secureagent.api.crm_api import router

# ====== API ========
app = FastAPI(title="Mock CRM API")
app.include_router(router, prefix='/api/v1')


def run(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    import uvicorn

    uvicorn.run("secureagent.main:app", host=host, port=port, reload=reload)