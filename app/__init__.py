from .database import engine, get_db
from .models import Base
from .main import app

# Create database tables
Base.metadata.create_all(bind=engine)