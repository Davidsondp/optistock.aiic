from fastapi import APIRouter, Depends
from app.modelos.producto import Producto
from app.servicios.ia_inventario import predecir_demanda
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import obtener_usuario_actual

router = APIRouter()

@router.get("/{producto_id}/predecir")
async def predecir_stock(
    producto_id: str,
    usuario: User = Depends(obtener_usuario_actual),
    session: AsyncSession = Depends(get_db)
):
    if usuario.role != "admin":
        raise HTTPException(status_code=403, detail="Solo para admins")
    
    producto = await Producto.obtener(session, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no existe")
    
    demanda = await predecir_demanda(producto.id)
    return {
        "producto": producto.nombre["es"],
        "stock_actual": producto.stock,
        "stock_recomendado": demanda["estimacion"]
    }
