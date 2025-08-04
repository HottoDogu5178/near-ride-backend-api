from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

# 設定 logger
logger = logging.getLogger(__name__)

# 載入 .env 檔案（如果 python-dotenv 可用）
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Successfully loaded .env file")
except ImportError:
    # 如果沒有 python-dotenv，跳過載入 .env
    logger.warning("python-dotenv not available, skipping .env file loading")
    pass

# 正確地從環境變數讀取 DATABASE_URL，否則用 sqlite 作為預設
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
logger.info(f"Database URL configured: {'PostgreSQL' if 'postgresql' in DATABASE_URL else 'SQLite'}")

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
    from app.models import user, hobby, user_status, commute_route, room, chat, gps_route
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def update_database_schema():
    """
    檢查並更新資料庫結構，確保所有欄位都存在
    這個函數會檢查現有表格並新增缺少的欄位
    """
    import psycopg2
    import re
    
    # 如果是 SQLite，直接使用 create_all
    if "sqlite" in DATABASE_URL:
        logger.info("Using SQLite database, creating tables...")
        create_tables()
        return
    
    # PostgreSQL 的欄位更新
    conn = None
    try:
        logger.info("Updating PostgreSQL database schema...")
        # 解析 PostgreSQL 連接字串
        match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
        if not match:
            logger.error("Unable to parse DATABASE_URL")
            return
            
        user, password, host, port, dbname = match.groups()
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname
        )
        conn_created = True
        
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
                logger.info(f'Added column {column_name} to users table')
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Database schema update completed successfully")
        
    except Exception as e:
        logger.error(f"Error updating database schema: {e}")
        if conn is not None:
            try:
                conn.rollback()
                conn.close()
            except:
                pass

