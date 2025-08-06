import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def generar_recomendacion(producto, cantidad_actual, promedio_diario):
    prompt = f"""
Eres un asistente de inventario. El producto "{producto}" tiene {cantidad_actual} unidades actuales.
El promedio de salida diaria es {promedio_diario}.
Recomienda si se debe pedir más, cuánto y por qué. Sé breve, claro y profesional.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",  # o gpt-3.5-turbo si usas otro plan
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message["content"]
