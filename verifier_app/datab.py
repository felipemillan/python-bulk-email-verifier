from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'sqlite:///../database.db', convert_unicode=True,
    pool_recycle=3600, poolclass=QueuePool
)

Session = sessionmaker(autocommit=True, autoflush=False, bind=engine)
db_session = Session()