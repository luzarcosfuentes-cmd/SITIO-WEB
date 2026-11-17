"""Mis Gastos - app web de control de gastos personales.
Flask + Python + SQLite.  Acceso: usuario "admin" / clave "123".
"""
import os
import sqlite3
from datetime import date
from functools import wraps

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "gastos.db")

app = Flask(__name__)
app.secret_key = "cambia-esta-clave-en-produccion"

USUARIO = "admin"
CLAVE = "123"


# ---------- Base de datos ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS gastos (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   fecha TEXT NOT NULL,
                   descripcion TEXT NOT NULL,
                   monto REAL NOT NULL
               )"""
        )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("usuario"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# ---------- Rutas ----------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("usuario"):
        return redirect(url_for("gastos"))
    if request.method == "POST":
        if (request.form.get("usuario") == USUARIO
                and request.form.get("clave") == CLAVE):
            session["usuario"] = USUARIO
            return redirect(url_for("gastos"))
        flash("Usuario o clave incorrectos.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/gastos", methods=["GET", "POST"])
@login_required
def gastos():
    db = get_db()
    if request.method == "POST":
        fecha = request.form.get("fecha", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        try:
            monto = float(request.form.get("monto", ""))
        except ValueError:
            monto = None
        if not fecha or not descripcion or monto is None or monto <= 0:
            flash("Completa fecha, descripción y un monto mayor a 0.", "error")
        else:
            db.execute(
                "INSERT INTO gastos (fecha, descripcion, monto) VALUES (?,?,?)",
                (fecha, descripcion, monto),
            )
            db.commit()
            flash("Gasto registrado.", "ok")
        return redirect(url_for("gastos"))

    lista = db.execute(
        "SELECT * FROM gastos ORDER BY fecha DESC, id DESC").fetchall()
    total = sum(r["monto"] for r in lista)
    return render_template("gastos.html", gastos=lista, total=total,
                           hoy=date.today().isoformat())


@app.route("/gastos/<int:gasto_id>/eliminar", methods=["POST"])
@login_required
def eliminar(gasto_id):
    db = get_db()
    db.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))
    db.commit()
    flash("Gasto eliminado.", "ok")
    return redirect(url_for("gastos"))


@app.route("/reporte")
@login_required
def reporte():
    db = get_db()
    desde = request.args.get("desde", "")
    hasta = request.args.get("hasta", "")
    sql, params = "SELECT * FROM gastos WHERE 1=1", []
    if desde:
        sql += " AND fecha >= ?"
        params.append(desde)
    if hasta:
        sql += " AND fecha <= ?"
        params.append(hasta)
    sql += " ORDER BY fecha ASC, id ASC"
    filas = db.execute(sql, params).fetchall()

    total = sum(r["monto"] for r in filas)
    cantidad = len(filas)
    promedio = total / cantidad if cantidad else 0
    mayor = max(filas, key=lambda r: r["monto"]) if filas else None

    por_mes = {}
    for r in filas:
        mes = r["fecha"][:7]
        por_mes[mes] = por_mes.get(mes, 0) + r["monto"]
    max_mes = max(por_mes.values()) if por_mes else 1

    return render_template("reporte.html", filas=filas, total=total,
                           cantidad=cantidad, promedio=promedio, mayor=mayor,
                           por_mes=por_mes, max_mes=max_mes,
                           desde=desde, hasta=hasta)


init_db()

if __name__ == "__main__":
    app.run(debug=True)
