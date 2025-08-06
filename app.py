from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Producto, Movimiento
from auth import login_required, admin_required, empleado_o_admin_required
from ia import generar_recomendacion
from datetime import datetime, timedelta
from sqlalchemy.sql import func
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_segura")

# Configuración de sesión y base de datos
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = not app.debug
app.config['SESSION_PERMANENT'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///local.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configuración del correo
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["usuario_rol"] = user.rol
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Credenciales inválidas.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.")
    return redirect(url_for("login"))

@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email, rol="admin").first()
        if user:
            token = serializer.dumps(email, salt="recuperar-clave")
            enlace = url_for("restablecer_clave", token=token, _external=True)
            try:
                msg = Message("🔐 Restablecimiento de contraseña",
                              recipients=[email],
                              body=f"Para restablecer tu contraseña, haz clic en este enlace:\n\n{enlace}\n\nEste enlace expirará en 15 minutos.")
                mail.send(msg)
                flash("Se ha enviado un enlace de restablecimiento al correo.", "success")
            except Exception:
                flash("No se pudo enviar el correo. Verifica tu configuración.", "danger")
        else:
            flash("No se encontró una cuenta de administrador con ese correo.", "danger")
    return render_template("recuperar.html")

@app.route("/restablecer/<token>", methods=["GET", "POST"])
def restablecer_clave(token):
    try:
        email = serializer.loads(token, salt="recuperar-clave", max_age=900)
    except SignatureExpired:
        flash("El enlace ha expirado.", "danger")
        return redirect(url_for("login"))
    except BadSignature:
        flash("El enlace no es válido.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        nueva = request.form["password"]
        user = User.query.filter_by(email=email, rol="admin").first()
        if user:
            user.password = generate_password_hash(nueva)
            db.session.commit()
            flash("Contraseña actualizada correctamente. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("login"))
    return render_template("restablecer.html", email=email)

@app.route("/register", methods=["GET", "POST"])
@app.route("/crear_cuenta", methods=["GET", "POST"])
def register():
    admin_exists = User.query.filter_by(rol="admin").first() is not None

    if admin_exists:
        if "user_id" not in session or session.get("usuario_rol") != "admin":
            flash("Debe iniciar sesión como administrador para registrar usuarios.", "danger")
            return redirect(url_for("login"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        rol = request.form.get("rol", "empleado")

        if not admin_exists:
            rol = "admin"

        hashed = generate_password_hash(password)
        user = User(email=email, password=hashed, rol=rol)

        try:
            db.session.add(user)
            db.session.commit()
            flash("Usuario registrado con éxito.", "success")

            if not admin_exists:
                session["user_id"] = user.id
                session["usuario_rol"] = user.rol
                return redirect(url_for("dashboard"))

        except Exception:
            db.session.rollback()
            flash("Error: El correo ya está en uso.", "danger")
    return render_template("register.html")

@app.route("/dashboard")
@login_required
@admin_required
def dashboard():
    consulta = request.args.get("q", "").strip()
    if consulta:
        productos = Producto.query.filter(Producto.nombre.ilike(f"%{consulta}%")).all()
    else:
        productos = Producto.query.all()

    nombres = [p.nombre for p in productos]
    cantidades = [p.cantidad for p in productos]

    alertas = []
    recomendaciones = []

    for p in productos:
        if p.cantidad is not None and p.cantidad < 5:
            alertas.append({'nombre': p.nombre, 'cantidad': p.cantidad, 'tipo': 'bajo'})

        consumo_total = Movimiento.query.filter(
            Movimiento.producto_id == p.id,
            Movimiento.tipo == 'salida'
        ).with_entities(func.sum(Movimiento.cantidad)).scalar() or 0

        consumo_diario = consumo_total / 30
        recomendado = max(0, int(consumo_diario * 7 - p.cantidad))

        if recomendado > 0:
            texto = generar_recomendacion(p.nombre, p.cantidad, consumo_diario)
            recomendaciones.append({'nombre': p.nombre, 'sugerencia': texto})

    return render_template("dashboard.html",
        productos=productos,
        nombres=nombres,
        cantidades=cantidades,
        alertas=alertas,
        recomendaciones=recomendaciones
    )

@app.route("/agregar", methods=["GET", "POST"])
@login_required
def agregar_producto():
    if request.method == "POST":
        nombre = request.form["nombre"]
        cantidad = int(request.form["cantidad"])
        categoria = request.form.get("categoria")
        unidad = request.form.get("unidad")
        proveedor = request.form.get("proveedor")
        precio = float(request.form.get("precio", 0))

        nuevo = Producto(
            nombre=nombre,
            cantidad=cantidad,
            categoria=categoria,
            unidad=unidad,
            proveedor=proveedor,
            precio=precio
        )
        try:
            db.session.add(nuevo)
            db.session.commit()
            flash("Producto agregado exitosamente.")
        except Exception:
            db.session.rollback()
            flash("Ocurrió un error al agregar el producto.")
        return redirect(url_for("dashboard"))
    return render_template("agregar_producto.html")

@app.route("/prediccion")
@login_required
@admin_required
def prediccion():
    hoy = datetime.utcnow()
    hace_7_dias = hoy - timedelta(days=7)
    consulta = request.args.get("q", "").strip()

    if consulta:
        productos = Producto.query.filter(Producto.nombre.ilike(f"%{consulta}%")).all()
    else:
        productos = Producto.query.all()

    predicciones = []

    for producto in productos:
        total_salidas = Movimiento.query.filter(
            Movimiento.producto_id == producto.id,
            Movimiento.tipo == 'salida',
            Movimiento.fecha >= hace_7_dias
        ).with_entities(func.sum(Movimiento.cantidad)).scalar() or 0

        promedio_diario = round(total_salidas / 7, 2)
        predicciones.append({
            'nombre': producto.nombre,
            'promedio_diario': promedio_diario
        })

    return render_template("prediccion.html", predicciones=predicciones)

@app.route("/movimientos", methods=["GET", "POST"])
@login_required
@empleado_o_admin_required
def movimientos():
    consulta = request.args.get("q", "").strip()
    productos = Producto.query.all()

    if request.method == "POST":
        tipo = request.form["tipo"]
        producto_id = int(request.form["producto_id"])
        cantidad = int(request.form["cantidad"])

        producto = Producto.query.get(producto_id)
        if not producto:
            flash("Producto no encontrado.")
            return redirect(url_for("movimientos"))

        if tipo == "entrada":
            producto.cantidad += cantidad
        elif tipo == "salida":
            if producto.cantidad < cantidad:
                flash("Cantidad insuficiente en stock.")
                return redirect(url_for("movimientos"))
            producto.cantidad -= cantidad

        movimiento = Movimiento(
            producto_id=producto_id,
            tipo=tipo,
            cantidad=cantidad,
            fecha=datetime.utcnow()
        )

        try:
            db.session.add(movimiento)
            db.session.commit()
            flash("Movimiento registrado.")
        except Exception:
            db.session.rollback()
            flash("Error al registrar el movimiento.")
        return redirect(url_for("movimientos"))

    if consulta:
        movimientos = Movimiento.query.join(Producto).filter(
            Producto.nombre.ilike(f"%{consulta}%")
        ).order_by(Movimiento.fecha.desc()).limit(50).all()
    else:
        movimientos = Movimiento.query.order_by(Movimiento.fecha.desc()).limit(50).all()

    return render_template("movimientos.html", productos=productos, movimientos=movimientos)

@app.route("/usuarios", methods=["GET", "POST"])
@login_required
@admin_required
def usuarios():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        rol = request.form["rol"]
        hashed = generate_password_hash(password)
        nuevo = User(email=email, password=hashed, rol=rol)
        try:
            db.session.add(nuevo)
            db.session.commit()
            flash("Usuario creado exitosamente.")
        except Exception:
            db.session.rollback()
            flash("Error al crear el usuario.")
        return redirect(url_for("usuarios"))

    todos = User.query.all()
    return render_template("usuarios.html", usuarios=todos)

@app.route("/usuarios/promover/<int:id>", methods=["POST"])
@login_required
@admin_required
def promocionar_usuario(id):
    user = User.query.get_or_404(id)
    if user.rol != "admin":
        user.rol = "admin"
        db.session.commit()
        flash(f"{user.email} ahora es administrador.")
    else:
        flash(f"{user.email} ya es administrador.")
    return redirect(url_for("usuarios"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)







    




