from sqlalchemy import Column, String, Numeric, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()
engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/nexustock")

class Producto(Base):
    __tablename__ = "productos"

    id = Column(String, primary_key=True)
    nombre = Column(JSON)  # {"es": "Producto", "ht": "Pwodwi"}
    precio_clp = Column(Numeric(12, 2))
    precio_usd = Column(Numeric(12, 2))
    stock = Column(Numeric(10, 2))

    @classmethod
    async def obtener(cls, session: AsyncSession, producto_id: str):
        result = await session.execute(
            select(cls).where(cls.id == producto_id)
        return result.scalars().first()
