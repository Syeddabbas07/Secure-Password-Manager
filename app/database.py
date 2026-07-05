from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///password_manager.db"

engine = create_engine(DATABASE_URL)