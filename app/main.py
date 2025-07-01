from fastapi import FastAPI
from app.routers import users

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, world!"}

app.include_router(users.router)
