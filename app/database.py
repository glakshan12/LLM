from requests import session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
DATABASE_URL = "postgresql+asyncpg://postgres:pass123@localhost:5432/LLM"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()
async def get_db():
    async with SessionLocal() as session:
        try:
           yield session
           await session.commit()
        except Exception:
           await session.rollback()
           raise
        finally:
           await session.close()


