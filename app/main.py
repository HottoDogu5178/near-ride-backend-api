from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user_routes, chat_routes, friend_routes, hobby_routes
from app.database import create_tables
import app.models.chat  # ← 加這行才會建立 chat_messages 表
import app.models.user_status  # ← 加這行才會建立 user_status 表
import app.models.hobby  # ← 加這行才會建立 hobbies 表
import app.models.commute_route  # ← 加這行才會建立 commute_routes 表
import logging

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # 記錄到檔案
        logging.StreamHandler()  # 記錄到 console
    ]
)

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
app.include_router(chat_routes.router)
app.include_router(friend_routes.router, prefix="/friends")
app.include_router(hobby_routes.router)

@app.get("/")
def read_root():
    return {"message": "Hello from Render"}
