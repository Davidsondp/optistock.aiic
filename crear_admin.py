from app import db
from app.models import User
from werkzeug.security import generate_password_hash

def crear_admin():
    email = "admin@optistock.com"
    password = "admin123"

    if User.query.filter_by(email=email).first():
        print("⚠️  El usuario ya existe.")
        return

    admin = User(
        email=email,
        password=generate_password_hash(password, method="pbkdf2:sha256", salt_length=8),
        rol="admin"
    )

    db.session.add(admin)
    db.session.commit()
    print("✅ Usuario administrador creado correctamente.")

if __name__ == "__main__":
    crear_admin()
