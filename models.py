from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"  # Evita conflictos con palabra reservada "user" en PostgreSQL

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), default="empleado", nullable=False)  # admin o empleado

    def __repr__(self):
        return f"<User {self.email} ({self.rol})>"

class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(100))
    unidad = db.Column(db.String(50))
    proveedor = db.Column(db.String(100))
    precio = db.Column(db.Float)

    def __repr__(self):
        return f"<Producto {self.nombre} ({self.cantidad})>"

class Movimiento(db.Model):
    __tablename__ = "movimientos"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # entrada o salida
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    producto = db.relationship('Producto', backref=db.backref('movimientos', lazy=True))

    def __repr__(self):
        return f"<Movimiento {self.tipo} - Producto ID {self.producto_id} ({self.cantidad})>"



