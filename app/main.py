from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user_routes
from app.database import create_tables

app = FastAPI()

# CORS 設定（允許 Flutter 串接）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 正式上線請改為你的 app 網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 啟動時自動建立資料表
@app.on_event("startup")
def startup():
    create_tables()

app.include_router(user_routes.router, prefix="/users")

@app.get("/")
def read_root():
    return {"message": "Hello from Render"}
