from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'sqlite:///database.db', convert_unicode=True,
    pool_recycle=3600, poolclass=QueuePool
)

db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))