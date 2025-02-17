# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from v1 import lamp

app = FastAPI()

# Allow all origins for local testing.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lamp.router, prefix="/api/v1")
