import sqlite3
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response

app = Flask(__name__)
app.secret_key = 'clave_super_secreta_para_sesiones'
DATABASE = 'gastos.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        if usuario == 'admin' and clave == '123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas. Intenta de nuevo.', 'error')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        fecha = request.form['fecha']
        descripcion = request.form['descripcion']
        monto = float(request.form['monto'])
        conn.execute('INSERT INTO gastos (fecha, descripcion, monto) VALUES (?, ?, ?)',
                     (fecha, descripcion, monto))
        conn.commit()
        flash('¡Gasto registrado con éxito!', 'success')
        return redirect(url_for('dashboard'))

    gastos = conn.execute('SELECT * FROM gastos ORDER BY fecha DESC, id DESC').fetchall()
    total = sum(gasto['monto'] for gasto in gastos)
    conn.close()
    return render_template('dashboard.html', gastos=gastos, total=total)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM gastos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Gasto eliminado.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/reporte')
def reporte():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    gastos = conn.execute('SELECT * FROM gastos ORDER BY fecha DESC').fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Fecha', 'Descripción', 'Monto'])
    
    total = 0
    for g in gastos:
        writer.writerow([g['id'], g['fecha'], g['descripcion'], f"{g['monto']:.2f}"])
        total += g['monto']
    
    writer.writerow([])
    writer.writerow(['', '', 'TOTAL GENERAL', f"{total:.2f}"])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=reporte_gastos.csv"}
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
