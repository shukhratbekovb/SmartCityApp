from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from configs import ASYNC_DATABASE_URL

engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, expire_on_commit=False)
