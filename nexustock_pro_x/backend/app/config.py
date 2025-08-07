from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.api.v1.auth import router as auth_router
from app.api.v1.productos import router as productos_router

app = FastAPI(title="NexuStock Pro X")

# Conexión a DB
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/nexustock"
engine = create_async_engine(DATABASE_URL)

# Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(productos_router, prefix="/api/v1")

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
