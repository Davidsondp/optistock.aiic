import httpx
from datetime import datetime
from app.modelos.moneda import Moneda

async def actualizar_tasas():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.bcentral.cl/v1/tasas")
        data = response.json()
        
        tasas = {
            "CLP_USD": data["dolar"]["valor"],
            "HTG_USD": data["gourde"]["valor"]  # API hipotética
        }
        
        for par, tasa in tasas.items():
            await Moneda.actualizar_tasa(par, tasa)
