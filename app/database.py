from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 正確地從環境變數讀取 DATABASE_URL，否則用 sqlite 作為預設
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

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
    # 在這裡導入所有模型，避免循環導入
    from app.models import user, hobby, user_status, commute_route, room, chat
    Base.metadata.create_all(bind=engine)

def update_database_schema():
    """
    檢查並更新資料庫結構，確保所有欄位都存在
    這個函數會檢查現有表格並新增缺少的欄位
    """
    import psycopg2
    import re
    
    # 如果是 SQLite，直接使用 create_all
    if "sqlite" in DATABASE_URL:
        create_tables()
        return
    
    # PostgreSQL 的欄位更新
    try:
        # 解析 PostgreSQL 連接字串
        match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
        if not match:
            print("無法解析 DATABASE_URL")
            return
            
        user, password, host, port, dbname = match.groups()
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname
        )
        
        cur = conn.cursor()
        
        # 首先建立基本表格
        create_tables()
        
        # 檢查並新增 users 表格的欄位
        required_columns = {
            'gender': 'VARCHAR(20)',
            'age': 'INTEGER',
            'location': 'VARCHAR(255)'
        }
        
        # 檢查現有欄位
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND table_schema = 'public';
        """)
        existing_columns = [row[0] for row in cur.fetchall()]
        
        # 新增缺少的欄位
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                cur.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type};')
                print(f'已新增 {column_name} 欄位')
        
        conn.commit()
        cur.close()
        conn.close()
        print("資料庫結構更新完成")
        
    except Exception as e:
        print(f"更新資料庫結構時發生錯誤: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

