from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session
import psycopg2
import time
from .config import settings
from psycopg2.extras import RealDictCursor
#SQLALCHEMY_DATABASE_URL='postgresql://<username:<password>@<ip-address/hostname>/<database-name>'
SQLALCHEMY_DATABASE_URL=f'postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}'
engine=create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

def get_db():
    db: Session=SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''while True:
    try:
        conn=psycopg2.connect(host='localhost',database='fastapi',user='postgres',password='password',cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        
        print("Connecting to database failed")
        print("Error:",error)
        time.sleep(2)'''