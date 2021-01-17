from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .views import router

origins = [
    "http://localhost:3000",
    # TODO: add hosts
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["link"],
)
app.add_middleware(GZipMiddleware)

app.include_router(router, prefix="/v1")
