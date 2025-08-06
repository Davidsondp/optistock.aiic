from functools import wraps
from flask import session, redirect, url_for, flash
from models import User

# Decorador general para verificar sesión activa
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))  # Cambio aquí
        return f(*args, **kwargs)
    return decorated_function

# Decorador para verificar si es usuario administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))  # Cambio aquí

        user = User.query.get(session["user_id"])
        if not user:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for("auth.login"))  # Cambio aquí

        if user.rol != "admin":
            flash("Acceso restringido solo para administradores.", "danger")
            return redirect(url_for("movimientos"))  # Cambia por "main.movimientos" si es blueprint

        return f(*args, **kwargs)
    return decorated_function

# Decorador para empleados o administradores (valida sesión y rol)
def empleado_o_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))  # Cambio aquí

        user = User.query.get(session["user_id"])
        if not user:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for("auth.login"))  # Cambio aquí

        if user.rol not in ("empleado", "admin"):
            flash("Acceso restringido solo para empleados o administradores.", "danger")
            return redirect(url_for("auth.login"))  # Cambio aquí

        return f(*args, **kwargs)
    return decorated_function


