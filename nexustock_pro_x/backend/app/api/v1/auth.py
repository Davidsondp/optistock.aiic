from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "tu_clave_secreta_chilena_2024"
ALGORITHM = "HS256"

class User(BaseModel):
    username: str
    role: str  # "admin", "manager", "user"

def crear_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return User(**payload)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.post("/login")
async def login(username: str, password: str):
    # Aquí validarías contra tu base de datos
    if username == "admin" and password == "clave":
        token = crear_token({"sub": username, "role": "admin"}, timedelta(minutes=30))
        return {"access_token": token}
    raise HTTPException(status_code=400, detail="Credenciales incorrectas")
