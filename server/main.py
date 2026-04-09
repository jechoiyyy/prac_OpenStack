from fastapi import FastAPI
from app.recovery.router import router as recovery_router

app = FastAPI()

app.include_router(recovery_router, prefix="/recovery", tags=["recovery"])