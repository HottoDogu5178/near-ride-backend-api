from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.models import user
import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 正確地從環境變數讀取 DATABASE_URL，否則用 sqlite 作為預設
DATABASE_URL = os.getenv("ostgresql://postgres.ikjyahdimpdadsszmgzg:Xu.6up4u06@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}, isolation_level="AUTOCOMMIT")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

