import uvicorn
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health_router
from app.core import settings

logging.basicConfig()

app = FastAPI()
app.include_router(health_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL
        if settings.FRONTEND_URL
        else "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
