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
                conn.close()
            except:
                pass

def initialize_hobbies():
    """初始化興趣愛好數據"""
    from app.models.hobby import Hobby
    
    # 預定義的興趣列表
    default_hobbies = [
        (1, "閱讀", "喜歡透過書籍探索不同世界與觀點"),
        (2, "旅行", "熱愛探索新地方與文化"),
        (3, "烹飪", "享受親手製作美味料理的樂趣"),
        (4, "電影", "喜歡觀賞各類型影片並分享心得"),
        (5, "音樂", "喜愛聆聽或演奏音樂"),
        (6, "攝影", "用相機捕捉生活中的美好瞬間"),
        (7, "健身", "注重健康與身材管理"),
        (8, "瑜伽", "追求身心平衡與放鬆"),
        (9, "跑步", "喜歡挑戰自我、保持活力"),
        (10, "登山", "享受與大自然親近的時光"),
        (11, "游泳", "喜愛水中運動與放鬆"),
        (12, "跳舞", "以舞蹈表達情感與活力"),
        (13, "手作", "喜歡親手製作工藝或飾品"),
        (14, "繪畫", "用顏色與線條表達創意"),
        (15, "桌遊", "喜歡與朋友聚會玩遊戲"),
        (16, "電子遊戲", "享受虛擬世界的冒險"),
        (17, "咖啡", "喜歡品嚐與研究咖啡文化"),
        (18, "品酒", "欣賞紅酒、白酒或調酒的風味"),
        (19, "露營", "喜愛戶外生活與野營體驗"),
        (20, "衝浪", "追求海上刺激與自由感"),
        (21, "潛水", "探索海底世界與生態"),
        (22, "志工服務", "熱心參與公益與幫助他人"),
        (23, "寵物", "喜歡與動物相處"),
        (24, "園藝", "享受種植花草與照顧植物"),
        (25, "美食探索", "喜愛嘗試不同餐廳與料理"),
        (26, "語言學習", "對不同語言與文化有興趣"),
        (27, "攝影棚拍攝", "享受專業拍攝與造型"),
        (28, "汽車", "對車輛與駕駛有熱情"),
        (29, "天文", "喜歡觀星與宇宙探索"),
        (30, "模型製作", "熱愛製作與收藏模型")
    ]
    
    db = SessionLocal()
    try:
        logger.info("Initializing hobbies data...")
        
        # 檢查是否已經有興趣數據
        existing_count = db.query(Hobby).count()
        if existing_count > 0:
            logger.info(f"Hobbies already initialized ({existing_count} hobbies found)")
            return
        
        # 插入預設興趣
        for hobby_id, name, description in default_hobbies:
            # 檢查是否已存在同名興趣
            existing = db.query(Hobby).filter(Hobby.name == name).first()
            if not existing:
                # 先嘗試使用指定的ID
                existing_id = db.query(Hobby).filter(Hobby.id == hobby_id).first()
                if not existing_id:
                    hobby = Hobby(id=hobby_id, name=name, description=description)
                else:
                    # 如果ID已存在，讓數據庫自動分配ID
                    hobby = Hobby(name=name, description=description)
                db.add(hobby)
        
        db.commit()
        
        # 確認插入數量
        final_count = db.query(Hobby).count()
        logger.info(f"Successfully initialized {final_count} hobbies")
        
    except Exception as e:
        logger.error(f"Error initializing hobbies: {e}")
        db.rollback()
    finally:
        db.close()

