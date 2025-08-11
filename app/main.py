from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user_routes, chat_routes, friend_routes, hobby_routes, gps_routes
from app.database import create_tables, initialize_hobbies
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
        logging.StreamHandler()  # 只記錄到 console
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Near Ride Backend API", version="1.0.0")

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
    logger.info("Starting Near Ride Backend API...")
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Initializing default hobbies data...")
    initialize_hobbies()
    logger.info("API startup completed successfully")

app.include_router(user_routes.router, prefix="/users")
app.include_router(chat_routes.router)
app.include_router(friend_routes.router, prefix="/friends")
app.include_router(hobby_routes.router)
app.include_router(gps_routes.router)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello from Render", "status": "running"}
