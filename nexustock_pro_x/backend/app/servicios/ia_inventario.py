import numpy as np
from datetime import datetime

async def predecir_demanda(producto_id: str):
    # Modelo simplificado (reemplazar con PyTorch/TensorFlow)
    historico = [100, 120, 90, 110]  # Datos de ejemplo
    prediccion = np.mean(historico) * 1.2  # Lógica de ejemplo
    
    return {
        "producto_id": producto_id,
        "estimacion": round(prediccion, 2),
        "fecha": datetime.now().strftime("%Y-%m-%d")
    }
