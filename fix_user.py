from app import app
from models import db, User

with app.app_context():
    email = "tucorreo@dominio.com"  # <- reemplaza con el correo real
    usuario = User.query.filter_by(email=email).first()
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        print(f"✅ Usuario '{email}' eliminado correctamente.")
    else:
        print("⚠️ Usuario no encontrado.")
