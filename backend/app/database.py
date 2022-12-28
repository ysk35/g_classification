from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URI = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}, echo=True
)

Base = declarative_base()

# 地域テーブルの定義
class Region(Base):
    __tablename__ = 'regions'
    id = Column('id', Integer, primary_key = True)
    name = Column('name', String(200))
    fire = Column('fire', String(200))
    plastic = Column('plastic', String(200))
    nonfire = Column('nonfire', String(200))
    pet = Column('pet', String(200))

class User(Base):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key = True)
    email = Column('email', String(200))
    password = Column('password', String(200))
    area = Column('area', Integer)


# テーブル作成
Base.metadata.create_all(bind=engine)